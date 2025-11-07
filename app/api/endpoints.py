from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import models
from ..schemas import schemas

router = APIRouter()

@router.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@router.post("/bills/", response_model=schemas.Bill)
def create_bill(bill: schemas.BillCreate, db: Session = Depends(get_db)):
    # Create new bill
    db_bill = models.Bill(customer_email=bill.customer_email,
                         total_amount=0,
                         tax_amount=0,
                         final_amount=0)
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)

    total_amount = 0
    total_tax = 0

    # Add items to bill
    for item in bill.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.available_stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")

        item_total = product.price * item.quantity
        item_tax = item_total * (product.tax_percentage / 100)
        
        db_item = models.BillItem(
            bill_id=db_bill.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price,
            total_price=item_total,
            tax_amount=item_tax
        )
        
        # Update product stock
        product.available_stock -= item.quantity
        
        total_amount += item_total
        total_tax += item_tax
        
        db.add(db_item)

    # Update bill totals
    db_bill.total_amount = total_amount
    db_bill.tax_amount = total_tax
    db_bill.final_amount = total_amount + total_tax
    
    db.commit()
    db.refresh(db_bill)
    return db_bill

@router.get("/bills/", response_model=List[schemas.Bill])
def read_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bills = db.query(models.Bill).offset(skip).limit(limit).all()
    return bills

@router.get("/bills/{customer_email}", response_model=List[schemas.Bill])
def read_customer_bills(customer_email: str, db: Session = Depends(get_db)):
    bills = db.query(models.Bill).filter(models.Bill.customer_email == customer_email).all()
    return bills