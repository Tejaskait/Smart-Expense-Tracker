from rest_framework import serializers
from .models import Expenses

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenses
        fields = "__all__" 


class ExpenseImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()