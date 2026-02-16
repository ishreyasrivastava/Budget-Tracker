"""
Tests for the AI prediction engine.
"""

import pytest
from app.ai.predictor import (
    calculate_weighted_moving_average,
    calculate_linear_trend,
    predict_next_month,
    predict_by_category
)


class TestWeightedMovingAverage:
    def test_empty_values(self):
        assert calculate_weighted_moving_average([]) == 0.0

    def test_single_value(self):
        result = calculate_weighted_moving_average([100.0])
        assert result == 100.0

    def test_equal_values(self):
        result = calculate_weighted_moving_average([50.0, 50.0, 50.0])
        assert result == 50.0

    def test_increasing_values(self):
        """Recent values should have more weight, so result > simple average."""
        result = calculate_weighted_moving_average([10.0, 20.0, 30.0])
        simple_avg = 20.0
        assert result > simple_avg  # Weighted toward recent (30)

    def test_custom_weights(self):
        result = calculate_weighted_moving_average([10.0, 20.0], [1, 1])
        assert result == 15.0  # Equal weights = simple average


class TestLinearTrend:
    def test_single_point(self):
        slope, intercept = calculate_linear_trend([42.0])
        assert slope == 0.0
        assert intercept == 42.0

    def test_perfect_increasing(self):
        slope, intercept = calculate_linear_trend([10.0, 20.0, 30.0])
        assert slope == 10.0
        assert intercept == 10.0

    def test_flat_trend(self):
        slope, intercept = calculate_linear_trend([50.0, 50.0, 50.0])
        assert slope == 0.0

    def test_decreasing(self):
        slope, _ = calculate_linear_trend([30.0, 20.0, 10.0])
        assert slope == -10.0


class TestPredictNextMonth:
    def test_empty_data(self):
        result = predict_next_month([])
        assert result["predicted_amount"] == 0.0
        assert result["confidence"] == "low"
        assert result["trend"] == "insufficient_data"

    def test_single_month(self):
        result = predict_next_month([1000.0])
        assert result["predicted_amount"] > 0
        assert result["confidence"] == "low"

    def test_stable_spending(self):
        result = predict_next_month([500.0, 500.0, 500.0, 500.0])
        assert abs(result["predicted_amount"] - 500.0) < 50  # Should be ~500

    def test_increasing_spending(self):
        result = predict_next_month([100.0, 200.0, 300.0, 400.0])
        assert result["predicted_amount"] > 400.0
        assert result["trend"] == "increasing"

    def test_decreasing_spending(self):
        result = predict_next_month([400.0, 300.0, 200.0, 100.0])
        assert result["trend"] == "decreasing"

    def test_high_confidence(self):
        result = predict_next_month([100, 200, 300, 400, 500, 600])
        assert result["confidence"] == "high"

    def test_medium_confidence(self):
        result = predict_next_month([100, 200, 300])
        assert result["confidence"] == "medium"

    def test_prediction_never_negative(self):
        result = predict_next_month([100.0, 50.0, 10.0, 1.0])
        assert result["predicted_amount"] >= 0


class TestPredictByCategory:
    def test_multiple_categories(self):
        data = {
            "Food": [500, 600, 550, 580],
            "Transport": [200, 180, 210, 190]
        }
        result = predict_by_category(data)
        assert "category_predictions" in result
        assert "total_predicted" in result
        assert "Food" in result["category_predictions"]
        assert "Transport" in result["category_predictions"]
        assert result["total_predicted"] > 0

    def test_empty_categories(self):
        result = predict_by_category({})
        assert result["total_predicted"] == 0.0
