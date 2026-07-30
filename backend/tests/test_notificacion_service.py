"""Unit tests for notification business logic."""

from types import SimpleNamespace
from typing import Any, cast
from unittest import TestCase

from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Session

from app.models import Notificacion
from app.routers.notificaciones import mark_notificacion_as_read
from app.services.notificacion_service import (
    OCUPACION_CRITICA_TITLE,
    create_event_notifications,
    create_occupancy_notifications,
)


class FakeQuery:
    """Minimal SQLAlchemy query double."""

    def __init__(self, result: list[Any]) -> None:
        self.result = result

    def filter(self, *conditions: object) -> "FakeQuery":
        """Ignore query conditions in this controlled test double."""
        return self

    def all(self) -> list[Any]:
        """Return configured query rows."""
        return self.result

    def first(self) -> Any | None:
        """Return the first configured row."""
        return self.result[0] if self.result else None


class FakeSession:
    """Minimal SQLAlchemy session double."""

    def __init__(self, query_results: list[list[Any]]) -> None:
        self.query_results = query_results
        self.added: list[Notificacion] = []
        self.executed: list[Any] = []
        self.has_committed = False

    def query(self, *entities: object) -> FakeQuery:
        """Return the next configured query result."""
        return FakeQuery(self.query_results.pop(0))

    def add_all(self, instances: list[Notificacion]) -> None:
        """Capture notifications queued for persistence."""
        self.added.extend(instances)

    def execute(self, statement: object) -> None:
        """Capture SQL statements queued for execution."""
        self.executed.append(statement)

    def commit(self) -> None:
        """Record transaction commit."""
        self.has_committed = True


class NotificacionServiceTest(TestCase):
    """Notification service unit tests."""

    def test_creates_event_notification_for_each_active_user(self) -> None:
        """Create an event notification for every active user."""
        fake_db = FakeSession([[(1,), (2,)]])
        evento = SimpleNamespace(
            id=7,
            playa_id=1,
            tipo=SimpleNamespace(value="marea_alta"),
        )
        create_event_notifications(cast(Session, fake_db), evento, "Junquillal")
        self.assertEqual([1, 2], [item.usuario_id for item in fake_db.added])
        self.assertTrue(all(item.evento_id == 7 for item in fake_db.added))

    def test_does_not_create_normal_occupancy_notifications(self) -> None:
        """Skip notifications while occupancy remains normal."""
        fake_db = FakeSession([])
        create_occupancy_notifications(
            db=cast(Session, fake_db),
            playa_id=1,
            playa_nombre="Junquillal",
            estado="normal",
            porcentaje_ocupacion=25.0,
        )
        self.assertEqual([], fake_db.added)

    def test_uses_upsert_to_deduplicate_occupancy_notifications(self) -> None:
        """Use unique-key upsert semantics for concurrent critical alerts."""
        fake_db = FakeSession([[(1,), (2,)]])
        create_occupancy_notifications(
            db=cast(Session, fake_db),
            playa_id=1,
            playa_nombre="Junquillal",
            estado="critico",
            porcentaje_ocupacion=105.5,
        )
        self.assertEqual(1, len(fake_db.executed))
        statement = fake_db.executed[0]
        compiled = statement.compile(dialect=mysql.dialect())
        self.assertIn("ON DUPLICATE KEY UPDATE", str(compiled))
        self.assertIn("occupancy:1:1:critico", compiled.params.values())
        self.assertIn(OCUPACION_CRITICA_TITLE, compiled.params.values())

    def test_marking_notification_read_releases_deduplication_key(self) -> None:
        """Release the unique key so a future alert can be created."""
        notification = SimpleNamespace(id=9, leida=False, deduplication_key="occupancy:1:1:critico")
        fake_db = FakeSession([[notification]])
        current_user = SimpleNamespace(id=1)
        response = mark_notificacion_as_read(
            notificacion_id=notification.id,
            db=cast(Session, fake_db),
            current_user=current_user,
        )
        self.assertTrue(response.leida)
        self.assertIsNone(notification.deduplication_key)
        self.assertTrue(fake_db.has_committed)
