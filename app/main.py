from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os


app = FastAPI(title="Billing System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# --- Provide mock API routes under /api to avoid DB dependency for local testing ---
from fastapi import APIRouter
api_router = APIRouter()


@api_router.get('/products/')
async def api_get_products():
    return mock_db.get_all_products()


@api_router.get('/products/{product_id}')
async def api_get_product(product_id: str):
    product = mock_db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return product


@api_router.post('/bills/')
async def api_create_bill(payload: dict):
    # delegate to mock_create_bill logic
    return await mock_create_bill(payload)


@api_router.get('/bills/{customer_email}')
async def api_get_customer_bills(customer_email: str):
    return mock_db.get_customer_bills(customer_email)

# Include mock API router first so it takes precedence over DB-backed routes
app.include_router(api_router, prefix='/api')

# --- Mock endpoints (in-memory) for local testing without a DB ---
from .mock_data import MockDB
from fastapi import HTTPException

# Initialize mock DB instance
mock_db = MockDB()


@app.get('/products')
async def mock_get_products():
    return mock_db.get_all_products()


@app.get('/products/{product_id}')
async def mock_get_product(product_id: str):
    product = mock_db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return product


@app.post('/bills')
async def mock_create_bill(payload: dict):
    # payload expected to contain customer_email, items, denominations
    try:
        customer_email = payload['customer_email']
        items = payload['items']
        denominations = payload.get('denominations', {})
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid payload')

    # perform same calculations as mock_data logic
    total_amount = 0
    tax_amount = 0
    bill_items = []

    for item in items:
        pid = item.get('product_id')
        qty = int(item.get('quantity', 0))
        product = mock_db.get_product(pid)
        if not product:
            raise HTTPException(status_code=404, detail=f'Product {pid} not found')
        if qty > product['available_stock']:
            raise HTTPException(status_code=400, detail=f'Insufficient stock for {product["name"]}')

        item_base = product['price'] * qty
        item_tax = (item_base * product['tax_percentage']) / 100
        bill_items.append({
            'product_id': pid,
            'name': product['name'],
            'quantity': qty,
            'unit_price': product['price'],
            'tax_percentage': product['tax_percentage'],
            'tax_amount': item_tax,
            'total': item_base + item_tax
        })

        total_amount += item_base
        tax_amount += item_tax
        mock_db.update_stock(pid, qty)

    final_amount = total_amount + tax_amount
    total_paid = sum(int(denom) * count for denom, count in denominations.items()) if denominations else 0
    if total_paid < final_amount:
        raise HTTPException(status_code=400, detail='Insufficient payment amount')

    bill = {
        'customer_email': customer_email,
        'items': bill_items,
        'total_amount': total_amount,
        'tax_amount': tax_amount,
        'final_amount': final_amount,
        'denominations': denominations,
        'change_amount': total_paid - final_amount
    }

    return mock_db.create_bill(bill)


@app.get('/bills/customer/{email}')
async def mock_get_customer_bills(email: str):
    return mock_db.get_customer_bills(email)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/bill")
async def bill_page(request: Request):
    return templates.TemplateResponse("bill.html", {"request": request})