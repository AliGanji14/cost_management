from fastapi import FastAPI, status, Query, HTTPException, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db, engine, Base
from models import User, Category, Expense, Tag, Budget
from schemas import (
    # User schemas
    UserCreateSchema, UserResponseSchema, UserUpdateSchema,
    # Category schemas
    CategoryCreateSchema, CategoryResponseSchema, CategoryUpdateSchema,
    # Tag schemas
    TagCreateSchema, TagResponseSchema, TagUpdateSchema,
    # Expense schemas
    ExpenseCreateSchema, ExpenseResponseSchema, ExpenseUpdateSchema,
    # Budget schemas
    BudgetCreateSchema, BudgetResponseSchema, BudgetUpdateSchema,
)

app = FastAPI(
    title="Expense Management API",
    description="API for managing personal expenses, categories, budgets, and tags",
    version="2.0.0"
)


# ==================== Category Endpoints ====================

@app.get('/categories', status_code=status.HTTP_200_OK, response_model=List[CategoryResponseSchema], tags=["Categories"])
def get_categories(
    q: Optional[str] = Query(None, description='Search categories by name', max_length=50),
    db: Session = Depends(get_db)
):
    """Get all categories or search by name."""
    query = db.query(Category)
    if q:
        query = query.filter(Category.name.ilike(f'%{q}%'))
    categories = query.all()
    if q and not categories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No category found')
    return categories


@app.post('/categories', status_code=status.HTTP_201_CREATED, response_model=CategoryResponseSchema, tags=["Categories"])
def create_category(category: CategoryCreateSchema, db: Session = Depends(get_db)):
    """Create a new category."""
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category name already exists')
    
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.get('/categories/{category_id}', status_code=status.HTTP_200_OK, response_model=CategoryResponseSchema, tags=["Categories"])
def get_category(category_id: int = Path(description='The ID of the category'), db: Session = Depends(get_db)):
    """Get a specific category by ID."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    return category


@app.put('/categories/{category_id}', status_code=status.HTTP_200_OK, response_model=CategoryResponseSchema, tags=["Categories"])
def update_category(
    category: CategoryUpdateSchema,
    category_id: int = Path(description='The ID of the category'),
    db: Session = Depends(get_db)
):
    """Update an existing category."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    
    update_data = category.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


@app.delete('/categories/{category_id}', status_code=status.HTTP_200_OK, tags=["Categories"])
def delete_category(category_id: int = Path(description='The ID of the category'), db: Session = Depends(get_db)):
    """Delete a category."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    
    db.delete(db_category)
    db.commit()
    return JSONResponse(content={'detail': 'Category removed successfully'})


# ==================== Tag Endpoints ====================

@app.get('/tags', status_code=status.HTTP_200_OK, response_model=List[TagResponseSchema], tags=["Tags"])
def get_tags(
    q: Optional[str] = Query(None, description='Search tags by name', max_length=30),
    db: Session = Depends(get_db)
):
    """Get all tags or search by name."""
    query = db.query(Tag)
    if q:
        query = query.filter(Tag.name.ilike(f'%{q}%'))
    tags = query.all()
    return tags


@app.post('/tags', status_code=status.HTTP_201_CREATED, response_model=TagResponseSchema, tags=["Tags"])
def create_tag(tag: TagCreateSchema, db: Session = Depends(get_db)):
    """Create a new tag."""
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Tag name already exists')
    
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.get('/tags/{tag_id}', status_code=status.HTTP_200_OK, response_model=TagResponseSchema, tags=["Tags"])
def get_tag(tag_id: int = Path(description='The ID of the tag'), db: Session = Depends(get_db)):
    """Get a specific tag by ID."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tag not found')
    return tag


