# Billing System

A FastAPI-based billing system with a simple UI for managing products and generating bills.

## Features

- Product management with CRUD operations
- Dynamic billing calculator
- Customer email integration
- Denomination-based payment handling
- Previous purchases view
- Tax calculation
- Stock management

## Tech Stack

- Backend: FastAPI
- Database: PostgreSQL
- Frontend: HTML, CSS, JavaScript
- Template Engine: Jinja2

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/jeevithalakshminarayanan/Billing-System-Project.git
cd billing-system
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows
.\\venv\\Scripts\\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a PostgreSQL database named 'billing_system'

5. Create a .env file in the root directory with the following content:
```
DATABASE_URL=postgresql://username:password@localhost/billing_system
```
Replace username and password with your PostgreSQL credentials.

6. Run the application:
```bash
uvicorn app.main:app --reload
```

The application will be available at http://localhost:8000

## API Documentation

After running the application, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Schema

### Products Table
- id (Primary Key)
- name
- product_id (Unique)
- price
- available_stock
- tax_percentage

### Bills Table
- id (Primary Key)
- customer_email
- total_amount
- tax_amount
- final_amount
- created_at

### Bill Items Table
- id (Primary Key)
- bill_id (Foreign Key)
- product_id (Foreign Key)
- quantity
- unit_price
- total_price
- tax_amount

## Usage

1. Access the web interface at http://localhost:8000
2. Add products through the API or admin interface
3. Create bills by:
   - Entering customer email
   - Adding products and quantities
   - Entering payment denominations
   - Generating the bill
4. View previous bills by entering customer email

## Notes

- All amounts are in INR (₹)
- Tax is calculated per product based on the tax_percentage
- Stock is automatically updated when bills are generated
- Denominations available: 1, 2, 5, 10, 20, 50, 100, 500