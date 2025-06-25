from django import template
from gestionLogin.models import User

register = template.Library()

@register.filter
def get_user_by_username(entidades, username):
    return next((e for e in entidades if e.username == username), None)