from fastapi import APIRouter, Depends, Query 
from Models.model import Order, OrderCreated, OrderStatus
from sqlmodel import Session, select , func
from datetime import datetime

from dabbewale.database import get_session

router = APIRouter(
    prefix="/stats",
    tags=["stats"]
)

@router.get("/get_average_order_per_day")
async def get_average_order_per_day(
    date: datetime = Query(default=None, description="The day you want order data for"),
    session: Session = Depends(get_session),
):
    if date is None:
        date = datetime.now()
    # Count orders on that day
    count_query = (
        select(func.count(Order.id))
        .where(func.date(Order.createdAt) == date.date())
    )
    order_count = session.exec(count_query).one()
    # Optional: also return the orders for that day
    orders_query = (
        select(Order)
        .where(func.date(Order.createdAt) == date.date())
    )
    orders = session.exec(orders_query).all()
    return {
        "date": date.date().isoformat(),
        "order_count": order_count,
        "orders": orders,
    }
