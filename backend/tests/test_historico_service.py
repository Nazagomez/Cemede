"""Unit tests for historical visitation helpers."""

from unittest import TestCase

from app.constants.ccf_field_params import CEMEDE_FIELD_CCF_PARAMS
from app.services.historico_service import _normalize_header, _visitantes_from_annual_count


class HistoricoServiceTestCase(TestCase):
    """Tests for historico_service utilities."""

    def test_normalize_header_strips_accents(self) -> None:
        """Header normalization should ignore accents."""
        self.assertEqual(_normalize_header("Año"), "anio")

    def test_visitantes_from_annual_count(self) -> None:
        """Annual visits should convert to daily average proxy."""
        self.assertEqual(_visitantes_from_annual_count(365), 1)
        self.assertEqual(_visitantes_from_annual_count(0), 0)

    def test_field_params_include_both_beaches(self) -> None:
        """CEMEDE field params should define both monitored beaches."""
        self.assertIn("junquillal", CEMEDE_FIELD_CCF_PARAMS)
        self.assertIn("playa_grande", CEMEDE_FIELD_CCF_PARAMS)
