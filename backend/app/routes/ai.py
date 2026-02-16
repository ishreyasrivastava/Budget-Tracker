"""
AI-powered analytics routes.
Provides expense predictions, anomaly detection, and smart insights.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
from ..database import supabase
from ..auth import get_current_user
from ..ai.predictor import predict_next_month, predict_by_category
from ..ai.anomaly import detect_anomalies_zscore, detect_anomalies_iqr, get_spending_insights

router = APIRouter(prefix="/ai", tags=["AI Analytics"])


def get_monthly_data(user_id: str, months_back: int = 6) -> dict:
    """Fetch and organize expense data by month and category."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months_back * 31)
    
    result = supabase.table("expenses") \
        .select("*") \
        .eq("user_id", user_id) \
        .gte("date", start_date.strftime("%Y-%m-%d")) \
        .order("date", desc=False) \
        .execute()
    
    expenses = result.data or []
    
    # Organize by month
    monthly_totals = defaultdict(float)
    category_monthly = defaultdict(lambda: defaultdict(float))
    
    for exp in expenses:
        month_key = exp["date"][:7]  # YYYY-MM
        monthly_totals[month_key] += exp["amount"]
        category_monthly[exp["category"]][month_key] += exp["amount"]
    
    # Convert to sorted lists
    sorted_months = sorted(monthly_totals.keys())
    
    return {
        "expenses": expenses,
        "monthly_totals": monthly_totals,
        "category_monthly": category_monthly,
        "sorted_months": sorted_months
    }


@router.get("/predict")
async def predict_spending(
    current_user: dict = Depends(get_current_user),
    months_back: int = Query(6, ge=2, le=12, description="Months of history to analyze")
):
    """
    Predict next month's spending using AI.
    
    Analyzes historical spending patterns to forecast:
    - Total predicted spending
    - Per-category predictions
    - Trend direction (increasing/decreasing/stable)
    - Confidence level based on data availability
    """
    try:
        data = get_monthly_data(current_user["id"], months_back)
        
        if not data["sorted_months"]:
            return {
                "message": "Not enough data for predictions. Keep tracking expenses!",
                "predictions": None
            }
        
        # Overall prediction
        total_series = [data["monthly_totals"][m] for m in data["sorted_months"]]
        overall = predict_next_month(total_series)
        
        # Per-category prediction
        category_series = {}
        for category, monthly in data["category_monthly"].items():
            series = [monthly.get(m, 0) for m in data["sorted_months"]]
            category_series[category] = series
        
        category_preds = predict_by_category(category_series)
        
        # Next month label
        last_month = data["sorted_months"][-1]
        year, mon = map(int, last_month.split("-"))
        if mon == 12:
            next_month = f"{year + 1}-01"
        else:
            next_month = f"{year}-{mon + 1:02d}"
        
        return {
            "prediction_for": next_month,
            "overall": overall,
            "by_category": category_preds,
            "historical_months": data["sorted_months"],
            "historical_totals": {m: round(data["monthly_totals"][m], 2) for m in data["sorted_months"]}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating predictions: {str(e)}"
        )


@router.get("/anomalies")
async def detect_spending_anomalies(
    current_user: dict = Depends(get_current_user),
    months_back: int = Query(3, ge=1, le=12, description="Months to analyze"),
    method: str = Query("zscore", description="Detection method: zscore or iqr"),
    threshold: float = Query(2.0, ge=1.0, le=4.0, description="Sensitivity threshold")
):
    """
    Detect anomalous expenses using statistical analysis.
    
    Methods:
    - zscore: Z-score based (good for normally distributed data)
    - iqr: IQR based (more robust against extreme outliers)
    
    Lower threshold = more sensitive (flags more expenses).
    """
    try:
        data = get_monthly_data(current_user["id"], months_back)
        expenses = data["expenses"]
        
        if len(expenses) < 5:
            return {
                "message": "Need at least 5 expenses for anomaly detection.",
                "anomalies": [],
                "total_analyzed": len(expenses)
            }
        
        if method == "iqr":
            anomalies = detect_anomalies_iqr(expenses, multiplier=threshold)
        else:
            anomalies = detect_anomalies_zscore(expenses, threshold=threshold)
        
        return {
            "anomalies": anomalies,
            "total_analyzed": len(expenses),
            "anomalies_found": len(anomalies),
            "method": method,
            "threshold": threshold,
            "severity_breakdown": {
                "high": len([a for a in anomalies if a["severity"] == "high"]),
                "medium": len([a for a in anomalies if a["severity"] == "medium"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting anomalies: {str(e)}"
        )


@router.get("/insights")
async def get_smart_insights(
    current_user: dict = Depends(get_current_user),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format")
):
    """
    Get AI-powered spending insights and recommendations.
    
    Analyzes your spending patterns and provides:
    - Category dominance warnings
    - Budget utilization alerts
    - Spending frequency analysis
    - Transaction size patterns
    """
    try:
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        year, mon = month.split("-")
        month_start = f"{year}-{mon}-01"
        if int(mon) == 12:
            month_end = f"{int(year) + 1}-01-01"
        else:
            month_end = f"{year}-{int(mon) + 1:02d}-01"
        
        # Get expenses for the month
        expenses_result = supabase.table("expenses") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .gte("date", month_start) \
            .lt("date", month_end) \
            .execute()
        
        # Get budgets for the month
        budgets_result = supabase.table("budgets") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .eq("month", month) \
            .execute()
        
        expenses = expenses_result.data or []
        budgets = {b["category"]: b["amount"] for b in (budgets_result.data or [])}
        
        insights = get_spending_insights(expenses, budgets)
        
        # Add prediction insight if we have enough data
        data = get_monthly_data(current_user["id"], 6)
        if len(data["sorted_months"]) >= 2:
            total_series = [data["monthly_totals"][m] for m in data["sorted_months"]]
            pred = predict_next_month(total_series)
            
            if pred["trend"] == "increasing":
                insights.append({
                    "type": "warning",
                    "message": f"Your spending is trending upward "
                              f"({pred['change_from_last_month_pct']}% projected change). "
                              f"Next month prediction: ₹{pred['predicted_amount']}"
                })
            elif pred["trend"] == "decreasing":
                insights.append({
                    "type": "positive",
                    "message": f"Your spending is trending downward. Keep it up! "
                              f"Next month prediction: ₹{pred['predicted_amount']}"
                })
        
        return {
            "month": month,
            "insights": insights,
            "total_insights": len(insights)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating insights: {str(e)}"
        )
