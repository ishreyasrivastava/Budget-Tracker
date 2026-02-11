"""
Pydantic models for request/response validation.
These define the data structures used throughout the API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class ExpenseCategory(str, Enum):
    """Available expense categories."""
    FOOD = "Food"
    TRANSPORT = "Transport"
    ENTERTAINMENT = "Entertainment"
    BILLS = "Bills"
    SHOPPING = "Shopping"
    HEALTH = "Health"
    EDUCATION = "Education"
    OTHER = "Other"


# =============================================================================
# AUTH MODELS
# =============================================================================

class UserSignUp(BaseModel):
    """User registration request."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    full_name: Optional[str] = Field(None, description="User's full name")


class UserSignIn(BaseModel):
    """User login request."""
    email: str
    password: str


class UserResponse(BaseModel):
    """User data response."""
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: Optional[str] = None


class AuthResponse(BaseModel):
    """Authentication response with tokens."""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# =============================================================================
# EXPENSE MODELS
# =============================================================================

class ExpenseCreate(BaseModel):
    """Create a new expense."""
    amount: float = Field(..., gt=0, description="Expense amount (must be positive)")
    category: ExpenseCategory = Field(..., description="Expense category")
    description: Optional[str] = Field(None, max_length=500)
    date: date = Field(..., description="Date of the expense")
    
    @field_validator('amount')
    @classmethod
    def round_amount(cls, v):
        """Round amount to 2 decimal places."""
        return round(v, 2)


class ExpenseUpdate(BaseModel):
    """Update an existing expense."""
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[date] = None
    
    @field_validator('amount')
    @classmethod
    def round_amount(cls, v):
        if v is not None:
            return round(v, 2)
        return v


class ExpenseResponse(BaseModel):
    """Expense data response."""
    id: str
    user_id: str
    amount: float
    category: str
    description: Optional[str]
    date: str
    created_at: str


class ExpenseListResponse(BaseModel):
    """List of expenses with metadata."""
    expenses: List[ExpenseResponse]
    total: int
    total_amount: float


# =============================================================================
# BUDGET MODELS
# =============================================================================

class BudgetCreate(BaseModel):
    """Create or update a budget for a category."""
    category: ExpenseCategory = Field(..., description="Category for the budget")
    amount: float = Field(..., gt=0, description="Budget amount")
    month: str = Field(..., description="Month in YYYY-MM format")
    
    @field_validator('month')
    @classmethod
    def validate_month(cls, v):
        """Validate month format."""
        try:
            datetime.strptime(v, "%Y-%m")
        except ValueError:
            raise ValueError("Month must be in YYYY-MM format")
        return v
    
    @field_validator('amount')
    @classmethod
    def round_amount(cls, v):
        return round(v, 2)


class BudgetUpdate(BaseModel):
    """Update a budget."""
    amount: Optional[float] = Field(None, gt=0)
    
    @field_validator('amount')
    @classmethod
    def round_amount(cls, v):
        if v is not None:
            return round(v, 2)
        return v


class BudgetResponse(BaseModel):
    """Budget data response."""
    id: str
    user_id: str
    category: str
    amount: float
    month: str
    created_at: str
    spent: float = 0.0  # Calculated field
    remaining: float = 0.0  # Calculated field
    percentage_used: float = 0.0  # Calculated field


class BudgetListResponse(BaseModel):
    """List of budgets."""
    budgets: List[BudgetResponse]
    total_budget: float
    total_spent: float


# =============================================================================
# DASHBOARD MODELS
# =============================================================================

class CategoryBreakdown(BaseModel):
    """Spending breakdown by category."""
    category: str
    amount: float
    percentage: float
    budget: Optional[float] = None
    status: str = "ok"  # ok, warning, exceeded


class DashboardResponse(BaseModel):
    """Dashboard summary data."""
    total_spent_this_month: float
    total_budget_this_month: float
    remaining_budget: float
    budget_status: str  # ok, warning, exceeded
    category_breakdown: List[CategoryBreakdown]
    recent_expenses: List[ExpenseResponse]
    spending_trend: List[dict]  # Daily spending for charts
