from django import template
register = template.Library()

@register.filter
def lookup(dict_obj, key):
    try:
        return dict_obj.get(key)
    except Exception:
        return None
