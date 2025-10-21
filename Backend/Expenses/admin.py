from django.contrib import admin
from .models import Expenses

@admin.register(Expenses)
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'amount', 'date', 'category', 'user')
    search_fields = ('merchant', 'category', 'user__username')
