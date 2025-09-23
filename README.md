# 📊 Smart Expense Tracker

A **Django-based expense tracker** that extracts text from uploaded screenshots (OCR) and saves expenses to the user’s database.  
Includes **weekly & monthly dashboards**, secure authentication, and a modular design that’s easy to extend.

---

## 🚀 Features
- 📸 Upload receipts/screenshot images  
- 🔎 OCR text extraction (pluggable adapters, e.g., Tesseract)  
- 💾 User-specific expense database  
- 📊 Weekly & monthly dashboards with charts and summaries  
- 🔐 User authentication & authorization  
- ⚡ Extensible architecture (add new OCR providers, dashboards, or export formats)  

---

## 🛠 Tech Stack
- **Backend:** Django (Python web framework)  
- **OCR:** Tesseract-OCR (default, pluggable adapters supported)  
- **Database:** PostgreSQL / MySQL / SQLite  
- **Optional:** Celery + Redis (for async OCR jobs)  
- **API:** Django REST Framework  

---

## 📦 Installation

Clone the repository: git clone https://github.com/your-username/smart-expense-tracker.git
Install dependencies: pip install -r requirements.txt
Run migrations: python manage.py migrate
Start the development server: python manage.py runserver

## Usage

Create a user account and log in
Upload a screenshot of your expense receipt
The OCR feature will extract text from the image and add it to your expense database
View your monthly and weekly dashboards to track your expenses

## Code Structure

expense_tracker: Django app containing models, views, and templates for expense tracking
ocr: Module containing OCR functionality for text extraction
dashboards: Module containing logic for generating monthly and weekly dashboards
**We will update code structure accordingly to future needs**