@app.put('/tags/{tag_id}', status_code=status.HTTP_200_OK, response_model=TagResponseSchema, tags=["Tags"])
def update_tag(
    tag: TagUpdateSchema,
    tag_id: int = Path(description='The ID of the tag'),
    db: Session = Depends(get_db)
):
    """Update an existing tag."""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tag not found')
    
    update_data = tag.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tag, key, value)
    
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.delete('/tags/{tag_id}', status_code=status.HTTP_200_OK, tags=["Tags"])
def delete_tag(tag_id: int = Path(description='The ID of the tag'), db: Session = Depends(get_db)):
    """Delete a tag."""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tag not found')
    
    db.delete(db_tag)
    db.commit()
    return JSONResponse(content={'detail': 'Tag removed successfully'})


# ==================== Expense Endpoints ====================

@app.get('/expenses', status_code=status.HTTP_200_OK, response_model=List[ExpenseResponseSchema], tags=["Expenses"])
def get_expenses(
    q: Optional[str] = Query(None, description='Search expenses by description', alias='search', max_length=200),
    category_id: Optional[int] = Query(None, description='Filter by category ID'),
    user_id: Optional[int] = Query(None, description='Filter by user ID'),
    start_date: Optional[date] = Query(None, description='Filter expenses from this date'),
    end_date: Optional[date] = Query(None, description='Filter expenses until this date'),
    db: Session = Depends(get_db)
):
    """Get all expenses with optional filters."""
    query = db.query(Expense)
    
    if q:
        query = query.filter(Expense.description.ilike(f'%{q}%'))
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    if user_id:
        query = query.filter(Expense.user_id == user_id)
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    
    expenses = query.all()
    if q and not expenses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No expense found with that description')
    return expenses


@app.post('/expenses', status_code=status.HTTP_201_CREATED, response_model=ExpenseResponseSchema, tags=["Expenses"])
def create_expense(
    expense: ExpenseCreateSchema,
    user_id: int = Query(..., description='User ID for the expense'),
    db: Session = Depends(get_db)
):
    """Create a new expense."""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    # Verify category exists if provided
    if expense.category_id:
        category = db.query(Category).filter(Category.id == expense.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    
    # Extract tag_ids before creating expense
    tag_ids = expense.tag_ids or []
    expense_data = expense.model_dump(exclude={'tag_ids'})
    
    db_expense = Expense(**expense_data, user_id=user_id)
    
    # Add tags if provided
    if tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        if len(tags) != len(tag_ids):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='One or more tags not found')
        db_expense.tags = tags
    
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.get('/expenses/{expense_id}', status_code=status.HTTP_200_OK, response_model=ExpenseResponseSchema, tags=["Expenses"])
def get_expense(expense_id: int = Path(description='The ID of the expense'), db: Session = Depends(get_db)):
    """Get a specific expense by ID."""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Expense not found')
    return expense


@app.put('/expenses/{expense_id}', status_code=status.HTTP_200_OK, response_model=ExpenseResponseSchema, tags=["Expenses"])
def update_expense(
    expense: ExpenseUpdateSchema,
    expense_id: int = Path(description='The ID of the expense'),
    db: Session = Depends(get_db)
):
    """Update an existing expense."""
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Expense not found')
    
    update_data = expense.model_dump(exclude_unset=True, exclude={'tag_ids'})
    for key, value in update_data.items():
        setattr(db_expense, key, value)
    
    # Update tags if provided
    if expense.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(expense.tag_ids)).all()
        if len(tags) != len(expense.tag_ids):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='One or more tags not found')
        db_expense.tags = tags
    
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.delete('/expenses/{expense_id}', status_code=status.HTTP_200_OK, tags=["Expenses"])
def delete_expense(expense_id: int = Path(description='The ID of the expense'), db: Session = Depends(get_db)):
    """Delete an expense."""
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Expense not found')
    
    db.delete(db_expense)
    db.commit()
    return JSONResponse(content={'detail': 'Expense removed successfully'})


# ==================== Budget Endpoints ====================

