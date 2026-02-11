"""
Budget management routes.
Set and track budgets by category and month.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime
from ..models import (
    BudgetCreate, BudgetUpdate, BudgetResponse, 
    BudgetListResponse, ExpenseCategory
)
from ..database import supabase
from ..auth import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])


def calculate_spent_for_budget(user_id: str, category: str, month: str) -> float:
    """Calculate total spent for a category in a given month."""
    year, mon = month.split("-")
    month_start = f"{year}-{mon}-01"
    if int(mon) == 12:
        month_end = f"{int(year)+1}-01-01"
    else:
        month_end = f"{year}-{int(mon)+1:02d}-01"
    
    result = supabase.table("expenses") \
        .select("amount") \
        .eq("user_id", user_id) \
        .eq("category", category) \
        .gte("date", month_start) \
        .lt("date", month_end) \
        .execute()
    
    return sum(e["amount"] for e in result.data) if result.data else 0.0


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_budget(
    budget: BudgetCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create or update a budget for a category/month.
    If budget already exists for this category/month, it updates it.
    """
    try:
        # Check if budget exists for this category/month
        existing = supabase.table("budgets") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .eq("category", budget.category.value) \
            .eq("month", budget.month) \
            .execute()
        
        if existing.data:
            # Update existing budget
            result = supabase.table("budgets") \
                .update({"amount": budget.amount}) \
                .eq("id", existing.data[0]["id"]) \
                .execute()
            b = result.data[0]
        else:
            # Create new budget
            budget_data = {
                "user_id": current_user["id"],
                "category": budget.category.value,
                "amount": budget.amount,
                "month": budget.month
            }
            
            result = supabase.table("budgets").insert(budget_data).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create budget"
                )
            b = result.data[0]
        
        # Calculate spent amount
        spent = calculate_spent_for_budget(
            current_user["id"], 
            b["category"], 
            b["month"]
        )
        remaining = b["amount"] - spent
        percentage = (spent / b["amount"] * 100) if b["amount"] > 0 else 0
        
        return BudgetResponse(
            id=b["id"],
            user_id=b["user_id"],
            category=b["category"],
            amount=b["amount"],
            month=b["month"],
            created_at=b["created_at"],
            spent=round(spent, 2),
            remaining=round(remaining, 2),
            percentage_used=round(percentage, 1)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating budget: {str(e)}"
        )


@router.get("/", response_model=BudgetListResponse)
async def list_budgets(
    current_user: dict = Depends(get_current_user),
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM)"),
    category: Optional[ExpenseCategory] = Query(None)
):
    """
    List budgets for the authenticated user.
    """
    try:
        query = supabase.table("budgets") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .order("month", desc=True)
        
        if month:
            query = query.eq("month", month)
        if category:
            query = query.eq("category", category.value)
        
        result = query.execute()
        
        budgets = []
        total_budget = 0.0
        total_spent = 0.0
        
        for b in result.data:
            spent = calculate_spent_for_budget(
                current_user["id"],
                b["category"],
                b["month"]
            )
            remaining = b["amount"] - spent
            percentage = (spent / b["amount"] * 100) if b["amount"] > 0 else 0
            
            budgets.append(BudgetResponse(
                id=b["id"],
                user_id=b["user_id"],
                category=b["category"],
                amount=b["amount"],
                month=b["month"],
                created_at=b["created_at"],
                spent=round(spent, 2),
                remaining=round(remaining, 2),
                percentage_used=round(percentage, 1)
            ))
            
            # Only count current month for totals
            if not month or b["month"] == month:
                total_budget += b["amount"]
                total_spent += spent
        
        return BudgetListResponse(
            budgets=budgets,
            total_budget=round(total_budget, 2),
            total_spent=round(total_spent, 2)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching budgets: {str(e)}"
        )


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific budget by ID.
    """
    try:
        result = supabase.table("budgets") \
            .select("*") \
            .eq("id", budget_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        b = result.data
        spent = calculate_spent_for_budget(
            current_user["id"],
            b["category"],
            b["month"]
        )
        remaining = b["amount"] - spent
        percentage = (spent / b["amount"] * 100) if b["amount"] > 0 else 0
        
        return BudgetResponse(
            id=b["id"],
            user_id=b["user_id"],
            category=b["category"],
            amount=b["amount"],
            month=b["month"],
            created_at=b["created_at"],
            spent=round(spent, 2),
            remaining=round(remaining, 2),
            percentage_used=round(percentage, 1)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )


@router.patch("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    budget_update: BudgetUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a budget amount.
    """
    try:
        # Verify ownership
        existing = supabase.table("budgets") \
            .select("*") \
            .eq("id", budget_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        if budget_update.amount is not None:
            result = supabase.table("budgets") \
                .update({"amount": budget_update.amount}) \
                .eq("id", budget_id) \
                .execute()
            b = result.data[0]
        else:
            b = existing.data
        
        spent = calculate_spent_for_budget(
            current_user["id"],
            b["category"],
            b["month"]
        )
        remaining = b["amount"] - spent
        percentage = (spent / b["amount"] * 100) if b["amount"] > 0 else 0
        
        return BudgetResponse(
            id=b["id"],
            user_id=b["user_id"],
            category=b["category"],
            amount=b["amount"],
            month=b["month"],
            created_at=b["created_at"],
            spent=round(spent, 2),
            remaining=round(remaining, 2),
            percentage_used=round(percentage, 1)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating budget: {str(e)}"
        )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a budget.
    """
    try:
        existing = supabase.table("budgets") \
            .select("id") \
            .eq("id", budget_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        
        supabase.table("budgets") \
            .delete() \
            .eq("id", budget_id) \
            .execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting budget: {str(e)}"
        )
