# Expense Management System - Database Schema

## Overview

This document describes the database schema for the Expense Management System. The schema is designed to support user authentication, expense tracking, categorization, tagging, and budget management.

## Entity Relationship Diagram

The visual diagram is available in `database_schema.drawio` file. You can open it using:
- [draw.io](https://app.diagrams.net/) - Online
- VS Code with Draw.io Integration extension
- Draw.io Desktop application

## Tables

### 1. Users Table (`users`)

Stores user account information for authentication and expense ownership.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT | Unique user identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | User's username |
| email | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | User's email address |
| hashed_password | VARCHAR(255) | NOT NULL | Hashed password |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

### 2. Categories Table (`categories`)

Stores expense categories for organizing expenses.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT | Unique category identifier |
| name | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Category name |
| description | VARCHAR(200) | NULLABLE | Category description |
| icon | VARCHAR(50) | NULLABLE | Icon name or emoji |
| color | VARCHAR(20) | NULLABLE | Hex color code |

### 3. Expenses Table (`expenses`)

Main table for storing expense records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT | Unique expense identifier |
| user_id | INTEGER | FK → users.id, NOT NULL, INDEX | Owner user |
| category_id | INTEGER | FK → categories.id, NULLABLE, INDEX | Expense category |
| description | VARCHAR(200) | NOT NULL | Expense description |
| amount | DECIMAL(12,2) | NOT NULL | Expense amount |
| expense_date | DATE | NOT NULL | Date of expense |
| receipt_image | VARCHAR(255) | NULLABLE | Path to receipt image |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

### 4. Tags Table (`tags`)

Stores tags for labeling expenses.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT | Unique tag identifier |
| name | VARCHAR(30) | UNIQUE, NOT NULL, INDEX | Tag name |
| color | VARCHAR(20) | NULLABLE | Hex color code |

### 5. Expense Tags Table (`expense_tags`)

Junction table for many-to-many relationship between expenses and tags.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| expense_id | INTEGER | PK, FK → expenses.id | Expense reference |
| tag_id | INTEGER | PK, FK → tags.id | Tag reference |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Association timestamp |

### 6. Budgets Table (`budgets`)

Stores budget limits per category and period.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT | Unique budget identifier |
| user_id | INTEGER | FK → users.id, NOT NULL, INDEX | Owner user |
| category_id | INTEGER | FK → categories.id, NULLABLE, INDEX | Budget category |
| amount | DECIMAL(12,2) | NOT NULL | Budget amount limit |
| period | VARCHAR(20) | NOT NULL | Period: daily, weekly, monthly, yearly |
| start_date | DATE | NOT NULL | Budget start date |

## Relationships

### One-to-Many (1:N)

1. **Users → Expenses**: One user can have many expenses
2. **Users → Budgets**: One user can have many budgets
3. **Categories → Expenses**: One category can have many expenses
4. **Categories → Budgets**: One category can have many budgets

### Many-to-Many (N:N)

1. **Expenses ↔ Tags**: Expenses can have multiple tags, and tags can be associated with multiple expenses (via `expense_tags` junction table)

## Foreign Key Actions

| Relationship | ON DELETE |
|--------------|-----------|
| expenses.user_id → users.id | CASCADE |
| expenses.category_id → categories.id | SET NULL |
| budgets.user_id → users.id | CASCADE |
| budgets.category_id → categories.id | CASCADE |
| expense_tags.expense_id → expenses.id | CASCADE |
| expense_tags.tag_id → tags.id | CASCADE |

## Indexes

All primary keys are automatically indexed. Additional indexes are created on:

- `users.username` (UNIQUE)
- `users.email` (UNIQUE)
- `categories.name` (UNIQUE)
- `tags.name` (UNIQUE)
- `expenses.user_id`
- `expenses.category_id`
- `budgets.user_id`
- `budgets.category_id`

## Sample Categories

| Name | Icon | Color | Description |
|------|------|-------|-------------|
| Food & Dining | 🍔 | #FF5733 | Restaurants, groceries, cafes |
| Transportation | 🚗 | #3498DB | Fuel, taxi, public transport |
| Shopping | 🛒 | #9B59B6 | Clothes, electronics, etc. |
| Entertainment | 🎬 | #E74C3C | Movies, games, events |
| Bills & Utilities | 💡 | #2ECC71 | Electricity, water, internet |
| Health | 🏥 | #1ABC9C | Medical, pharmacy |
| Education | 📚 | #F39C12 | Books, courses, training |
| Other | 📌 | #95A5A6 | Miscellaneous expenses |

## Alembic Migrations

Database migrations are managed using Alembic. Available commands:

```bash
# Apply all migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "Migration description"

# View migration history
alembic history

# View current revision
alembic current
```
