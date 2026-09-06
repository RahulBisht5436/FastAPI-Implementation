from fastapi import APIRouter, Depends, Query 
from Models.model import Order, OrderCreated, OrderStatus
from sqlmodel import Session, select , func
from datetime import datetime

from dabbewale.database import get_session

router = APIRouter(
    prefix="/order",
    tags=["order"]
)


@router.post("/create", response_model=Order)
async def create_order(order: OrderCreated, session: Session = Depends(get_session)):
    db_order = Order(
        customer_name=order.customer_name,
        delivery_address=order.delivery_address,
        items=order.items,
        status=OrderStatus.PREPARING,
    )
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order


@router.get("/get_orders", response_model=list[Order])
async def get_orders(
    # Optional filters — omit from the URL to skip that filter
    status: OrderStatus = Query(default=None),
    created_date: datetime = Query(default=None),
    # Pagination: page starts at 1, limit caps how many rows per page
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    session: Session = Depends(get_session),
):
    # Base query — selects all columns from the order table
    query = select(Order)

    # Narrow results when optional query params are provided
    if status:
        query = query.where(Order.status == status)
     
    from datetime import date

    if created_date:
        query = query.where(
            func.date(Order.createdAt) == created_date.date()
        )
    # Skip earlier pages, then take only `limit` rows
    query = query.offset((page - 1) * limit).limit(limit)

    # Run the query and return matching orders as a list
    return session.exec(query).all()