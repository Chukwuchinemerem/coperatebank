from django.shortcuts import render
# ...existing code...

def about(request):
    return render(request, 'core/about.html')

def faq(request):
    return render(request, 'core/faq.html')

def privacy(request):
    return render(request, 'core/privacy.html')

def terms(request):
    return render(request, 'core/terms.html')
from django.contrib.admin.views.decorators import staff_member_required

# Admin dashboard view
@staff_member_required
def admin_dashboard(request):
    from django.contrib import messages
    from .models import UserProfile, Transaction, Notification
    users = UserProfile.objects.all()
    transactions = Transaction.objects.all().order_by('-timestamp')[:50]
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        # Add funds
        if 'add_funds' in request.POST:
            amount = request.POST.get('amount')
            try:
                user_profile = UserProfile.objects.get(id=user_id)
                from decimal import Decimal
                user_profile.balance += Decimal(amount)
                user_profile.save()
                Transaction.objects.create(user=user_profile, tx_type='deposit', amount=Decimal(amount), description='Admin deposit')
                messages.success(request, f'${amount} added to {user_profile.full_name} successfully!')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User not found.')
        # Approve KYC
        elif 'approve_kyc' in request.POST:
            try:
                user_profile = UserProfile.objects.get(id=user_id)
                user_profile.kyc_status = 'Approved'
                user_profile.save()
                messages.success(request, f'KYC approved for {user_profile.full_name}.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User not found.')
        # Reject KYC
        elif 'reject_kyc' in request.POST:
            try:
                user_profile = UserProfile.objects.get(id=user_id)
                user_profile.kyc_status = 'Rejected'
                user_profile.save()
                messages.success(request, f'KYC rejected for {user_profile.full_name}.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User not found.')
        # Set transfer PIN
        elif 'set_pin' in request.POST:
            pin = request.POST.get('transfer_pin')
            try:
                user_profile = UserProfile.objects.get(id=user_id)
                user_profile.transfer_pin = pin
                user_profile.save()
                messages.success(request, f'Transfer PIN set for {user_profile.full_name}.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User not found.')
        # Freeze user
        elif 'freeze_user' in request.POST:
            try:
                user_profile = UserProfile.objects.get(id=user_id)
                user_profile.is_frozen = True
                user_profile.save()
                messages.success(request, f'User {user_profile.full_name} account frozen.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User not found.')
        # Unfreeze user
        elif 'unfreeze_user' in request.POST:
            try:
                user_profile = UserProfile.objects.get(id=user_id)
                user_profile.is_frozen = False
                user_profile.save()
                messages.success(request, f'User {user_profile.full_name} account unfrozen.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User not found.')
        # Delete user
        elif 'delete_user' in request.POST:
            try:
                user_profile = UserProfile.objects.get(id=user_id)
                user_profile.user.delete()
                user_profile.delete()
                messages.success(request, 'User deleted successfully.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User not found.')
        # Send notification
        elif 'send_notification' in request.POST:
            notify_user_id = request.POST.get('notify_user_id')
            notify_message = request.POST.get('notify_message')
            try:
                notify_user = UserProfile.objects.get(id=notify_user_id)
                Notification.objects.create(user=notify_user, message=notify_message)
                messages.success(request, f'Notification sent to {notify_user.full_name}.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User not found for notification.')
    return render(request, 'core/admin_dashboard.html', {'users': users, 'transactions': transactions})
from django.contrib.auth.decorators import login_required
from .models import UserProfile

from django.contrib import messages
from decimal import Decimal

@login_required
def dashboard(request):
    from django.contrib import messages
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Auto-create profile for user if missing
        from django.contrib.auth.models import User
        user = request.user
        profile = UserProfile.objects.create(
            user=user,
            full_name=f"{user.first_name} {user.last_name}".strip(),
            phone="",
            address="",
            dob="2000-01-01",
            sex="",
            country="",
            occupation="",
            passport=None
        )
        profile.save()
    if request.method == 'POST':
        recipient_account = request.POST.get('recipient_account')
        amount = request.POST.get('amount')
        transfer_pin = request.POST.get('transfer_pin')
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, 'Amount must be greater than zero.')
            elif profile.balance < amount:
                messages.error(request, 'Insufficient balance.')
            elif not profile.transfer_pin or transfer_pin != profile.transfer_pin:
                messages.error(request, 'Invalid or missing transfer PIN. Please get your PIN from the admin.')
            else:
                try:
                    recipient = UserProfile.objects.get(account_number=recipient_account)
                    profile.balance -= amount
                    recipient.balance += amount
                    profile.save()
                    recipient.save()
                    # Log transaction for sender
                    from .models import Transaction
                    Transaction.objects.create(
                        user=profile,
                        tx_type='transfer',
                        amount=amount,
                        description=f'Transfer to {recipient.full_name} ({recipient.account_number})',
                        related_user=recipient
                    )
                    # Log transaction for recipient
                    Transaction.objects.create(
                        user=recipient,
                        tx_type='transfer',
                        amount=amount,
                        description=f'Transfer from {profile.full_name} ({profile.account_number})',
                        related_user=profile
                    )
                    messages.success(request, f'Transferred ${amount} to {recipient.full_name} ({recipient.account_number}) successfully!')
                except UserProfile.DoesNotExist:
                    messages.error(request, 'Recipient account not found.')
        except Exception:
            messages.error(request, 'Invalid amount.')
    return render(request, 'core/dashboard.html', {'profile': profile})
from django.contrib.auth import authenticate, login as auth_login

def login(request):
    from django.contrib import messages
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'core/login.html')
from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect
from django.core.files.storage import default_storage
from django.conf import settings
import os
from datetime import datetime

def register(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        middlename = request.POST.get('middlename')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        dob = request.POST.get('dob')
        sex = request.POST.get('sex')
        country = request.POST.get('country')
        occupation = request.POST.get('occupation')
        passport = request.FILES.get('passport')
        password = request.POST.get('password')
        username = email

        # Save passport file
        passport_path = None
        if passport:
            passport_path = default_storage.save(f'passports/{passport.name}', passport)

        user = User.objects.create_user(username=username, email=email, password=password,
                                       first_name=firstname, last_name=lastname)
        user.save()
        full_name = f"{firstname} {middlename} {lastname}".strip()
        profile = UserProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            address=address,
            dob=dob,
            sex=sex,
            country=country,
            occupation=occupation,
            passport=passport_path if passport_path else None
        )
        profile.save()
        auth_login(request, user)
        return redirect('dashboard')
    return render(request, 'core/register.html')
