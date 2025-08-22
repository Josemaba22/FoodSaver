# FoodSaver API

A REST API built with FastAPI for food inventory management.

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)

## Description

FoodSaver is an API that allows you to manage a food inventory system, organizing items by categories and tracking their admission dates.

## Technologies Used

- fastapi
- uvicorn
- sqlalchemy
- mysql-connector-python
- pydantic
- pymysql
- resend

## Prerequisites

- Docker and Docker Compose
- Or for local development:
  - Python 3.8 or higher
  - MySQL Server
  - pip (Python package manager)

## Setup and Running

### Docker Setup (Recommended)

1. Build and start the containers:
```bash
docker-compose up --build -d
```

2. Access the API:
- API Endpoints: http://localhost:3002
- Swagger UI: http://localhost:3002/docs
- ReDoc: http://localhost:3002/redoc

3. Database Connection Details:
```
Host: localhost
Port: 3308
Database: food_inventory
User: food_user
Password: food_password
```

4. Stop the containers:
```bash
docker-compose down
```

### Local Development Setup

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment on Windows
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup
- Create a MySQL database named `food_inventory`
- Update credentials in `app/config/db.py` if needed

### 4. Start the Server

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Interactive Documentation

### Swagger UI
- Access at `http://localhost:8000/docs`
- Interactive interface featuring:
  - All available endpoints
  - Direct operation testing
  - Data schemas
  - Integrated authentication

### ReDoc
- Access at `http://localhost:8000/redoc`
- Alternative detailed documentation
- Better for reference and consultation

## API Usage Guide

### Category Management

#### 1. Create a New Category
```http
POST /categories
{
    "name": "Fruits"
}
```

#### 2. Get All Categories
```http
GET /categories
```

#### 3. Get Category by ID
```http
GET /categories/{category_id}
```

### Food Management

#### 1. Create a New Food Item
```http
POST /foods
{
    "name": "Apple",
    "category_id": 1,
    "admission_date": "2025-08-18"
}
```

#### 2. Get All Food Items
```http
GET /foods
```

#### 3. Get Food Item by ID
```http
GET /foods/{food_id}
```

#### 4. Update a Food Item
```http
PUT /foods/{food_id}
{
    "name": "Green Apple",
    "category_id": 1,
    "admission_date": "2025-08-18"
}
```

#### 5. Delete a Food Item
```http
DELETE /foods/{food_id}
```

### Response Examples

#### Successful Response
```json
{
    "id": 1,
    "name": "Apple",
    "category_id": 1,
    "admission_date": "2025-08-18",
    "category": {
        "id": 1,
        "name": "Fruits"
    }
}
```

#### Error Response
```json
{
    "detail": "Food not found"
}
```
## Project Structure

```
app/
├── config/         # Database configuration
├── controllers/    # API controllers
├── dtos/          # Data Transfer Objects
├── entities/      # Database models
├── exceptions/    # Custom exceptions
├── repositories/  # Data access layer
├── services/      # Business logic
└── main.py        # Application entry point
```

## Features

- Complete CRUD operations for food items and categories
- Data validation with Pydantic
- Layered architecture
- Automatic documentation with Swagger/OpenAPI
