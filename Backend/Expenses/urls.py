from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_expense_image, name='upload_expense_image'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('set-budget/', views.set_budget, name='set_budget'),
    path('delete-expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('login/', views.login_view, name='login'),
path('signup/', views.signup_view, name='signup'),
path('logout/', views.logout_view, name='logout'),
path('profile/', views.profile_view, name='profile'),
path('delete-account/', views.delete_account, name='delete_account'),



]
