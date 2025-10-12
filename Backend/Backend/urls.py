# Backend/urls.py
from django.contrib import admin
from django.urls import path, include
from Expenses import views as expenses_views

# Wrong import (causing error):
# from .views import ExpensesViewSet, UploadExpensesImage

urlpatterns = [
    path('admin/', admin.site.urls),
        path('accounts/', include('django.contrib.auth.urls')),

    # Signup — custom view we will create
    path('accounts/signup/', expenses_views.signup, name='signup'),

    path('', include('Expenses.urls')),  # include your app urls instead
]
