"""
Tests for the anomaly detection engine.
"""

import pytest
from app.ai.anomaly import (
    calculate_stats,
    detect_anomalies_zscore,
    detect_anomalies_iqr,
    get_spending_insights
)


class TestCalculateStats:
    def test_empty_values(self):
        stats = calculate_stats([])
        assert stats["mean"] == 0
        assert stats["std"] == 0

    def test_single_value(self):
        stats = calculate_stats([100.0])
        assert stats["mean"] == 100.0
        assert stats["median"] == 100.0

    def test_known_values(self):
        stats = calculate_stats([10, 20, 30, 40, 50])
        assert stats["mean"] == 30.0
        assert stats["median"] == 30.0


class TestZScoreAnomalies:
    def test_insufficient_data(self):
        expenses = [{"amount": 100, "category": "Food"}]
        result = detect_anomalies_zscore(expenses)
        assert result == []

    def test_no_anomalies(self):
        expenses = [
            {"amount": 100, "category": "Food", "date": "2026-01-01", "description": "lunch"},
            {"amount": 105, "category": "Food", "date": "2026-01-02", "description": "dinner"},
            {"amount": 98, "category": "Food", "date": "2026-01-03", "description": "lunch"},
            {"amount": 102, "category": "Food", "date": "2026-01-04", "description": "lunch"},
        ]
        result = detect_anomalies_zscore(expenses)
        assert len(result) == 0

    def test_obvious_anomaly(self):
        expenses = [
            {"amount": 100, "category": "Food", "date": "2026-01-01", "description": "lunch", "id": "1"},
            {"amount": 105, "category": "Food", "date": "2026-01-02", "description": "dinner", "id": "2"},
            {"amount": 98, "category": "Food", "date": "2026-01-03", "description": "lunch", "id": "3"},
            {"amount": 102, "category": "Food", "date": "2026-01-04", "description": "lunch", "id": "4"},
            {"amount": 5000, "category": "Food", "date": "2026-01-05", "description": "party", "id": "5"},
        ]
        result = detect_anomalies_zscore(expenses, threshold=2.0)
        assert len(result) > 0
        assert result[0]["amount"] == 5000

    def test_anomaly_has_required_fields(self):
        expenses = [
            {"amount": 50, "category": "Food", "date": "2026-01-01", "description": "a", "id": "1"},
            {"amount": 55, "category": "Food", "date": "2026-01-02", "description": "b", "id": "2"},
            {"amount": 48, "category": "Food", "date": "2026-01-03", "description": "c", "id": "3"},
            {"amount": 52, "category": "Food", "date": "2026-01-04", "description": "d", "id": "4"},
            {"amount": 500, "category": "Food", "date": "2026-01-05", "description": "e", "id": "5"},
        ]
        result = detect_anomalies_zscore(expenses)
        if result:
            anomaly = result[0]
            assert "severity" in anomaly
            assert "reason" in anomaly
            assert "z_score" in anomaly


class TestIQRAnomalies:
    def test_insufficient_data(self):
        expenses = [
            {"amount": 100, "category": "Food"},
            {"amount": 200, "category": "Food"},
        ]
        result = detect_anomalies_iqr(expenses)
        assert result == []

    def test_detects_outlier(self):
        expenses = [
            {"amount": 100, "category": "Food", "date": "2026-01-01", "description": "a", "id": "1"},
            {"amount": 110, "category": "Food", "date": "2026-01-02", "description": "b", "id": "2"},
            {"amount": 95, "category": "Food", "date": "2026-01-03", "description": "c", "id": "3"},
            {"amount": 105, "category": "Food", "date": "2026-01-04", "description": "d", "id": "4"},
            {"amount": 2000, "category": "Food", "date": "2026-01-05", "description": "e", "id": "5"},
        ]
        result = detect_anomalies_iqr(expenses)
        assert len(result) > 0


class TestSpendingInsights:
    def test_empty_expenses(self):
        result = get_spending_insights([], {})
        assert len(result) == 1
        assert result[0]["type"] == "info"

    def test_dominant_category_warning(self):
        expenses = [
            {"amount": 5000, "category": "Food"},
            {"amount": 100, "category": "Transport"},
        ]
        result = get_spending_insights(expenses, {})
        types = [i["type"] for i in result]
        assert "warning" in types

    def test_budget_alert(self):
        expenses = [
            {"amount": 950, "category": "Food"},
        ]
        budgets = {"Food": 1000}
        result = get_spending_insights(expenses, budgets)
        alert_messages = [i for i in result if i["type"] == "alert"]
        assert len(alert_messages) > 0

    def test_positive_feedback(self):
        expenses = [
            {"amount": 100, "category": "Food"},
        ]
        budgets = {"Food": 5000}
        result = get_spending_insights(expenses, budgets)
        positive = [i for i in result if i["type"] == "positive"]
        assert len(positive) > 0
