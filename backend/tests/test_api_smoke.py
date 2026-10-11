"""Smoke tests against the FastAPI app (requires MySQL with seed data)."""

import unittest

from fastapi.testclient import TestClient

from app.main import app


class ApiSmokeTestCase(unittest.TestCase):
    """Verify critical API flows respond successfully."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        login = cls.client.post(
            "/api/auth/login",
            json={"email": "admin@cemede.una.ac.cr", "password": "cemede2026"},
        )
        if login.status_code != 200:
            raise AssertionError(f"Login failed: {login.status_code} {login.text}")
        cls.token = login.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    def test_health(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_capacidad_publico_junquillal(self) -> None:
        response = self.client.get("/api/capacidad/publico/1")
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertIn("ccf", body)
        self.assertIn("ccr_final", body)
        self.assertIn("cce", body)
        self.assertGreater(body["ccf"], 0)

    def test_capacidad_ccf_ccr_cce(self) -> None:
        for suffix in ("ccf", "ccr", "cce"):
            response = self.client.get(f"/api/capacidad/{suffix}/1", headers=self.headers)
            self.assertEqual(response.status_code, 200, response.text)

    def test_ml_estado(self) -> None:
        response = self.client.get("/api/ml/estado/1", headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["playa_id"], 1)
        self.assertIn("registros_disponibles", body)

    def test_historico_visitacion_list(self) -> None:
        response = self.client.get("/api/historico/visitacion", headers=self.headers)
        self.assertIn(response.status_code, (200, 403), response.text)

    def test_dashboard_general(self) -> None:
        response = self.client.get("/api/dashboard", headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)

    def test_playas_list(self) -> None:
        response = self.client.get("/api/playas", headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertGreaterEqual(len(response.json()), 1)


if __name__ == "__main__":
    unittest.main()
