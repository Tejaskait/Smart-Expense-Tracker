from django.db import models

# Create your models here.

class Expense(models.Model):
    title = models.Charfield(max_length = 80)
    amount = models.DecimalField(max_digits = 10,decimal_place = 2)
    category = models.CharField(max_length = 50, blank=True, null = True)
    date = models.DateField(auto_now_add = True)

    def __str__(self):
        return f"{self.title} - {self.amount}"
