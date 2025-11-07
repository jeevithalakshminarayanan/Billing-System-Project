from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    product_id: str
    price: float
    available_stock: int
    tax_percentage: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True

class BillItemBase(BaseModel):
    product_id: int
    quantity: int

class BillItemCreate(BillItemBase):
    pass

class BillItem(BillItemBase):
    id: int
    unit_price: float
    total_price: float
    tax_amount: float

    class Config:
        orm_mode = True

class BillBase(BaseModel):
    customer_email: str

class BillCreate(BillBase):
    items: List[BillItemCreate]

class Bill(BillBase):
    id: int
    total_amount: float
    tax_amount: float
    final_amount: float
    created_at: datetime
    items: List[BillItem]

    class Config:
        orm_mode = True