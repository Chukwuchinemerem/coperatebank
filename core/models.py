from django.db import models
from django.contrib.auth.models import User

import random

def generate_account_number():
	return str(random.randint(1000000000, 9999999999))

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	full_name = models.CharField(max_length=100)
	phone = models.CharField(max_length=20)
	address = models.CharField(max_length=255)
	dob = models.DateField()
	sex = models.CharField(max_length=10)
	country = models.CharField(max_length=50)
	occupation = models.CharField(max_length=50)
	passport = models.ImageField(upload_to='passports/')
	account_number = models.CharField(max_length=20, unique=True, default=generate_account_number)
	balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
	# Admin/transfer fields
	is_authorized = models.BooleanField(default=True)  # If False, transfers require admin approval
	pending_transfer = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Amount pending admin approval
	transfer_pin = models.CharField(max_length=10, blank=True, null=True)  # PIN issued by admin
	is_frozen = models.BooleanField(default=False)  # If True, account is frozen

	def __str__(self):
		return self.user.username


# Transaction log model
class Transaction(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='transactions')
	tx_type = models.CharField(max_length=20, choices=[('deposit','Deposit'),('withdrawal','Withdrawal'),('transfer','Transfer'),('admin','Admin')])
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	timestamp = models.DateTimeField(auto_now_add=True)
	description = models.TextField(blank=True)
	related_user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_transactions')

	def __str__(self):
		return f"{self.user.full_name} {self.tx_type} ${self.amount} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

# Notification model
class Notification(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications')
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)

	def __str__(self):
		return f"To {self.user.full_name}: {self.message[:30]}..."
