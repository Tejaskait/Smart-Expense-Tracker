from django.db import models

class Expenses(models.Model):
    amount = models.FloatField()
    date = models.DateField()
    merchant = models.CharField(max_length=255, default="Unknown")
    category = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="expenses/", null=True, blank=True)

    def __str__(self):
        return f"{self.merchant} - {self.amount}"
