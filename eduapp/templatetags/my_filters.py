import re
from django import template

register = template.Library()

@register.filter(name='times') 
def times(number):
    number = int(number)
    return range(number)

@register.filter(name='is_teacher') 
def is_teacher(user):
    return user.groups.filter(name='Преподаватель').exists()

@register.filter(name='is_admin') 
def is_admin(user):
    return user.groups.filter(name='Администратор').exists()

@register.filter(name='is_student') 
def is_student(user):
    return user.groups.filter(name='Студент').exists()

@register.filter
def youtube_id(url):
    """Извлекает YouTube video ID из URL"""
    if not url:
        return ''
    
    patterns = [
        r'(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return ''