@app.get('/budgets', status_code=status.HTTP_200_OK, response_model=List[BudgetResponseSchema], tags=["Budgets"])
def get_budgets(
    user_id: Optional[int] = Query(None, description='Filter by user ID'),
    category_id: Optional[int] = Query(None, description='Filter by category ID'),
    period: Optional[str] = Query(None, description='Filter by period'),
    db: Session = Depends(get_db)
):
    """Get all budgets with optional filters."""
    query = db.query(Budget)
    
    if user_id:
        query = query.filter(Budget.user_id == user_id)
    if category_id:
        query = query.filter(Budget.category_id == category_id)
    if period:
        query = query.filter(Budget.period == period.lower())
    
    return query.all()


@app.post('/budgets', status_code=status.HTTP_201_CREATED, response_model=BudgetResponseSchema, tags=["Budgets"])
def create_budget(
    budget: BudgetCreateSchema,
    user_id: int = Query(..., description='User ID for the budget'),
    db: Session = Depends(get_db)
):
    """Create a new budget."""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    # Verify category exists if provided
    if budget.category_id:
        category = db.query(Category).filter(Category.id == budget.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    
    db_budget = Budget(**budget.model_dump(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@app.get('/budgets/{budget_id}', status_code=status.HTTP_200_OK, response_model=BudgetResponseSchema, tags=["Budgets"])
def get_budget(budget_id: int = Path(description='The ID of the budget'), db: Session = Depends(get_db)):
    """Get a specific budget by ID."""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Budget not found')
    return budget


@app.put('/budgets/{budget_id}', status_code=status.HTTP_200_OK, response_model=BudgetResponseSchema, tags=["Budgets"])
def update_budget(
    budget: BudgetUpdateSchema,
    budget_id: int = Path(description='The ID of the budget'),
    db: Session = Depends(get_db)
):
    """Update an existing budget."""
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Budget not found')
    
    update_data = budget.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_budget, key, value)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget


@app.delete('/budgets/{budget_id}', status_code=status.HTTP_200_OK, tags=["Budgets"])
def delete_budget(budget_id: int = Path(description='The ID of the budget'), db: Session = Depends(get_db)):
    """Delete a budget."""
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Budget not found')
    
    db.delete(db_budget)
    db.commit()
    return JSONResponse(content={'detail': 'Budget removed successfully'})


# ==================== User Endpoints ====================

@app.get('/users', status_code=status.HTTP_200_OK, response_model=List[UserResponseSchema], tags=["Users"])
def get_users(
    q: Optional[str] = Query(None, description='Search users by username', max_length=50),
    db: Session = Depends(get_db)
):
    """Get all users or search by username."""
    query = db.query(User)
    if q:
        query = query.filter(User.username.ilike(f'%{q}%'))
    return query.all()


@app.post('/users', status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema, tags=["Users"])
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if username exists
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exists')
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already exists')
    
    # In production, password should be hashed
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password  # TODO: Hash password in production
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get('/users/{user_id}', status_code=status.HTTP_200_OK, response_model=UserResponseSchema, tags=["Users"])
def get_user(user_id: int = Path(description='The ID of the user'), db: Session = Depends(get_db)):
    """Get a specific user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user


@app.put('/users/{user_id}', status_code=status.HTTP_200_OK, response_model=UserResponseSchema, tags=["Users"])
def update_user(
    user: UserUpdateSchema,
    user_id: int = Path(description='The ID of the user'),
    db: Session = Depends(get_db)
):
    """Update an existing user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    update_data = user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete('/users/{user_id}', status_code=status.HTTP_200_OK, tags=["Users"])
def delete_user(user_id: int = Path(description='The ID of the user'), db: Session = Depends(get_db)):
    """Delete a user."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    db.delete(db_user)
    db.commit()
    return JSONResponse(content={'detail': 'User removed successfully'})


# ==================== Health Check ====================

@app.get('/health', status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}
