"""Unit tests for notification business logic."""

from types import SimpleNamespace
from typing import Any, cast
from unittest import TestCase

from sqlalchemy.orm import Session

from app.models import Notificacion
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


class FakeSession:
    """Minimal SQLAlchemy session double."""

    def __init__(self, query_results: list[list[Any]]) -> None:
        self.query_results = query_results
        self.added: list[Notificacion] = []

    def query(self, *entities: object) -> FakeQuery:
        """Return the next configured query result."""
        return FakeQuery(self.query_results.pop(0))

    def add_all(self, instances: list[Notificacion]) -> None:
        """Capture notifications queued for persistence."""
        self.added.extend(instances)


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

    def test_deduplicates_unread_occupancy_notifications(self) -> None:
        """Create critical alerts only for users without an unread alert."""
        fake_db = FakeSession([[(1,), (2,)], [(1,)]])
        create_occupancy_notifications(
            db=cast(Session, fake_db),
            playa_id=1,
            playa_nombre="Junquillal",
            estado="critico",
            porcentaje_ocupacion=105.5,
        )
        self.assertEqual(1, len(fake_db.added))
        self.assertEqual(2, fake_db.added[0].usuario_id)
        self.assertEqual(OCUPACION_CRITICA_TITLE, fake_db.added[0].titulo)
