from django.shortcuts import render
from .forms import UploadForm
from .models import Expenses
from PIL import Image
import pytesseract
import re
from datetime import datetime

def extract_text_from_image(image_file):
    img = Image.open(image_file)
    text = pytesseract.image_to_string(img)
    return text

def parse_upi_text(text):
    data = {}

    # Amount
    amount_match = re.search(r'₹\s?(\d+(?:\.\d+)?)', text)
    if amount_match:
        data['amount'] = float(amount_match.group(1))

    # Date (example: DD/MM/YYYY)
    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if date_match:
        data['date'] = datetime.strptime(date_match.group(1), '%d/%m/%Y').date()

    # Merchant: first non-empty line
    lines = text.split('\n')
    for line in lines:
        if line.strip():
            data['merchant'] = line.strip()
            break

    return data

def save_expense(data):
    expense = Expenses(
        merchant=data.get('merchant', 'Unknown'),
        amount=data.get('amount', 0),
        date=data.get('date')
    )
    expense.save()

def upload_expense_image(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']
            text = extract_text_from_image(image_file)
            data = parse_upi_text(text)
            save_expense(data)
            return render(request, 'success.html', {'data': data})
    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form})
