from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Account, Transaction, CustomerProfile, Transfer, BillPay, Alert
import random
from faker import Faker
from decimal import Decimal

fake = Faker()

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Create customer profile and sample data
            create_customer_profile(user)
            create_sample_data(user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def create_customer_profile(user):
    """Create customer profile for new user"""
    CustomerProfile.objects.create(
        user=user,
        phone_number=fake.phone_number()[:15],
        address=fake.address(),
        date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=90),
        ssn_last_four=fake.random_number(digits=4, fix_len=True)
    )

@login_required
def dashboard(request):
    """Main dashboard similar to Chase Online Banking"""
    accounts = Account.objects.filter(user=request.user, status='active')
    
    # Create sample data if no accounts exist
    if not accounts.exists():
        accounts = create_sample_data(request.user)

    # Calculate totals
    total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0
    available_balance = accounts.aggregate(total=Sum('available_balance'))['total'] or 0
    
    # Recent transactions (last 10 across all accounts)
    recent_transactions = Transaction.objects.filter(
        account__user=request.user
    ).select_related('account').order_by('-date')[:10]

    # Upcoming bills
    upcoming_bills = BillPay.objects.filter(
        user=request.user,
        scheduled_date__gte=timezone.now().date(),
        status='scheduled'
    ).order_by('scheduled_date')[:5]

    # Recent alerts
    recent_alerts = Alert.objects.filter(user=request.user, is_read=False)[:5]

    # Quick account summary
    account_summary = []
    for account in accounts:
        account_summary.append({
            'account': account,
            'recent_activity': Transaction.objects.filter(account=account).order_by('-date')[:3]
        })

    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'available_balance': available_balance,
        'recent_transactions': recent_transactions,
        'upcoming_bills': upcoming_bills,
        'recent_alerts': recent_alerts,
        'account_summary': account_summary,
    }
    return render(request, 'accounts/dashboard.html', context)

def create_sample_data(user):
    """Create realistic sample banking data"""
    accounts = []
    
    # Create checking account
    checking = Account.objects.create(
        user=user,
        account_type='checking',
        account_nickname='Chase Premier Checking',
        balance=Decimal('12567.89'),
        available_balance=Decimal('12567.89'),
        interest_rate=Decimal('0.001'),
        overdraft_protection=True
    )
    accounts.append(checking)

    # Create savings account
    savings = Account.objects.create(
        user=user,
        account_type='savings',
        account_nickname='Chase Savings',
        balance=Decimal('45320.15'),
        available_balance=Decimal('45320.15'),
        interest_rate=Decimal('0.015')
    )
    accounts.append(savings)

    # Create credit card account
    credit_card = Account.objects.create(
        user=user,
        account_type='credit_card',
        account_nickname='Chase Freedom Unlimited',
        balance=Decimal('-1245.67'),  # Negative balance for credit cards
        available_balance=Decimal('8754.33'),
        interest_rate=Decimal('0.1899')  # 18.99% APR
    )
    accounts.append(credit_card)

    # Create sample transactions for each account
    create_sample_transactions(checking, 25)
    create_sample_transactions(savings, 10)
    create_sample_transactions(credit_card, 15)

    return accounts

