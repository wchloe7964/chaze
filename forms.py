from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomerProfile, Account, BillPay, Transfer

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'address', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['from_account', 'to_account', 'amount', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'description': forms.TextInput(attrs={'placeholder': 'Enter description...'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_account'].queryset = Account.objects.filter(user=user, status='active')
        self.fields['to_account'].queryset = Account.objects.filter(user=user, status='active')

    def clean(self):
        cleaned_data = super().clean()
        from_account = cleaned_data.get('from_account')
        to_account = cleaned_data.get('to_account')
        amount = cleaned_data.get('amount')

        if from_account and to_account:
            if from_account == to_account:
                raise forms.ValidationError("Cannot transfer to the same account.")
            
            if amount and from_account.available_balance < amount:
                raise forms.ValidationError("Insufficient funds for this transfer.")

        return cleaned_data

class BillPayForm(forms.ModelForm):
    class Meta:
        model = BillPay
        fields = ['payee_name', 'payee_account', 'amount', 'scheduled_date', 'frequency']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        }

class AccountNicknameForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['account_nickname']