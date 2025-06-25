from django.contrib import admin
from gestionLogin.models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "user_type", "nivel", "experiencia")
    search_fields = ("username", "email")

admin.site.register(User, UserAdmin)