def create_sample_transactions(account, count):
    """Create realistic sample transactions for an account"""
    categories = [cat[0] for cat in Transaction.CATEGORIES]
    merchants = {
        'debit': ['Amazon', 'Walmart', 'Starbucks', 'Target', 'Whole Foods', 
                 'Exxon Mobil', 'Shell', 'Uber', 'Netflix', 'Apple Store'],
        'credit': ['Salary Deposit', 'Interest Payment', 'Transfer In', 'Dividend'],
        'payment': ['Credit Card Payment', 'Mortgage Payment', 'Car Payment']
    }

    balance = account.balance
    for i in range(count):
        if account.account_type == 'credit_card':
            # For credit cards, most transactions are debits (purchases)
            trans_type = random.choice(['debit', 'debit', 'debit', 'credit', 'payment'])
        else:
            trans_type = random.choice(['debit', 'debit', 'credit', 'transfer'])

        if trans_type == 'debit':
            amount = Decimal(random.uniform(5, 250)).quantize(Decimal('0.01'))
            balance -= amount
            merchant = random.choice(merchants['debit'])
            category = random.choice(['shopping', 'food', 'transport', 'entertainment', 'bills'])
        elif trans_type == 'credit':
            amount = Decimal(random.uniform(100, 5000)).quantize(Decimal('0.01'))
            balance += amount
            merchant = random.choice(merchants['credit'])
            category = 'income'
        else:  # payment or transfer
            amount = Decimal(random.uniform(50, 2000)).quantize(Decimal('0.01'))
            if trans_type == 'payment':
                balance += amount if account.account_type == 'credit_card' else balance
                merchant = random.choice(merchants['payment'])
                category = 'transfer'
            else:
                balance += amount if random.choice([True, False]) else balance - amount
                merchant = 'Transfer'
                category = 'transfer'

        Transaction.objects.create(
            account=account,
            amount=amount,
            transaction_type=trans_type,
            category=category,
            description=f"{merchant} Transaction",
            merchant=merchant,
            balance_after=balance,
            location_city=fake.city(),
            location_state=fake.state_abbr()
        )

@login_required
def account_detail(request, account_id):
    """View account details and transactions"""
    account = get_object_or_404(Account, id=account_id, user=request.user)
    
    # Get transactions with pagination
    transactions = Transaction.objects.filter(account=account).order_by('-date')
    
    # Filter by date range if provided
    date_filter = request.GET.get('date_filter', '30')
    if date_filter != 'all':
        days = int(date_filter)
        start_date = timezone.now() - timedelta(days=days)
        transactions = transactions.filter(date__gte=start_date)

    context = {
        'account': account,
        'transactions': transactions,
        'date_filter': date_filter,
    }
    return render(request, 'accounts/account_detail.html', context)

