from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import engine, Base
from .api import endpoints
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Billing System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(endpoints.router, prefix="/api")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/bill")
async def bill_page(request: Request):
    return templates.TemplateResponse("bill.html", {"request": request})