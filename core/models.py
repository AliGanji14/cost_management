from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date,
    ForeignKey, Table, Numeric, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

try:
    from database import Base
except ImportError:
    from core.database import Base


# Association table for Many-to-Many relationship between Expenses and Tags
expense_tags = Table(
    'expense_tags',
    Base.metadata,
    Column('expense_id', Integer, ForeignKey('expenses.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)


class User(Base):
    """
    User model for authentication and expense ownership.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Category(Base):
    """
    Category model for expense categorization.
    """
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    icon = Column(String(50), nullable=True)  # Icon name or emoji
    color = Column(String(20), nullable=True)  # Hex color code

    # Relationships
    expenses = relationship("Expense", back_populates="category")
    budgets = relationship("Budget", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Expense(Base):
    """
    Expense model for storing expense records.
    """
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    receipt_image = Column(String(255), nullable=True)  # Path to receipt image
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
    tags = relationship("Tag", secondary=expense_tags, back_populates="expenses")

    def __repr__(self):
        return f"<Expense(id={self.id}, description='{self.description}', amount={self.amount})>"


class Tag(Base):
    """
    Tag model for labeling expenses.
    """
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False, index=True)
    color = Column(String(20), nullable=True)  # Hex color code

    # Relationships
    expenses = relationship("Expense", secondary=expense_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class Budget(Base):
    """
    Budget model for setting spending limits per category.
    """
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=True, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    period = Column(String(20), nullable=False)  # 'daily', 'weekly', 'monthly', 'yearly'
    start_date = Column(Date, nullable=False)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

    def __repr__(self):
        return f"<Budget(id={self.id}, amount={self.amount}, period='{self.period}')>"
