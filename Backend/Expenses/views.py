from django.shortcuts import render
from .forms import ExpenseImageUploadForm
from .models import Expenses
from PIL import Image
import pytesseract
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



def upload_expense_image(request):
    if request.method == "POST":
        form = ExpenseImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = Image.open(request.FILES['image'])
            
            # OCR text extraction
            text = pytesseract.image_to_string(img)

            # Simple parsing logic (adjust as needed)
            merchant = "Unknown"
            amount = 0.0
            date = datetime.today().date()

            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if line.lower().startswith("paid to"):
                    merchant = line[8:].strip()
                elif line.replace('.', '', 1).isdigit():  # crude amount detection
                    amount = float(line)

            expense = Expenses.objects.create(
                merchant=merchant,
                amount=amount,
                date=date,
                image=request.FILES['image']
            )

            # Pass saved data to template
            context = {
                'merchant': expense.merchant,
                'amount': expense.amount,
                'date': expense.date
            }
            return render(request, 'upload_success.html', context)
    else:
        form = ExpenseImageUploadForm()
    
    return render(request, 'upload_expense.html', {'form': form})
