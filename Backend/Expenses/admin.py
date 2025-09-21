from django.contrib import admin
from .models import Expense

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title','amount','category','date')   # show columns
    search_fields = ('title','category')                  # search bar
    list_filter = ('category','date')                     # filter

