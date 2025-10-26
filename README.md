# 📊 Smart Expense Tracker

A **Django-based smart expense tracker** that extracts text from uploaded screenshots (OCR) and saves expenses to the user’s database.  
Includes **weekly & monthly dashboards**, secure authentication, and a modular design that’s easy to extend.

---

## 🚀 Features
- 📸 Upload receipts/screenshot images  
- 🔎 OCR text extraction (used Gemini API)  
- 💾 User-specific expense database  
- 📊 Category wise and Weekly & monthly dashboards with charts and summaries  
- 🔐 User authentication & authorization  
---

## 🛠 Tech Stack
- **Backend:** Django (Python web framework)  
- **OCR:** Gemini API 
- **Database:** Mostly db.sqlite3 
- **API:** Django REST Framework
- **FrontEnd:** Html, TailwindCSS, JS
- **Data Visualization:** Js ChartJS libraries
---

## 📦 Installation

Clone the repository: git clone https://github.com/your-username/smart-expense-tracker.git
Install dependencies: pip install -r requirements.txt
Run migrations: python manage.py migrate
Start the development server: python manage.py runserver

## 📊 Usage

Create a user account and log in
Upload a screenshot of your expense receipt
The OCR feature will extract text from the image and add it to your expense database
View your monthly and weekly dashboards to track your expenses

## 💾 Code Structure

**Myapp:** It contains the main binded django app.
Backend: It contains backend settings, urls, etc.
Expenses: Django app containing models, views, templates, urls, forms, etc. for expense tracking.

*Templates -*
base.html : It contains Html Landing Page with Navbar,Footer so that it can be extended for use on multiple pages
home.html : It is home page with hero section and main functions of adding expense.
dashboard.html : It contains dashboard having expense records, charts,etc.
login.html : It contains user login and info

static: It has Source files and external css.
db.sqlite3 : It has Database
.env: It stores venv and API key 
.requirements : It has all essential dependancies to be installed
