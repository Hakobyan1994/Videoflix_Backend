# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
  list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
  list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
  search_fields = ('email',)
  ordering = ('-date_joined',) 

admin.site.register(User, UserAdmin)