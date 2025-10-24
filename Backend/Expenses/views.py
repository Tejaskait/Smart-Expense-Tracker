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
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse



# -----------------------------
# Configure Gemini API
# -----------------------------
genai.configure(api_key=settings.GOOGLE_API_KEY)



# 🏠 Home Page
def home(request):
    return render(request, 'home.html')


from datetime import date, timedelta
from django.db.models import Sum

@login_required
def profile_view(request):
    # Get all expenses for the current user
    expenses = Expenses.objects.filter(user=request.user)

    # Map each date → total spent on that date
    daily_expenses = (
        expenses.values('date')
        .annotate(total=Sum('amount'))
        .order_by('date')
    )

    # Create a dictionary for quick lookup
    expense_map = {d['date']: float(d['total']) for d in daily_expenses}

    # Build last 90 days (or 3 months) of history
    today = date.today()
    start_date = today - timedelta(days=89)
    days = [start_date + timedelta(days=i) for i in range(90)]

    # Normalize total expense values to color intensity
    max_expense = max(expense_map.values()) if expense_map else 0
    graph_data = []
    for d in days:
        amt = expense_map.get(d, 0)
        if max_expense > 0:
            intensity = int((amt / max_expense) * 100)
        else:
            intensity = 0
        graph_data.append({
            "date": d,
            "amount": amt,
            "intensity": intensity
        })

    return render(request, "profile.html", {"graph_data": graph_data, "user": request.user})

# ➕ Add Expense
@login_required
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
                merchant=description or "Manual Entry",
                user=request.user if request.user.is_authenticated else None
            )

        return redirect("dashboard")

    return redirect("home")


# 🗑️ Delete Expense
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expenses, id=expense_id)
    expense.delete()
    return redirect("dashboard")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "registration/login.html", {"error": "Invalid credentials"})
    return render(request, "registration/login.html")



def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            return render(request, "registration/signup.html", {"error": "Username already exists"})
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect("dashboard")
    return render(request, "registration/signup.html")



@login_required
def logout_view(request):
    logout(request)
    return redirect("login")



# 📊 Dashboard Page
@login_required
def dashboard(request):
    # 🔹 Handle month filter
    selected_month = request.GET.get('month')
    if request.user.is_authenticated:
        expenses = Expenses.objects.filter(user=request.user).order_by('-date')
    else:
        expenses = Expenses.objects.none()


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
@login_required
def upload_expense_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]
        image_bytes = image_file.read()
        
        import google.generativeai as genai
        from datetime import datetime
        import json
        
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        prompt = """
        You are an OCR assistant. Extract from the uploaded receipt:
        - merchant
        - amount (numeric only)
        - date (YYYY-MM-DD)
        Return strictly JSON: {"merchant": "", "amount": "", "date": ""} 
        Do NOT include extra text.
        """
        
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])
        
        raw_output = response.text.strip()
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1
        json_str = raw_output[start:end] if start != -1 and end != -1 else "{}"
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            data = {"merchant": "Unknown", "amount": 0.0, "date": str(datetime.today().date())}
        
        merchant = data.get("merchant", "Unknown")
        try:
            amount = float(str(data.get("amount", 0)).replace(",", "").strip())
        except ValueError:
            amount = 0.0
        
        date_str = str(data.get("date", "")).replace('"','').replace('“','').replace('”','')
        try:
            date_val = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            date_val = datetime.today().date()
        
        expense = Expenses.objects.create(
            merchant=merchant,
            amount=amount,
            date=date_val,
            category="Other",  # Or user can edit later
            image=image_file,
            user=request.user
        )
        
        # Return JSON for AJAX
        return JsonResponse({
            "id": expense.id,
            "merchant": expense.merchant,
            "amount": expense.amount,
            "date": expense.date.strftime("%Y-%m-%d"),
            "category": expense.category
        })
    
    return JsonResponse({"error": "No image uploaded"}, status=400)