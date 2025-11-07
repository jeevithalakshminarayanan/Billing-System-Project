from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    product_id = Column(String, unique=True, index=True)
    price = Column(Float)
    available_stock = Column(Integer)
    tax_percentage = Column(Float)

    bills = relationship("BillItem", back_populates="product")

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, index=True)
    total_amount = Column(Float)
    tax_amount = Column(Float)
    final_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("BillItem", back_populates="bill")

class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_price = Column(Float)
    tax_amount = Column(Float)

    bill = relationship("Bill", back_populates="items")
    product = relationship("Product", back_populates="bills")