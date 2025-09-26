
from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_expense_image, name="upload_expense"),
    path('', views.home, name='home'),
]

