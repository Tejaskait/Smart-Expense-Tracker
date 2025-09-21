# expenses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, UploadExpenseImage

router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/upload/', UploadExpenseImage.as_view(), name='upload-expense-image'),
]
