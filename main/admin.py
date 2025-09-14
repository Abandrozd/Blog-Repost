
# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, BlogRequest, SavedRequest
from django.forms.models import BaseInlineFormSet
from django import forms

class RequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            # If the form has errors, don't check required
            return
        # Require at least one form (profile)
        if not any(form.has_changed() for form in self.forms):
            raise forms.ValidationError('User profile is required for each user.')

# Inline for UserProfile in User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    formset = RequiredInlineFormSet
    fields = ('litnet_link', 'vk_link', 'subscribers_count',
              'genres', 'telegram_nickname', 'balance')


# Extend User admin to include profile
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_balance')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

    def get_balance(self, obj):
        return f"{obj.profile.balance} ₽" if hasattr(obj, 'profile') else "No Profile"

    get_balance.short_description = 'Balance'
    get_balance.admin_order_field = 'profile__balance'


# Custom BlogRequest admin
@admin.register(BlogRequest)
class BlogRequestAdmin(admin.ModelAdmin):
    list_display = ('book_name', 'user', 'start_date', 'date_created', 'acceptance_count')
    list_filter = ('start_date', 'date_created', 'user__profile__genres')
    search_fields = ('book_name', 'user__username', 'user__email')
    date_hierarchy = 'start_date'
    ordering = ('-date_created',)

    fields = ('user', 'book_name', 'litnet_link', 'vk_link',
              'start_date', 'available_from', 'available_to')

    def acceptance_count(self, obj):
        return SavedRequest.objects.filter(request=obj).count()

    acceptance_count.short_description = 'Acceptances'

    # Allow admin to create requests for any user
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.all().order_by('username')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Custom SavedRequest admin
@admin.register(SavedRequest)
class SavedRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_title', 'request_author', 'created_at')
    list_filter = ('created_at', 'request__user')
    search_fields = ('user__username', 'request__book_name', 'request__user__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def request_title(self, obj):
        return obj.request.book_name

    request_title.short_description = 'Request Title'

    def request_author(self, obj):
        return obj.request.user.username

    request_author.short_description = 'Request Author'


# Custom UserProfile admin (separate from User)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'subscribers_count', 'genres', 'telegram_nickname')
    list_filter = ('genres',)
    search_fields = ('user__username', 'user__email', 'telegram_nickname')
    ordering = ('user__username',)

    fields = ('user', 'balance', 'litnet_link', 'vk_link',
              'subscribers_count', 'genres', 'telegram_nickname')


# Re-register User with our custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Customize admin site headers
admin.site.site_header = "Blog Exchange Admin"
admin.site.site_title = "Blog Exchange Admin"
admin.site.index_title = "Welcome to Blog Exchange Administration"

