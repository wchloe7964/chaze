from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import CustomerProfile, Account, Transaction, Transfer, BillPay, Alert

class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (CustomerProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'account_type', 'balance', 'status', 'opened_date')
    list_filter = ('account_type', 'status', 'opened_date')
    search_fields = ('account_number', 'user__username', 'user__email')
    readonly_fields = ('account_number', 'opened_date')
    fieldsets = (
        (None, {
            'fields': ('user', 'account_number', 'account_type', 'account_nickname')
        }),
        ('Balances', {
            'fields': ('balance', 'available_balance', 'interest_rate')
        }),
        ('Status', {
            'fields': ('status', 'opened_date', 'closed_date')
        }),
        ('Features', {
            'fields': ('overdraft_protection', 'minimum_balance')
        }),
    )

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'account', 'amount', 'transaction_type', 'category', 'date', 'status')
    list_filter = ('transaction_type', 'category', 'status', 'date')
    search_fields = ('transaction_id', 'account__account_number', 'description')
    readonly_fields = ('transaction_id', 'date', 'posted_date')
    date_hierarchy = 'date'

class TransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_id', 'from_account', 'to_account', 'amount', 'status', 'initiated_date')
    list_filter = ('status', 'initiated_date')
    readonly_fields = ('transfer_id', 'initiated_date')

class BillPayAdmin(admin.ModelAdmin):
    list_display = ('bill_id', 'user', 'payee_name', 'amount', 'scheduled_date', 'status')
    list_filter = ('status', 'frequency', 'scheduled_date')
    search_fields = ('payee_name', 'user__username')

class AlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'alert_type', 'message', 'is_read', 'created_date')
    list_filter = ('alert_type', 'is_read', 'created_date')
    search_fields = ('user__username', 'message')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register other models
admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Transfer, TransferAdmin)
admin.site.register(BillPay, BillPayAdmin)
admin.site.register(Alert, AlertAdmin)