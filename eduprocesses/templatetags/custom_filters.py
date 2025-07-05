from django import template
from eduprocesses.models import StudentAttendance 
import random


register = template.Library()

@register.filter
def attendance_exists(student, lesson):
    """
    Проверяет, существует ли объект посещаемости для студента и урока.
    Возвращает True, если объект существует, иначе False.
    """
    return StudentAttendance.objects.filter(lesson=lesson, student=student).exists()

@register.filter
def get_attendance_mark(student, lesson):
	try:
		attendance = student.studentattendance_set.get(lesson=lesson)
		if attendance.attendance_status == 'ABS-R': #не пришел, с причиной
			return 'НБ(П)'
		elif attendance.attendance_status == 'ABS-NR': #не пришел, без причины
			return 'НБ'
		if attendance.mark == None:
			return ' '
		else:
			return attendance.mark
	except StudentAttendance.DoesNotExist:
		return ' '


@register.filter
def get_dnevnik_data(attendance):
    if attendance.mark:
        return attendance.mark
    if attendance.attendance_status:
        if attendance.attendance_status == 'ABS-R': # не пришел, с причиной
            return 'НБ(П)'
        elif attendance.attendance_status == 'ABS-NR': # не пришел, без причины
            return 'НБ'
    if attendance.lesson.status == 'O':
        return 'Отм'
    elif attendance.lesson.status == 'Z':
        return 'Зам'
    
    return "-"


@register.filter
def get_dict_value(d, key):
	return d.get(key, None)

@register.filter
def multiply(value, arg):
	return value * arg

@register.filter
def shuffle(arg):
    aux = list(arg)[:]
    random.shuffle(aux)
    return aux

@register.filter
def get_homework_status(student, lesson):
    """
    Получает статус выполнения домашнего задания для студента и урока
    """
    try:
        attendance = student.studentattendance_set.get(lesson=lesson)
        if attendance.homework_completed == True:
            return 'completed'
        elif attendance.homework_completed == False:
            return 'not_completed'
        else:
            return 'not_marked'
    except StudentAttendance.DoesNotExist:
        return 'not_marked'

@register.filter
def get_homework_display(student, lesson):
    """
    Возвращает текстовое представление статуса ДЗ
    """
    try:
        attendance = student.studentattendance_set.get(lesson=lesson)
        if attendance.homework_completed == True:
            return '✓'
        elif attendance.homework_completed == False:
            return '✗'
        else:
            return '—'
    except StudentAttendance.DoesNotExist:
        return '—'