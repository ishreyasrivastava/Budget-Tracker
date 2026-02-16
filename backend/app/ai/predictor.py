"""
AI-powered expense prediction engine.
Uses statistical analysis to forecast future spending patterns.

Techniques:
- Weighted Moving Average for short-term predictions
- Linear trend analysis for long-term trajectory
- Category-level granularity for actionable insights
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import math


def calculate_weighted_moving_average(
    values: List[float], 
    weights: Optional[List[float]] = None
) -> float:
    """
    Calculate weighted moving average.
    Recent months get higher weights by default.
    """
    if not values:
        return 0.0
    
    if weights is None:
        # Default: linearly increasing weights (recent = more important)
        n = len(values)
        weights = [(i + 1) for i in range(n)]
    
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(v * w for v, w in zip(values, weights))
    return round(weighted_sum / total_weight, 2)


def calculate_linear_trend(values: List[float]) -> Tuple[float, float]:
    """
    Simple linear regression to find trend.
    Returns (slope, intercept).
    """
    n = len(values)
    if n < 2:
        return (0.0, values[0] if values else 0.0)
    
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(values) / n
    
    numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return (0.0, y_mean)
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    return (round(slope, 2), round(intercept, 2))


def predict_next_month(
    monthly_totals: List[float],
    method: str = "hybrid"
) -> Dict:
    """
    Predict next month's spending.
    
    Methods:
    - 'wma': Weighted Moving Average only
    - 'trend': Linear trend only
    - 'hybrid': Average of both (default, most accurate)
    """
    if not monthly_totals:
        return {
            "predicted_amount": 0.0,
            "confidence": "low",
            "method": method,
            "trend": "insufficient_data"
        }
    
    n = len(monthly_totals)
    
    # WMA prediction
    wma_prediction = calculate_weighted_moving_average(monthly_totals[-6:])
    
    # Trend prediction
    slope, intercept = calculate_linear_trend(monthly_totals)
    trend_prediction = max(0, intercept + slope * n)
    
    # Hybrid
    if method == "wma":
        prediction = wma_prediction
    elif method == "trend":
        prediction = trend_prediction
    else:
        prediction = round((wma_prediction + trend_prediction) / 2, 2)
    
    # Confidence based on data points
    if n >= 6:
        confidence = "high"
    elif n >= 3:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Trend direction
    if slope > 0.5:
        trend = "increasing"
    elif slope < -0.5:
        trend = "decreasing"
    else:
        trend = "stable"
    
    # Percentage change from last month
    last_month = monthly_totals[-1] if monthly_totals else 0
    if last_month > 0:
        change_pct = round(((prediction - last_month) / last_month) * 100, 1)
    else:
        change_pct = 0.0
    
    return {
        "predicted_amount": round(prediction, 2),
        "confidence": confidence,
        "method": method,
        "trend": trend,
        "slope": slope,
        "change_from_last_month_pct": change_pct,
        "data_points_used": n
    }


def predict_by_category(
    category_monthly_data: Dict[str, List[float]]
) -> Dict[str, Dict]:
    """
    Predict next month's spending for each category.
    """
    predictions = {}
    total_predicted = 0.0
    
    for category, monthly_totals in category_monthly_data.items():
        pred = predict_next_month(monthly_totals)
        predictions[category] = pred
        total_predicted += pred["predicted_amount"]
    
    return {
        "category_predictions": predictions,
        "total_predicted": round(total_predicted, 2)
    }
