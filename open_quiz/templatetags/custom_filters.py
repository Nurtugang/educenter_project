from django import template

register = template.Library()

@register.filter
def divisibleby(value, arg):
    """Возвращает целую часть от деления"""
    try:
        return int(value) // int(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def modulo(value, arg):
    """Возвращает остаток от деления"""
    try:
        return int(value) % int(arg)
    except (ValueError, ZeroDivisionError):
        return 0