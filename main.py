from fastapi import FastAPI, status, Query, HTTPException, Body, Path
from fastapi.responses import JSONResponse


app = FastAPI()


expenses = [
    {"id": 1, "description": "Internet purchase", "amount": 250000.50},
    {"id": 2, "description": "Taxi fare", "amount": 85000.0},
    {"id": 3, "description": "Lunch purchase", "amount": 120000.75},
    {"id": 4, "description": "Mobile bill", "amount": 98000.0},
    {"id": 5, "description": "Book purchase", "amount": 175000.25},
    {"id": 6, "description": "Wallet top-up", "amount": 300000.0},
    {"id": 7, "description": "Parking fee", "amount": 40000.0}
]


@app.get('/expenses', status_code=status.HTTP_200_OK)
def get_expenses(q: str | None = Query(description='Search expenses by description',
                                       example='Internet',
                                       alias='search',
                                       max_length=50,
                                       default=None)):
    if q:
        results = [cost for cost in expenses if q.lower()
                   in cost['description'].lower()]
        if not results:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No cost found with description')
        return results
    return expenses


@app.post('/expenses', status_code=status.HTTP_201_CREATED)
def create_expense(description: str = Body(embed=True), amount: float = Body(embed=True)):
    last_id = max(expense['id'] for expense in expenses) if expenses else 0
    cost_obj = {'id': last_id+1, "description": description, "amount": amount}
    expenses.append(cost_obj)
    return cost_obj


@app.get('/expenses/{id}', status_code=status.HTTP_200_OK)
def get_expense(id: int = Path(description='the id of the cost in expenses')):
    for name in expenses:
        if name['id'] == id:
            return name
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='cost not found')
