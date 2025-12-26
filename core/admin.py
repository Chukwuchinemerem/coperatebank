
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Transaction, Notification

class UserProfileInline(admin.StackedInline):
	model = UserProfile
	can_delete = False
	verbose_name_plural = 'Profile'
	fk_name = 'user'
	fields = ('full_name', 'phone', 'address', 'dob', 'sex', 'country', 'occupation', 'passport', 'account_number', 'balance', 'is_authorized', 'pending_transfer', 'transfer_pin', 'is_frozen')
	readonly_fields = ('account_number',)

	def get_field_queryset(self, db, db_field, request):
		return super().get_field_queryset(db, db_field, request)

class UserAdmin(BaseUserAdmin):
	inlines = (UserProfileInline,)
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

	def get_inline_instances(self, request, obj=None):
		if not obj:
			return []
		return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'full_name', 'phone', 'country', 'balance', 'is_authorized', 'is_frozen', 'passport_image')
	readonly_fields = ('passport_image',)
	fields = ('user', 'full_name', 'phone', 'address', 'dob', 'sex', 'country', 'occupation', 'passport', 'passport_image', 'account_number', 'balance', 'is_authorized', 'pending_transfer', 'transfer_pin', 'is_frozen')

	def passport_image(self, obj):
		if obj.passport:
			return f'<img src="{obj.passport.url}" style="max-height:100px;max-width:100px;" />'
		return "No image"
	passport_image.allow_tags = True
	passport_image.short_description = 'Passport Photo'

admin.site.register(Transaction)
admin.site.register(Notification)
