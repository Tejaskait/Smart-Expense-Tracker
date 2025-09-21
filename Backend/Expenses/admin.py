from django.contrib import admin
from .models import Expenses  # <-- use Expenses

admin.site.register(Expenses)
    