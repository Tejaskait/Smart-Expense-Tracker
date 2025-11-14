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
from django.http import JsonResponse
from django.contrib import messages

# -----------------------------
# Configure Gemini API
# -----------------------------
genai.configure(api_key=settings.GOOGLE_API_KEY)

# 🏠 Home Page
def home(request):
    return render(request, 'home.html')


# 👤 Profile View
@login_required
def profile_view(request):
    total_spent = Expenses.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_transactions = Expenses.objects.filter(user=request.user).count()
    avg_daily_expense = round(total_spent / 90, 2) if total_spent else 0

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        if User.objects.exclude(id=request.user.id).filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif User.objects.exclude(id=request.user.id).filter(email=email).exists():
            messages.error(request, "Email already in use.")
        else:
            user = request.user
            user.username = username
            user.email = email
            user.save()
            messages.success(request, "Profile updated successfully ✅")
            return redirect('profile')

    context = {
        "user": request.user,
        "total_spent": total_spent,
        "total_transactions": total_transactions,
        "avg_daily_expense": avg_daily_expense,
    }
    return render(request, "profile.html", context)


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


# 🔐 Login View

def login_view(request):
    """
    Accepts POST with:
      - identifier (email OR username)
      - password
    Tries email lookup first (case-insensitive). If found, it authenticates using that user's username.
    Falls back to username-based authentication if email lookup fails.
    Returns same 'error' key your template already expects.
    """
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")

        user = None

        # If looks like an email, try to find user by email first
        if "@" in identifier:
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                # authenticate requires username
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        # If not found/authenticated yet, try treating the identifier as username
        if user is None:
            user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            # Keep same template behavior: return 'error' in context
            return render(request, "registration/login.html", {"error": "Invalid credentials — try email/username and password."})

    return render(request, "registration/login.html")

@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        logout(request)
        return redirect("home")
    return render(request, "profile.html", {"user": request.user})



# 🧾 Signup View
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


# 🚪 Logout
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# 📊 Dashboard Page
@login_required
def dashboard(request):
    selected_month = request.GET.get('month')
    if request.user.is_authenticated:
        expenses = Expenses.objects.filter(user=request.user).order_by('-date')
    else:
        expenses = Expenses.objects.none()

    if selected_month and selected_month != "all":
        expenses = expenses.filter(date__month=int(selected_month))

    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_budget = request.session.get("monthly_budget", 25000)
    remaining_balance = monthly_budget - total_expenses
    # 📊 Percentage of budget spent
    spent_percent = 0
    if monthly_budget > 0:
        spent_percent = round((total_expenses / monthly_budget) * 100, 1)


    # 📆 Monthly Expense Trend Data
    month_names, month_values = [], []
    for m in range(1, 13):
        month_names.append(calendar.month_abbr[m])
        total = Expenses.objects.filter(user=request.user, date__month=m).aggregate(Sum('amount'))['amount__sum'] or 0
        month_values.append(total)

    # 🧾 Category Breakdown
    category_data = defaultdict(float)
    for e in expenses:
        category_data[e.category] += e.amount

    category_labels = list(category_data.keys())
    category_values = list(category_data.values())

    # 🎨 Fixed Unique Colors
    category_colors = {
        "Food": "#FF6B6B",
        "Travel": "#4ECDC4",
        "Shopping": "#FFD93D",
        "Entertainment": "#6A5ACD",
        "Bills": "#FF8C00",
        "Health": "#20B2AA",
        "Education": "#9370DB",
        "Other": "#95A5A6"
    }

    category_color_list = [
        category_colors.get(cat, "#%06x" % (hash(cat) % 0xFFFFFF)) for cat in category_labels
    ]

    # Combine category + value + color
    category_totals = zip(category_labels, category_values, category_color_list)

    # 🔹 Weekly Expense Data (for backend)
    week_values = [0, 0, 0, 0]
    week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

    if selected_month and selected_month != "all":
        month_expenses = expenses
    else:
        import datetime
        current_month = datetime.date.today().month
        month_expenses = expenses.filter(date__month=current_month)

    for e in month_expenses:
        week_index = (e.date.day - 1) // 7
        if week_index < 4:
            week_values[week_index] += e.amount

    context = {
        "expenses": expenses,
        "total_expenses": total_expenses,
        "monthly_budget": monthly_budget,
        "remaining_balance": remaining_balance,
        "spent_percent": spent_percent,

        "month_names": month_names,
        "month_values": month_values,
        "selected_month": selected_month or "all",
        "category_labels": category_labels,
        "category_values": category_values,
        "category_colors": category_color_list,
        "category_totals": category_totals,
        "week_values": week_values,
        "week_labels": week_labels,
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


# 🧾 Signup (Form-based)
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


# 📸 Upload Expense Image (Gemini OCR)
@login_required
@login_required
def upload_expense_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]
        image_bytes = image_file.read()

        model = genai.GenerativeModel("models/gemini-2.5-flash")
        prompt = """
        You are an OCR assistant. Extract from the uploaded receipt:
        - merchant
        - amount (numeric only)
        - date (DD-MM-YYYY)
        - category(Food,Travel,Shopping,Personal if nothing matched)
        Return strictly JSON: {"merchant": "", "amount": "", "date": "", "category": ""} 
        """

        try:
            response = model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
            raw_output = response.text.strip()
            start = raw_output.find("{")
            end = raw_output.rfind("}") + 1
            json_str = raw_output[start:end] if start != -1 and end != -1 else "{}"
            data = json.loads(json_str)
        except Exception as e:
            return JsonResponse({"error": f"OCR failed: {str(e)}"}, status=500)

        # Just send extracted data — don't save yet
        return JsonResponse({
            "merchant": data.get("merchant", "Unknown"),
            "amount": data.get("amount", ""),
            "date": data.get("date", ""),
            "category": data.get("category", "Other")
        })

    return JsonResponse({"error": "No image uploaded"}, status=400)

@login_required
def confirm_expense(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        merchant = data.get("merchant", "Unknown")
        category = data.get("category", "Other")
        try:
            amount = float(str(data.get("amount", 0)).replace(",", "").strip())
        except ValueError:
            amount = 0.0

        try:
            date_val = datetime.strptime(data.get("date", ""), "%d-%m-%Y").date()
        except ValueError:
            date_val = datetime.today().date()

        expense = Expenses.objects.create(
            merchant=merchant,
            category=category,
            amount=amount,
            date=date_val,
            user=request.user
        )

        return JsonResponse({"message": "Expense saved successfully!", "id": expense.id})
    
    return JsonResponse({"error": "Invalid request"}, status=400)


import re
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 1️⃣ Check email format using regex
        if not EMAIL_REGEX.match(email):
            return render(request, "registration/signup.html", {
                "error": "⚠ Invalid email format. Please enter a valid email."
            })

        # 2️⃣ Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, "registration/signup.html", {
                "error": "⚠ Email already in use."
            })

        # 3️⃣ Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Auto login after signup
        login(request, user)

        return redirect("home")  # change to your homepage route

    return render(request, "registration/signup.html")
