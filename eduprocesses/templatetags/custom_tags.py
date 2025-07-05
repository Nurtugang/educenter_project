from django import template
from eduprocesses.models import Lesson, StudentAttendance, StudyGroupType
from django.db.models import Sum
register = template.Library()

@register.simple_tag
def get_hours_sum(teacher, group_type, choosen_range):
	try:
		lessons = Lesson.objects.filter(study_group__teacher = teacher, study_group__group_type = group_type,
			status = 'P', substitute_teacher__isnull = True)
		if isinstance(choosen_range, tuple):
			lessons = lessons.filter(date__range=choosen_range)
		elif choosen_range in ['1', '2', '3', '4']:
			lessons = lessons.filter(quarter=choosen_range)	
		return lessons.aggregate(Sum('hours'))['hours__sum'] or 0
	except Exception as e:
		print(e)
		return 0


@register.simple_tag
def get_hours_sum_all(teacher, group_type, choosen_range):
	try:
		lessons = Lesson.objects.filter(study_group__teacher = teacher, study_group__group_type = group_type)
		if isinstance(choosen_range, tuple):
			lessons = lessons.filter(date__range=choosen_range)
		elif choosen_range in ['1', '2', '3', '4']:
			lessons = lessons.filter(quarter=choosen_range)	
		return lessons.aggregate(Sum('hours'))['hours__sum'] or 0
	except Exception as e:
		print(e)
		return -1

@register.simple_tag
def get_student_statuses(student, status, choosen_range):
	try:
		sa = StudentAttendance.objects.filter(student=student, attendance_status=status[0])
		if isinstance(choosen_range, tuple):
			sa = sa.filter(lesson__date__range=choosen_range)
		elif choosen_range in ['1', '2', '3', '4']:
			sa = sa.filter(lesson__quarter=choosen_range)	
		return sa.count()
	except Exception as e:
		print(e)
		return -1

@register.simple_tag
def get_student_statuses_sum(student, choosen_range):
	try:
		sa = StudentAttendance.objects.filter(student=student)
		if isinstance(choosen_range, tuple):
			sa = sa.filter(lesson__date__range=choosen_range)
		elif choosen_range in ['1', '2', '3', '4']:
			sa = sa.filter(lesson__quarter=choosen_range)	
		return sa.count()
	except Exception as e:
		print(e)
		return -1

@register.simple_tag
def get_bad_lessons(student, choosen_range):
	try:
		sa = StudentAttendance.objects.filter(student=student, lesson__status__in = ['NP', 'Z', 'O'])
		if isinstance(choosen_range, tuple):
			sa = sa.filter(lesson__date__range=choosen_range)
		elif choosen_range in ['1', '2', '3', '4']:
			sa = sa.filter(lesson__quarter=choosen_range)	
		return sa.count()
	except Exception as e:
		print(e)
		return -1


@register.simple_tag
def homework_completion_rate(student, lessons):
    """
    Вычисляет процент выполнения домашних заданий студентом
    """
    try:
        # Получаем все уроки с домашними заданиями
        lessons_with_homework = [lesson for lesson in lessons if lesson.homework]
        
        if not lessons_with_homework:
            return 0
        
        # Считаем выполненные ДЗ
        completed_homework = 0
        for lesson in lessons_with_homework:
            try:
                attendance = StudentAttendance.objects.get(student=student, lesson=lesson)
                if attendance.homework_completed == True:
                    completed_homework += 1
            except StudentAttendance.DoesNotExist:
                continue
        
        # Вычисляем процент
        completion_rate = (completed_homework / len(lessons_with_homework) * 100) if lessons_with_homework else 0
        return int(completion_rate)
    
    except Exception as e:
        print(f"Error calculating homework completion rate: {e}")
        return 0