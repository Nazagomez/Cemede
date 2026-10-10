"""Unit tests for ML metric helpers."""

from unittest import TestCase

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


class MlMetricsTestCase(TestCase):
    """Sanity checks for MAE/RMSE calculation used in training."""

    def test_mae_rmse_on_sample_vectors(self) -> None:
        """MAE and RMSE should be computed for simple vectors."""
        expected = np.array([100.0, 200.0, 300.0])
        predicted = np.array([110.0, 190.0, 280.0])
        mae = float(mean_absolute_error(expected, predicted))
        rmse = float(np.sqrt(mean_squared_error(expected, predicted)))
        self.assertAlmostEqual(mae, 13.3333, places=3)
        self.assertAlmostEqual(rmse, 14.1421, places=3)
