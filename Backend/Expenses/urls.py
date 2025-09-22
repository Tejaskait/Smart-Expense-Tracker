# Expenses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.expenses_list, name="expenses_list"),
    path("upload/", views.upload_expense_image, name="upload_expense"),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
