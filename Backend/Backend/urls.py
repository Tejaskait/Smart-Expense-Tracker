# Backend/urls.py
from django.contrib import admin
from django.urls import path, include

# Wrong import (causing error):
# from .views import ExpensesViewSet, UploadExpensesImage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Expenses.urls')),  # include your app urls instead
]
