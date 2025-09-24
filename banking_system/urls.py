from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/password-reset-complete/'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Accounts
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/<int:account_id>/', views.account_detail, name='account_detail'),
    path('accounts/<int:account_id>/statement/', views.account_statement, name='account_statement'),
    
    # Transactions
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('transaction/<uuid:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/export/', views.export_transactions, name='export_transactions'),
    
    # Transfers & Payments
    path('transfer/', views.transfer_money, name='transfer_money'),
    path('transfer/quick/', views.quick_transfer, name='quick_transfer'),
    path('billpay/', views.bill_pay, name='bill_pay'),
    path('billpay/<uuid:bill_id>/cancel/', views.cancel_bill_pay, name='cancel_bill_pay'),
    
    # Alerts & Notifications
    path('alerts/', views.alerts_center, name='alerts'),
    path('alerts/<int:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
    path('alerts/mark-all-read/', views.mark_all_alerts_read, name='mark_all_alerts_read'),
    
    # Profile & Settings
    path('profile/', views.customer_profile, name='customer_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('security/', views.security_settings, name='security_settings'),
    path('security/update/', views.update_security_settings, name='update_security_settings'),
    
    # Statements & Documents
    path('statements/', views.account_statements, name='account_statements'),
    path('statements/generate/', views.generate_statement, name='generate_statement'),
    path('documents/', views.account_documents, name='account_documents'),
    
    # API Endpoints
    path('api/account-balance/<int:account_id>/', views.api_account_balance, name='api_account_balance'),
    path('api/transfer/', views.api_transfer, name='api_transfer'),
    path('api/transaction-history/', views.api_transaction_history, name='api_transaction_history'),
    path('api/alerts/count/', views.api_alerts_count, name='api_alerts_count'),
]

# Error handlers (add these to views.py)
def bad_request(request, exception):
    return render(request, 'accounts/400.html', status=400)

def permission_denied(request, exception):
    return render(request, 'accounts/403.html', status=403)

def page_not_found(request, exception):
    return render(request, 'accounts/404.html', status=404)

def server_error(request):
    return render(request, 'accounts/500.html', status=500)