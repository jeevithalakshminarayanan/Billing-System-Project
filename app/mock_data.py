from typing import Dict, List
from datetime import datetime

# Mock database for products
products_db: Dict[str, dict] = {
    "LP001": {
        "name": "Laptop",
        "product_id": "LP001",
        "price": 45000,
        "available_stock": 10,
        "tax_percentage": 18
    },
    "MS001": {
        "name": "Mouse",
        "product_id": "MS001",
        "price": 500,
        "available_stock": 20,
        "tax_percentage": 12
    },
    "KB001": {
        "name": "Keyboard",
        "product_id": "KB001",
        "price": 1000,
        "available_stock": 15,
        "tax_percentage": 12
    }
}

# Mock database for bills
bills_db: List[dict] = []

class MockDB:
    @staticmethod
    def get_all_products():
        return list(products_db.values())
    
    @staticmethod
    def get_product(product_id: str):
        return products_db.get(product_id)
    
    @staticmethod
    def add_product(product_data: dict):
        products_db[product_data["product_id"]] = product_data
        return product_data
    
    @staticmethod
    def update_stock(product_id: str, quantity: int):
        if product_id in products_db:
            products_db[product_id]["available_stock"] -= quantity
            return True
        return False
    
    @staticmethod
    def create_bill(bill_data: dict):
        bill_data["id"] = len(bills_db) + 1
        bill_data["created_at"] = datetime.now().isoformat()
        bills_db.append(bill_data)
        return bill_data
    
    @staticmethod
    def get_customer_bills(email: str):
        return [bill for bill in bills_db if bill["customer_email"] == email]