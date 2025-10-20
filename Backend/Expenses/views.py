from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import ExpenseImageUploadForm
from .models import Expenses
from datetime import datetime
import google.generativeai as genai
from io import BytesIO
import json
from django.conf import settings


# -----------------------------
# Configure Gemini API
# -----------------------------
genai.configure(api_key=settings.GOOGLE_API_KEY)


# -----------------------------
# Basic Pages
# -----------------------------
def home(request):
    return render(request, 'home.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def about(request):
    return render(request, 'about.html')


# -----------------------------
# Signup
# -----------------------------
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
