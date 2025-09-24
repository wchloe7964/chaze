# accounts/management/commands/create_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import CustomerProfile, Account, Transaction
from django.utils import timezone
from decimal import Decimal
import random
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Create sample banking data for development'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of sample users to create')
        parser.add_argument('--transactions', type=int, default=50, help='Transactions per account')

    def handle(self, *args, **options):
        self.stdout.write('Creating sample banking data...')
        
        # Create sample users
        for i in range(options['users']):
            username = f'customer{i+1}'
            email = f'{username}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                self.create_customer_data(user, options['transactions'])
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))

        self.stdout.write(self.style.SUCCESS('Sample data creation completed!'))

    def create_customer_data(self, user, transaction_count):
        # Create customer profile
        profile, created = CustomerProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': fake.phone_number()[:15],
                'address': fake.address(),
                'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=90),
                'ssn_last_four': fake.random_number(digits=4, fix_len=True)
            }
        )

        # Create accounts
        account_types = ['checking', 'savings', 'credit_card']
        accounts = []
        
        for acc_type in account_types:
            balance = Decimal(random.randint(1000, 50000))
            if acc_type == 'credit_card':
                balance = -Decimal(random.randint(1000, 10000))
                
            account = Account.objects.create(
                user=user,
                account_type=acc_type,
                account_nickname=f"Chase {acc_type.title()} Account",
                balance=balance,
                available_balance=abs(balance),
                interest_rate=Decimal('0.015') if acc_type == 'savings' else Decimal('0.001')
            )
            accounts.append(account)
            
            # Create transactions
            self.create_sample_transactions(account, transaction_count)

    def create_sample_transactions(self, account, count):
        categories = ['food', 'shopping', 'transport', 'entertainment', 'bills', 'income']
        balance = account.balance
        
        for i in range(count):
            is_credit = random.choice([True, False]) if account.account_type != 'credit_card' else False
            amount = Decimal(random.uniform(10, 500)).quantize(Decimal('0.01'))
            
            if is_credit:
                balance += amount
                trans_type = 'credit'
                category = 'income'
                merchant = 'Deposit'
            else:
                balance -= amount
                trans_type = 'debit'
                category = random.choice(categories)
                merchant = fake.company()
            
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