@login_required
def transfer_money(request):
    """Handle money transfers between accounts"""
    if request.method == 'POST':
        try:
            from_account_id = request.POST.get('from_account')
            to_account_id = request.POST.get('to_account')
            amount = Decimal(request.POST.get('amount', 0))
            description = request.POST.get('description', '')

            from_account = get_object_or_404(Account, id=from_account_id, user=request.user)
            to_account = get_object_or_404(Account, id=to_account_id, user=request.user)

            if amount <= 0:
                return JsonResponse({'success': False, 'error': 'Invalid amount'})

            if from_account.available_balance < amount:
                return JsonResponse({'success': False, 'error': 'Insufficient funds'})

            # Perform transfer
            from_account.balance -= amount
            from_account.available_balance -= amount
            to_account.balance += amount
            to_account.available_balance += amount

            from_account.save()
            to_account.save()

            # Create transfer record
            transfer = Transfer.objects.create(
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                description=description,
                completed_date=timezone.now()
            )

            # Create transactions
            Transaction.objects.create(
                account=from_account,
                amount=amount,
                transaction_type='transfer',
                category='transfer',
                description=f"Transfer to {to_account.account_nickname}",
                balance_after=from_account.balance
            )

            Transaction.objects.create(
                account=to_account,
                amount=amount,
                transaction_type='transfer',
                category='transfer',
                description=f"Transfer from {from_account.account_nickname}",
                balance_after=to_account.balance
            )

            return JsonResponse({'success': True, 'transfer_id': transfer.transfer_id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # GET request - show transfer form
    accounts = Account.objects.filter(user=request.user, status='active')
    return render(request, 'accounts/transfer.html', {'accounts': accounts})

@login_required
def bill_pay(request):
    """Handle bill payments"""
    if request.method == 'POST':
        try:
            account_id = request.POST.get('account')
            payee_name = request.POST.get('payee_name')
            payee_account = request.POST.get('payee_account')
            amount = Decimal(request.POST.get('amount', 0))
            scheduled_date = request.POST.get('scheduled_date')

            account = get_object_or_404(Account, id=account_id, user=request.user)

            if amount <= 0:
                return JsonResponse({'success': False, 'error': 'Invalid amount'})

            bill = BillPay.objects.create(
                user=request.user,
                payee_name=payee_name,
                payee_account=payee_account,
                amount=amount,
                scheduled_date=scheduled_date
            )

            return JsonResponse({'success': True, 'bill_id': bill.bill_id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    accounts = Account.objects.filter(user=request.user, status='active')
    return render(request, 'accounts/bill_pay.html', {'accounts': accounts})

@login_required
def transaction_history(request):
    """View complete transaction history with filters"""
    transactions = Transaction.objects.filter(account__user=request.user).select_related('account').order_by('-date')
    
    # Apply filters
    account_filter = request.GET.get('account', 'all')
    type_filter = request.GET.get('type', 'all')
    category_filter = request.GET.get('category', 'all')
    date_filter = request.GET.get('date', '30')

    if account_filter != 'all':
        transactions = transactions.filter(account_id=account_filter)
    
    if type_filter != 'all':
        transactions = transactions.filter(transaction_type=type_filter)
    
    if category_filter != 'all':
        transactions = transactions.filter(category=category_filter)
    
    if date_filter != 'all':
        days = int(date_filter)
        start_date = timezone.now() - timedelta(days=days)
        transactions = transactions.filter(date__gte=start_date)

    accounts = Account.objects.filter(user=request.user, status='active')

    context = {
        'transactions': transactions,
        'accounts': accounts,
        'filters': {
            'account': account_filter,
            'type': type_filter,
            'category': category_filter,
            'date': date_filter,
        }
    }
    return render(request, 'accounts/transaction_history.html', context)

@login_required
def alerts_center(request):
    """View and manage alerts"""
    alerts = Alert.objects.filter(user=request.user).order_by('-created_date')
    return render(request, 'accounts/alerts.html', {'alerts': alerts})

@login_required
@csrf_exempt
def mark_alert_read(request, alert_id):
    """Mark an alert as read"""
    if request.method == 'POST':
        alert = get_object_or_404(Alert, id=alert_id, user=request.user)
        alert.is_read = True
        alert.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def transaction_detail(request, transaction_id):
    """View detailed transaction information"""
    transaction = get_object_or_404(
        Transaction, 
        transaction_id=transaction_id, 
        account__user=request.user
    )
    
    similar_transactions = Transaction.objects.filter(
        account__user=request.user,
        merchant=transaction.merchant,
        category=transaction.category
    ).exclude(transaction_id=transaction_id).order_by('-date')[:5]
    
    context = {
        'transaction': transaction,
        'similar_transactions': similar_transactions,
    }
    return render(request, 'accounts/transaction_detail.html', context)

@login_required
def customer_profile(request):
    """View and update customer profile"""
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('customer_profile')
    else:
        form = CustomerProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'accounts/customer_profile.html', context)

@login_required
def security_settings(request):
    """Security settings page"""
    if request.method == 'POST':
        # Handle security settings update
        messages.success(request, 'Security settings updated successfully')
        return redirect('security_settings')
    
    return render(request, 'accounts/security_settings.html')

@login_required
def account_statements(request):
    """Account statements page"""
    accounts = Account.objects.filter(user=request.user, status='active')
    
    # Generate statement periods (last 12 months)
    today = timezone.now()
    statement_periods = []
    for i in range(12):
        period_date = today - timedelta(days=30*i)
        statement_periods.append({
            'month': period_date.strftime('%B %Y'),
            'start_date': period_date.replace(day=1),
            'end_date': (period_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        })
    
    context = {
        'accounts': accounts,
        'statement_periods': statement_periods,
    }
    return render(request, 'accounts/account_statements.html', context)

# API Views
@login_required
@csrf_exempt
def api_transfer(request):
    """API endpoint for transfers"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Transfer logic here
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})