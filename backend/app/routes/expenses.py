"""
Expense management routes.
Full CRUD operations for user expenses with filtering and pagination.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import date, datetime
from ..models import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, 
    ExpenseListResponse, ExpenseCategory
)
from ..database import supabase
from ..auth import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new expense for the authenticated user.
    """
    try:
        expense_data = {
            "user_id": current_user["id"],
            "amount": expense.amount,
            "category": expense.category.value,
            "description": expense.description,
            "date": expense.date.isoformat()
        }
        
        result = supabase.table("expenses").insert(expense_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create expense"
            )
        
        created = result.data[0]
        return ExpenseResponse(
            id=created["id"],
            user_id=created["user_id"],
            amount=created["amount"],
            category=created["category"],
            description=created.get("description"),
            date=created["date"],
            created_at=created["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating expense: {str(e)}"
        )


@router.get("/", response_model=ExpenseListResponse)
async def list_expenses(
    current_user: dict = Depends(get_current_user),
    category: Optional[ExpenseCategory] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List expenses for the authenticated user with optional filters.
    """
    try:
        query = supabase.table("expenses") \
            .select("*") \
            .eq("user_id", current_user["id"]) \
            .order("date", desc=True)
        
        # Apply filters
        if category:
            query = query.eq("category", category.value)
        
        if month:
            # Filter by month (YYYY-MM)
            year, mon = month.split("-")
            month_start = f"{year}-{mon}-01"
            # Calculate month end
            if int(mon) == 12:
                month_end = f"{int(year)+1}-01-01"
            else:
                month_end = f"{year}-{int(mon)+1:02d}-01"
            query = query.gte("date", month_start).lt("date", month_end)
        else:
            if start_date:
                query = query.gte("date", start_date.isoformat())
            if end_date:
                query = query.lte("date", end_date.isoformat())
        
        # Get total count first
        count_result = supabase.table("expenses") \
            .select("*", count="exact") \
            .eq("user_id", current_user["id"])
        
        if category:
            count_result = count_result.eq("category", category.value)
        
        count_data = count_result.execute()
        total = count_data.count or 0
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        
        expenses = [
            ExpenseResponse(
                id=e["id"],
                user_id=e["user_id"],
                amount=e["amount"],
                category=e["category"],
                description=e.get("description"),
                date=e["date"],
                created_at=e["created_at"]
            )
            for e in result.data
        ]
        
        total_amount = sum(e.amount for e in expenses)
        
        return ExpenseListResponse(
            expenses=expenses,
            total=total,
            total_amount=total_amount
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching expenses: {str(e)}"
        )


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific expense by ID.
    """
    try:
        result = supabase.table("expenses") \
            .select("*") \
            .eq("id", expense_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        e = result.data
        return ExpenseResponse(
            id=e["id"],
            user_id=e["user_id"],
            amount=e["amount"],
            category=e["category"],
            description=e.get("description"),
            date=e["date"],
            created_at=e["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )


@router.patch("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    expense_update: ExpenseUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing expense.
    """
    try:
        # First verify the expense belongs to the user
        existing = supabase.table("expenses") \
            .select("*") \
            .eq("id", expense_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        # Build update data
        update_data = {}
        if expense_update.amount is not None:
            update_data["amount"] = expense_update.amount
        if expense_update.category is not None:
            update_data["category"] = expense_update.category.value
        if expense_update.description is not None:
            update_data["description"] = expense_update.description
        if expense_update.date is not None:
            update_data["date"] = expense_update.date.isoformat()
        
        if not update_data:
            # Nothing to update, return existing
            e = existing.data
            return ExpenseResponse(
                id=e["id"],
                user_id=e["user_id"],
                amount=e["amount"],
                category=e["category"],
                description=e.get("description"),
                date=e["date"],
                created_at=e["created_at"]
            )
        
        result = supabase.table("expenses") \
            .update(update_data) \
            .eq("id", expense_id) \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update expense"
            )
        
        e = result.data[0]
        return ExpenseResponse(
            id=e["id"],
            user_id=e["user_id"],
            amount=e["amount"],
            category=e["category"],
            description=e.get("description"),
            date=e["date"],
            created_at=e["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating expense: {str(e)}"
        )


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an expense.
    """
    try:
        # Verify ownership first
        existing = supabase.table("expenses") \
            .select("id") \
            .eq("id", expense_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        supabase.table("expenses") \
            .delete() \
            .eq("id", expense_id) \
            .execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting expense: {str(e)}"
        )
