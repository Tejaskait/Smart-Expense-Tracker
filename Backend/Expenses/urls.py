from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_expense_image, name='upload_expense'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('set-budget/', views.set_budget, name='set_budget'),
    path('delete-expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('signup/', views.signup, name='signup'),
]
