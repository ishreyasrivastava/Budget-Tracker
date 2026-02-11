"""
Dashboard routes for aggregated views and analytics.
Provides summary data for the budget tracker dashboard.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
from ..models import (
    DashboardResponse, CategoryBreakdown, ExpenseResponse, ExpenseCategory
)
from ..database import supabase
from ..auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format (defaults to current)")
):
    """
    Get dashboard summary with spending breakdown, budget status, and trends.
    """
    try:
        # Default to current month
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        year, mon = month.split("-")
        month_start = f"{year}-{mon}-01"
        if int(mon) == 12:
            month_end = f"{int(year)+1}-01-01"
        else:
            month_end = f"{year}-{int(mon)+1:02d}-01"
        
        # Get all expenses for the month
        expenses_result = supabase.table("expenses") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .gte("date", month_start) \
            .lt("date", month_end) \
            .order("date", desc=True) \
            .execute()
        
        expenses = expenses_result.data or []
        
        # Get all budgets for the month
        budgets_result = supabase.table("budgets") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .eq("month", month) \
            .execute()
        
        budgets = {b["category"]: b["amount"] for b in (budgets_result.data or [])}
        
        # Calculate spending by category
        category_spending = defaultdict(float)
        for expense in expenses:
            category_spending[expense["category"]] += expense["amount"]
        
        total_spent = sum(category_spending.values())
        total_budget = sum(budgets.values())
        
        # Build category breakdown
        category_breakdown = []
        all_categories = set(category_spending.keys()) | set(budgets.keys())
        
        for category in all_categories:
            spent = category_spending.get(category, 0)
            budget = budgets.get(category)
            
            # Determine status
            if budget:
                percentage = (spent / budget * 100) if budget > 0 else 0
                if percentage >= 100:
                    cat_status = "exceeded"
                elif percentage >= 80:
                    cat_status = "warning"
                else:
                    cat_status = "ok"
            else:
                percentage = 0
                cat_status = "no_budget"
            
            category_breakdown.append(CategoryBreakdown(
                category=category,
                amount=round(spent, 2),
                percentage=round(percentage, 1) if budget else round((spent / total_spent * 100) if total_spent > 0 else 0, 1),
                budget=budget,
                status=cat_status
            ))
        
        # Sort by amount spent (descending)
        category_breakdown.sort(key=lambda x: x.amount, reverse=True)
        
        # Determine overall budget status
        if total_budget > 0:
            overall_percentage = (total_spent / total_budget * 100)
            if overall_percentage >= 100:
                budget_status = "exceeded"
            elif overall_percentage >= 80:
                budget_status = "warning"
            else:
                budget_status = "ok"
        else:
            budget_status = "no_budget"
        
        # Get recent expenses (last 5)
        recent_expenses = [
            ExpenseResponse(
                id=e["id"],
                user_id=e["user_id"],
                amount=e["amount"],
                category=e["category"],
                description=e.get("description"),
                date=e["date"],
                created_at=e["created_at"]
            )
            for e in expenses[:5]
        ]
        
        # Calculate daily spending trend for charts
        daily_spending = defaultdict(float)
        for expense in expenses:
            daily_spending[expense["date"]] += expense["amount"]
        
        # Fill in missing days with 0
        spending_trend = []
        current_date = datetime.strptime(month_start, "%Y-%m-%d")
        end_date = min(datetime.strptime(month_end, "%Y-%m-%d"), datetime.now())
        
        while current_date < end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            spending_trend.append({
                "date": date_str,
                "amount": round(daily_spending.get(date_str, 0), 2)
            })
            current_date += timedelta(days=1)
        
        return DashboardResponse(
            total_spent_this_month=round(total_spent, 2),
            total_budget_this_month=round(total_budget, 2),
            remaining_budget=round(total_budget - total_spent, 2),
            budget_status=budget_status,
            category_breakdown=category_breakdown,
            recent_expenses=recent_expenses,
            spending_trend=spending_trend
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard: {str(e)}"
        )


@router.get("/alerts")
async def get_budget_alerts(
    current_user: dict = Depends(get_current_user)
):
    """
    Get budget alerts for categories that are near or over budget.
    Returns alerts for current month.
    """
    try:
        month = datetime.now().strftime("%Y-%m")
        year, mon = month.split("-")
        month_start = f"{year}-{mon}-01"
        if int(mon) == 12:
            month_end = f"{int(year)+1}-01-01"
        else:
            month_end = f"{year}-{int(mon)+1:02d}-01"
        
        # Get budgets
        budgets_result = supabase.table("budgets") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .eq("month", month) \
            .execute()
        
        alerts = []
        
        for budget in (budgets_result.data or []):
            # Get spent for this category
            expenses_result = supabase.table("expenses") \
                .select("amount") \
                .eq("user_id", current_user["id"]) \
                .eq("category", budget["category"]) \
                .gte("date", month_start) \
                .lt("date", month_end) \
                .execute()
            
            spent = sum(e["amount"] for e in (expenses_result.data or []))
            percentage = (spent / budget["amount"] * 100) if budget["amount"] > 0 else 0
            
            if percentage >= 100:
                alerts.append({
                    "category": budget["category"],
                    "type": "exceeded",
                    "message": f"You've exceeded your {budget['category']} budget!",
                    "spent": round(spent, 2),
                    "budget": budget["amount"],
                    "percentage": round(percentage, 1),
                    "over_by": round(spent - budget["amount"], 2)
                })
            elif percentage >= 80:
                alerts.append({
                    "category": budget["category"],
                    "type": "warning",
                    "message": f"You're approaching your {budget['category']} budget limit",
                    "spent": round(spent, 2),
                    "budget": budget["amount"],
                    "percentage": round(percentage, 1),
                    "remaining": round(budget["amount"] - spent, 2)
                })
        
        # Sort by percentage (highest first)
        alerts.sort(key=lambda x: x["percentage"], reverse=True)
        
        return {"alerts": alerts, "count": len(alerts)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching alerts: {str(e)}"
        )
