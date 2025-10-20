from django import forms
from .models import Expenses

class ExpenseImageUploadForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['image']
