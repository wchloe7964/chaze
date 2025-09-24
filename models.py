from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from decimal import Decimal

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    ssn_last_four = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.customer_id}"

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('money_market', 'Money Market'),
        ('cd', 'Certificate of Deposit'),
        ('ira', 'IRA'),
        ('credit_card', 'Credit Card'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('closed', 'Closed'),
        ('frozen', 'Frozen'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True, default=lambda: str(uuid.uuid4())[:16])
    routing_number = models.CharField(max_length=9, default='021000021')  # Chase routing number
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_nickname = models.CharField(max_length=50, blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=3, default=0.001)  # APR
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    opened_date = models.DateField(default=timezone.now)
    closed_date = models.DateField(null=True, blank=True)
    overdraft_protection = models.BooleanField(default=False)
    minimum_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-opened_date']

    def __str__(self):
        nickname = f" - {self.account_nickname}" if self.account_nickname else ""
        return f"****{self.account_number[-4:]}{nickname}"

    def save(self, *args, **kwargs):
        if not self.account_nickname:
            self.account_nickname = f"{self.get_account_type_display()} Account"
        super().save(*args, **kwargs)

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ('transfer', 'Transfer'),
        ('withdrawal', 'Withdrawal'),
        ('deposit', 'Deposit'),
        ('payment', 'Payment'),
        ('fee', 'Fee'),
    )

    CATEGORIES = (
        ('food', 'Food & Dining'),
        ('shopping', 'Shopping'),
        ('transport', 'Transportation'),
        ('entertainment', 'Entertainment'),
        ('bills', 'Bills & Utilities'),
        ('healthcare', 'Healthcare'),
        ('income', 'Income'),
        ('transfer', 'Transfer'),
        ('subscriptions', 'Subscriptions'),
        ('mortgage', 'Mortgage/Rent'),
        ('insurance', 'Insurance'),
        ('education', 'Education'),
        ('travel', 'Travel'),
        ('grocery', 'Groceries'),
        ('gas', 'Gasoline'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField()
    merchant = models.CharField(max_length=100, blank=True)
    merchant_category = models.CharField(max_length=50, blank=True)
    check_number = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed')
    date = models.DateTimeField(default=timezone.now)
    posted_date = models.DateTimeField(default=timezone.now)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    location_city = models.CharField(max_length=50, blank=True)
    location_state = models.CharField(max_length=2, blank=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['account', 'date']),
            models.Index(fields=['date', 'transaction_type']),
        ]

class Transfer(models.Model):
    transfer_id = models.UUIDField(default=uuid.uuid4, unique=True)
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='outgoing_transfers')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='incoming_transfers')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=(
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ), default='completed')
    initiated_date = models.DateTimeField(default=timezone.now)
    completed_date = models.DateTimeField(null=True, blank=True)
    fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-initiated_date']

class BillPay(models.Model):
    bill_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payee_name = models.CharField(max_length=100)
    payee_account = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    scheduled_date = models.DateField()
    status = models.CharField(max_length=10, choices=(
        ('scheduled', 'Scheduled'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ), default='scheduled')
    frequency = models.CharField(max_length=10, choices=(
        ('once', 'One Time'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ), default='once')
    created_date = models.DateTimeField(auto_now_add=True)

class Alert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=(
        ('low_balance', 'Low Balance'),
        ('large_transaction', 'Large Transaction'),
        ('unusual_activity', 'Unusual Activity'),
        ('bill_reminder', 'Bill Reminder'),
        ('security', 'Security Alert'),
    ))
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    related_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_date']