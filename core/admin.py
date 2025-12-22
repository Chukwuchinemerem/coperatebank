from django.contrib import admin
from .models import UserProfile, Transaction, Notification

admin.site.register(UserProfile)
admin.site.register(Transaction)
admin.site.register(Notification)
