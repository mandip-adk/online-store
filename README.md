# Online Store – Django E-commerce Application

A Django-based e-commerce web application implementing core online shopping functionality including product management, cart system, order processing, and payment integration concepts.

## 🚀 Features

### 👤 User & Authentication
- Custom user model with email-based login  
- User roles:
  - Customer  
  - Delivery Person  
  - Admin  
- User registration, login & logout  
- “Remember me” session handling  

### 📦 Products & Categories
- Product listing with images  
- Product categories (many-to-many)  
- Featured products  
- Product detail page  
- Product filtering:
  - by name  
  - by price range  
  - by category  
- Sorting (price, latest, oldest)  
- Pagination  

### 🛒 Cart System
- Add products to cart  
- Update product quantity  
- Remove products from cart  
- Automatic cart creation per user  
- Cart total calculation  

### 📑 Orders
- Place orders from cart  
- Order history  
- Order cancellation  
- Order status tracking:
  - Pending  
  - Paid  
  - Shipped  
  - Delivered  
  - Cancelled  

### 💳 Payment (Khalti – Partial Implementation)
- Khalti payment gateway integration structure  
- Payment initiation flow implemented  
- Order → Payment relationship  
- Payment status handling logic  

**Important:**  
Payment verification is not fully functional due to environment and configuration issues. This project demonstrates payment gateway integration concepts and is not a production-ready payment system.

### 🚚 Delivery Person Module
- Separate delivery person profile  
- Age validation (18+)  
- Document upload (citizenship & driving license)  
- Vehicle details  
- Verification logic  

## 🛠️ Tech Stack
- **Backend:** Python, Django  
- **Database:** SQLite (default)  
- **Frontend:** HTML, CSS (Django Templates)  
- **Authentication:** Custom Django User Model  
- **Payment Gateway:** Khalti (test environment)  
- **Others:** Django ORM, Django Admin, Media handling  

## 📂 Project Structure

online-store/
│
├── accounts/          # Custom user & authentication
├── store/             # Products, cart, orders, payments
├── common_templates/  # Shared templates
├── project/           # Main Django project settings
├── manage.py
└── requirements.txt

## ⚙️ Installation & Setup

1. Clone the repository
    git clone https://github.com/mandip-adk/online-store.git
    cd online-store
2. Create and activate virtual environment
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    venv\Scripts\activate      # Windows
3. Install dependencies
    pip install -r requirements.txt
4. Run migrations
    python manage.py migrate
5. Create superuser
    python manage.py createsuperuser
6. Start the development server
    python manage.py runserver
7. Open in browser
    http://127.0.0.1:8000/

---

This project was developed with guidance during installation, setup, configuration, and the initial project structure phase.

## 👤 Author
**Mandip Adhikari**  
GitHub: https://github.com/mandip-adk