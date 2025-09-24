from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Accounts
    path('accounts/<int:account_id>/', views.account_detail, name='account_detail'),
    
    # Transactions
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('transaction/<uuid:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    
    # Transfers & Payments
    path('transfer/', views.transfer_money, name='transfer_money'),
    path('billpay/', views.bill_pay, name='bill_pay'),
    
    # Alerts
    path('alerts/', views.alerts_center, name='alerts'),
    path('alerts/<int:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
    
    # Profile & Settings
    path('profile/', views.customer_profile, name='customer_profile'),
    path('security/', views.security_settings, name='security_settings'),
    path('statements/', views.account_statements, name='account_statements'),
    
    # API Endpoints
    path('api/transfer/', views.api_transfer, name='api_transfer'),
    
    # Password reset (if needed)
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]