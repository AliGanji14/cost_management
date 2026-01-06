from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ==================== User Schemas ====================

class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        example="john_doe",
        description="Username (3-50 characters)"
    )
    email: str = Field(
        ...,
        max_length=100,
        example="john@example.com",
        description="User email address"
    )


class UserCreateSchema(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        example="securepassword123",
        description="User password (min 8 characters)"
    )


class UserResponseSchema(UserBase):
    id: int = Field(..., description="Unique user identifier")
    is_active: bool = Field(default=True, description="User active status")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


# ==================== Category Schemas ====================

class CategoryBase(BaseModel):
    name: str = Field(
        ...,
        max_length=50,
        example="Food & Dining",
        description="Category name"
    )
    description: Optional[str] = Field(
        None,
        max_length=200,
        example="Expenses related to food and dining",
        description="Category description"
    )
    icon: Optional[str] = Field(
        None,
        max_length=50,
        example="🍔",
        description="Category icon (emoji or icon name)"
    )
    color: Optional[str] = Field(
        None,
        max_length=20,
        example="#FF5733",
        description="Category color (hex code)"
    )


class CategoryCreateSchema(CategoryBase):
    pass


class CategoryResponseSchema(CategoryBase):
    id: int = Field(..., description="Unique category identifier")

    model_config = ConfigDict(from_attributes=True)


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)


# ==================== Tag Schemas ====================

class TagBase(BaseModel):
    name: str = Field(
        ...,
        max_length=30,
        example="urgent",
        description="Tag name"
    )
    color: Optional[str] = Field(
        None,
        max_length=20,
        example="#3498db",
        description="Tag color (hex code)"
    )


class TagCreateSchema(TagBase):
    pass


class TagResponseSchema(TagBase):
    id: int = Field(..., description="Unique tag identifier")

    model_config = ConfigDict(from_attributes=True)


class TagUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=30)
    color: Optional[str] = Field(None, max_length=20)


# ==================== Expense Schemas ====================

class BaseExpenseSchema(BaseModel):
    description: str = Field(
        ...,
        max_length=200,
        example="Internet purchase",
        description='Enter expense description (max 200 chars)'
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        example=120000.50,
        description='Enter expense amount (must be > 0)',
        decimal_places=2
    )

    @field_validator('description')
    def validate_description(cls, value):
        if len(value) > 200:
            raise ValueError('Description must not exceed 200 characters')
        return value


class ExpenseCreateSchema(BaseExpenseSchema):
    category_id: Optional[int] = Field(
        None,
        example=1,
        description="Category ID for the expense"
    )
    expense_date: date = Field(
        ...,
        example="2026-01-06",
        description="Date of the expense"
    )
    receipt_image: Optional[str] = Field(
        None,
        max_length=255,
        description="Path to receipt image"
    )
    tag_ids: Optional[List[int]] = Field(
        None,
        example=[1, 2],
        description="List of tag IDs to associate with expense"
    )


class ExpenseResponseSchema(BaseExpenseSchema):
    id: int = Field(..., description='Unique expense identifier')
    user_id: int = Field(..., description="Owner user ID")
    category_id: Optional[int] = Field(None, description="Category ID")
    expense_date: date = Field(..., description="Date of the expense")
    receipt_image: Optional[str] = Field(None, description="Path to receipt image")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    category: Optional[CategoryResponseSchema] = None
    tags: Optional[List[TagResponseSchema]] = None

    model_config = ConfigDict(from_attributes=True)


class ExpenseUpdateSchema(BaseModel):
    description: Optional[str] = Field(None, max_length=200)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category_id: Optional[int] = None
    expense_date: Optional[date] = None
    receipt_image: Optional[str] = Field(None, max_length=255)
    tag_ids: Optional[List[int]] = None


# ==================== Budget Schemas ====================

class BudgetBase(BaseModel):
    category_id: Optional[int] = Field(
        None,
        example=1,
        description="Category ID for the budget (null for overall budget)"
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        example=500000.00,
        description="Budget amount",
        decimal_places=2
    )
    period: str = Field(
        ...,
        max_length=20,
        example="monthly",
        description="Budget period (daily, weekly, monthly, yearly)"
    )
    start_date: date = Field(
        ...,
        example="2026-01-01",
        description="Budget start date"
    )

    @field_validator('period')
    def validate_period(cls, value):
        allowed_periods = ['daily', 'weekly', 'monthly', 'yearly']
        if value.lower() not in allowed_periods:
            raise ValueError(f"Period must be one of: {', '.join(allowed_periods)}")
        return value.lower()


class BudgetCreateSchema(BudgetBase):
    pass


class BudgetResponseSchema(BudgetBase):
    id: int = Field(..., description="Unique budget identifier")
    user_id: int = Field(..., description="Owner user ID")
    category: Optional[CategoryResponseSchema] = None

    model_config = ConfigDict(from_attributes=True)


class BudgetUpdateSchema(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    period: Optional[str] = Field(None, max_length=20)
    start_date: Optional[date] = None

    @field_validator('period')
    def validate_period(cls, value):
        if value is None:
            return value
        allowed_periods = ['daily', 'weekly', 'monthly', 'yearly']
        if value.lower() not in allowed_periods:
            raise ValueError(f"Period must be one of: {', '.join(allowed_periods)}")
        return value.lower()
