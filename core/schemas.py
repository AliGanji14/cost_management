from pydantic import BaseModel, Field, field_serializer, field_validator


class BaseExpenseSchema(BaseModel):
    description: str = Field(
        ...,
        example="Internet purchase",
        description='Enter expense description (max 50 chars, alphabetic only)'
    )
    amount: float = Field(
        ...,
        gt=0,
        example=120000.50,
        description='Enter expense amount (must be > 0)',
    )

    @field_validator('description')
    def validate_name(cls, value):
        if len(value) > 50:
            raise ValueError('description most not exceed 50 characters')
        if not all(char.isalpha() or char.isspace() or char == '-' for char in value):
            raise ValueError(
                'Description must contain only letters, spaces, or hyphens')
        return value


class ExpenseCreateSchema(BaseExpenseSchema):
    pass


class ExpenseResponseSchema(BaseExpenseSchema):
    id: int = Field(..., description='Unique expense identifier')


class ExpenseUpdateSchema(BaseExpenseSchema):
    pass
