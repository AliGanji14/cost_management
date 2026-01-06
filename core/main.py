from fastapi import FastAPI, status, Query, HTTPException, Path, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List
from sqlalchemy.orm import Session

from schemas import ExpenseCreateSchema, ExpenseResponseSchema, ExpenseUpdateSchema
from database import Base, engine, get_db, Expense


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Application startup')
    Base.metadata.create_all(engine)
    yield
    print('Application shutdown')

app = FastAPI(lifespan=lifespan)


@app.get('/expenses', status_code=status.HTTP_200_OK, response_model=List[ExpenseResponseSchema])
def get_expenses(q: str | None = Query(
        description='Search expenses by description',
        example='Internet',
        alias='search',
        max_length=50,
        default=None), db: Session = Depends(get_db)):
    query = db.query(Expense)
    if q:
        query = query.filter_by(description=q)
    results = query.all()
    return results


@app.post('/expenses', status_code=status.HTTP_201_CREATED, response_model=ExpenseResponseSchema)
def create_expense(request: ExpenseCreateSchema, db: Session = Depends(get_db)):
    new_expense = Expense(description=request.description,
                          amount=request.amount)
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


@app.get('/expenses/{id}', status_code=status.HTTP_200_OK, response_model=ExpenseResponseSchema)
def get_expense(id: int = Path(description='The ID of the cost in expenses'), db: Session = Depends(get_db)):
    expense = db.query(Expense).filter_by(id=id).one_or_none()
    if expense:
        return expense
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='cost not found')


@app.put('/expenses/{id}', status_code=status.HTTP_200_OK, response_model=ExpenseResponseSchema)
def update_expense(request: ExpenseUpdateSchema, id: int = Path(description='The ID of the cost in expenses'), db: Session = Depends(get_db)):
    expense = db.query(Expense).filter_by(id=id).one_or_none()
    if expense:
        expense.description = request.description
        expense.amount = request.amount
        db.commit()
        db.refresh(expense)
        return expense
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='cost not found')


@app.delete('/expenses/{id}', status_code=status.HTTP_200_OK)
def delete_expense(id: int = Path(description='The ID of the cost in expenses'), db: Session = Depends(get_db)):
    expense = db.query(Expense).filter_by(id=id).one_or_none()
    if expense:
        db.delete(expense)
        db.commit()
        return JSONResponse(content={'detail': 'cost removed successfuly'},)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='cost not found')
