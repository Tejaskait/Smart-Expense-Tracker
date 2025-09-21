# expenses/views.py
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Expenses
from .serializers import ExpenseSerializer, ExpenseImageSerializer
from PIL import Image
import pytesseract
import re
from datetime import datetime

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expenses.objects.all()
    serializer_class = ExpenseSerializer

class UploadExpenseImage(APIView):
    def post(self, request, format=None):
        serializer = ExpenseImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            text = pytesseract.image_to_string(Image.open(image))

            # Extract Amount
            amount_match = re.search(r'₹?\s?(\d+[.,]?\d*)', text)
            amount = float(amount_match.group(1).replace(',', '')) if amount_match else 0

            # Extract Date
            date_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{2,4})', text)
            date = datetime.strptime(date_match.group(1), '%d/%m/%Y').date() if date_match else None

            # Extract Receiver (simple heuristic)
            receiver_match = re.search(r'To:\s*(.+)', text)
            receiver = receiver_match.group(1).strip() if receiver_match else "Unknown"

            expense = Expenses.objects.create(
                title=receiver,
                amount=amount,
                date=date
            )
            return Response(ExpenseSerializer(expense).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
