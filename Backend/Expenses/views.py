from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from datetime import datetime
import calendar
from .models import Expenses
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login


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

    context = {
        "expenses": expenses,
        "total_expenses": total_expenses,
        "monthly_budget": monthly_budget,
        "remaining_balance": remaining_balance,
        "month_names": month_names,
        "month_values": month_values,
        "selected_month": selected_month or "all",
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
