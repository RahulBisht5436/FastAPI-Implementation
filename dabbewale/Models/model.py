from enum import Enum
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel , Field


class OrderStatus(str,Enum):
    PREPARING= "preparing" 
    PICKED_UP=  "picked_up"
    IN_TRANSIT= "in_transit"
    DELIVERED= "delivered"
    
    
#order class for creating order table in database

class Order(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str
    delivery_address: str
    items: str
    status: OrderStatus
    createdAt: datetime = Field(default_factory=datetime.now)
    updateat: datetime = Field(default_factory=datetime.now)
    
#schema for creating a new order 

class OrderCreated(SQLModel):
    customer_name: str = Field(..., description="The name of the customer")
    delivery_address: str = Field(..., description="The delivery address")
    items: str = Field(..., description="The items in the order")

# here above the ... means field is required and can have null value 


class OrderUpdated(SQLModel):
    status: OrderStatus = Field(..., description="The status of the order")
    deivery_address: Optional[str] = Field(None, description="The address of the customer")
    

class StatusLog(SQLModel):
    order_id: int = Field(..., description="The id of the order")
    old_status: OrderStatus = Field(..., description="The old status of the order")
    new_status: OrderStatus = Field(..., description="The new status of the order")
    createdAt: datetime = Field(default_factory=datetime.now)