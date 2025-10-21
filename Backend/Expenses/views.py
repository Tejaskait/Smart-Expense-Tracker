from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from datetime import datetime
import calendar
from collections import defaultdict
from .models import Expenses
from .forms import ExpenseImageUploadForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
import google.generativeai as genai
from io import BytesIO
import json
from django.conf import settings

# -----------------------------
# Configure Gemini API
# -----------------------------
genai.configure(api_key=settings.GOOGLE_API_KEY)



# 🏠 Home Page
def home(request):
    return render(request, 'home.html')


# ➕ Add Expense
def add_expense(request):
    if request.method == "POST":
        date = request.POST.get("date")
        category = request.POST.get("category")
        amount = request.POST.get("amount")
        description = request.POST.get("description")

        if amount:
            Expenses.objects.create(
                amount=float(amount),
                date=date,
                category=category,
                merchant=description or "Manual Entry"
            )
        return redirect("dashboard")

    return redirect("home")


# 🗑️ Delete Expense
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expenses, id=expense_id)
    expense.delete()
    return redirect("dashboard")


# 📊 Dashboard Page
def dashboard(request):
    # 🔹 Handle month filter
    selected_month = request.GET.get('month')
    expenses = Expenses.objects.all().order_by('-date')

    if selected_month and selected_month != "all":
        expenses = expenses.filter(date__month=int(selected_month))

    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Load budget from session (default ₹25000)
    monthly_budget = request.session.get("monthly_budget", 25000)
    remaining_balance = monthly_budget - total_expenses

    # Monthly expense chart data
    month_names, month_values = [], []
    for m in range(1, 13):
        month_names.append(calendar.month_abbr[m])
        total = Expenses.objects.filter(date__month=m).aggregate(Sum('amount'))['amount__sum'] or 0
        month_values.append(total)

    # Aggregate expenses per category for pie chart
    category_data = defaultdict(float)
    for e in expenses:
        category_data[e.category] += e.amount

    category_labels = list(category_data.keys())
    category_values = list(category_data.values())

    context = {
        "expenses": expenses,
        "total_expenses": total_expenses,
        "monthly_budget": monthly_budget,
        "remaining_balance": remaining_balance,
        "month_names": month_names,
        "month_values": month_values,
        "selected_month": selected_month or "all",
        "category_labels": category_labels,
        "category_values": category_values,
    }
    return render(request, "dashboard.html", context)


# 💰 Set Monthly Budget
def set_budget(request):
    if request.method == "POST":
        budget = request.POST.get("budget")
        if budget:
            request.session["monthly_budget"] = float(budget)
        return redirect("dashboard")
    return redirect("dashboard")


# ℹ️ About Page
def about(request):
    return render(request, 'about.html')


# 🧾 Signup Page
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


# -----------------------------
# Upload Expense Image (Gemini OCR)
# -----------------------------
def upload_expense_image(request):
    if request.method == "POST":
        form = ExpenseImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Load image bytes
            image_bytes = request.FILES['image'].read()

            model = genai.GenerativeModel("models/gemini-2.5-flash")

            prompt = """
            You are an OCR and data extraction assistant. 
            Extract the following details from the uploaded receipt image:
            - merchant (store or payee name)
            - amount (numeric only)
            - date (in YYYY-MM-DD format)
            
            Return the result strictly as JSON with keys:
            {"merchant": "", "amount": "", "date": ""}

            Do not include any extra text or explanation.
            """

            response = model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])

            # Gemini might sometimes return formatted JSON with backticks or extra text
            raw_output = response.text.strip()
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()

            # Parse JSON safely
            try:
                data = json.loads(raw_output)
            except json.JSONDecodeError:
                data = {"merchant": "Unknown", "amount": 0.0, "date": str(datetime.today().date())}

            # Clean & convert fields
            merchant = data.get("merchant", "Unknown")
            amount = float(str(data.get("amount", 0)).replace(",", "").strip())

            # Clean date format
            date_str = str(data.get("date", "")).replace('"', '').replace('“', '').replace('”', '')
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                date = datetime.today().date()

            # Save to DB
            expense = Expenses.objects.create(
                merchant=merchant,
                amount=amount,
                date=date,
                image=request.FILES['image']
            )

            # Render result
            context = {
                'merchant': expense.merchant,
                'amount': expense.amount,
                'date': expense.date
            }
            return render(request, 'upload_success.html', context)

    else:
        form = ExpenseImageUploadForm()

    return render(request, 'upload_expense.html', {'form': form})
