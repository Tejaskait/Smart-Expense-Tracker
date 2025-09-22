from django.shortcuts import render, redirect
from .models import Expenses
from datetime import datetime , date

def expenses_list(request):
    expenses = Expenses.objects.all().order_by('-date')
    return render(request, "expenses_list.html", {"expenses": expenses})

def upload_expense_image(request):
    if request.method == "POST":
        title = request.POST.get("title")
        amount = request.POST.get("amount")
        category = request.POST.get("category", "")
        expense_date = request.POST.get("date")

        if expense_date:
            expense_date = datetime.strptime(expense_date, "%Y-%m-%d").date()
        else:
            expense_date = date.today()

        Expenses.objects.create(
            title=title,
            amount=amount,
            category=category,
            date=expense_date
        )

        return redirect("expenses_list")

    return render(request, "upload_expense.html")
