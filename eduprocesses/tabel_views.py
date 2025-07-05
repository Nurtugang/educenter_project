from django.shortcuts import render
from django.db.models import Sum, F
from django.contrib.auth.models import Group

from users.models import CustomUser
from .models import Lesson, StudyGroupType
from eduprocesses.date_utils import get_this_month_dates, get_this_week_dates


def calc_lessons_and_hours_count(request, status, choosen_range, group_type, is_admin, is_teacher):
	lessons_hours = [1, 2, 3]
	lessons = Lesson.objects.filter(study_group__group_type = group_type)
	if isinstance(choosen_range, tuple):
		lessons = lessons.filter(date__range=choosen_range)
	elif choosen_range in ['1', '2', '3', '4']:
		lessons = lessons.filter(quarter=choosen_range)	

	if status == 'P':
		lessons = lessons.filter(status='P', substitute_teacher__isnull = True)

	if is_teacher:
		lessons_cnt = lessons.filter(study_group__teacher = request.user).count()
		lessons_hours = lessons.filter(study_group__teacher = request.user).aggregate(total_hours=Sum('hours'))['total_hours'] or 0
	elif is_admin:
		lessons_cnt = lessons.count()
		lessons_hours = lessons.aggregate(total_hours=Sum('hours'))['total_hours'] or 0

	return (lessons_cnt, lessons_hours)


def filter_lessons(request, status, is_substituted_teacher, choosen_range, is_admin, is_teacher):
	lessons = Lesson.objects.all().select_related('study_group')

	if type(choosen_range) == tuple:
		lessons = lessons.filter(date__range=choosen_range)
	elif choosen_range in ['1', '2', '3', '4']:
		lessons = lessons.filter(quarter=choosen_range)	

	if status == 'P':
		lessons = lessons.filter(status='P')
		if is_teacher:
			if is_substituted_teacher:
				lessons = lessons.filter(substitute_teacher = request.user)
			else:
				lessons = lessons.filter(study_group__teacher = request.user, substitute_teacher__isnull = True)
	elif status == 'all':
		if is_teacher:
			if is_substituted_teacher:
				lessons = lessons.filter(substitute_teacher = request.user)
			else:
				lessons = lessons.filter(study_group__teacher = request.user)

	if is_admin:
		if is_substituted_teacher:
			lessons = lessons.filter(substitute_teacher__isnull = False)
		else:
			lessons = lessons.filter(substitute_teacher__isnull = True)
	return lessons.order_by('-date')


def tabel(request):
	#роль пользователя
	is_subs_teacher = True
	is_admin = request.user.groups.filter(name__in=['Администратор']).exists()
	is_teacher = request.user.groups.filter(name__in=['Преподаватель']).exists()  

	teachers = CustomUser.objects.filter(groups = Group.objects.get(name='Преподаватель'))
	group_types = StudyGroupType.objects.all().order_by('-payment')

	all_lessons_per_group_type = {} #словарь-> тип_группы:кол-во всех уроков
	all_payments_per_group_type = {} #словарь-> тип_группы:выплата по всем урокам
	all_hours_per_group_type = {} #словарь-> тип_группы:кол-во часов всех уроков 

	complete_lessons_per_group_type = {} #словарь-> тип_группы:кол-во проведенных уроков
	complete_payments_per_group_type = {} #словарь-> тип_группы:выплата по проведенным урокам
	complete_hours_per_group_type = {} #словарь-> тип_группы:кол-во часов проведенных уроков

	

	if request.method == 'POST': #если использован фильтр
		if request.POST.get('tabel-quarter'): #если выбрана четверть
			tabel_quarter = request.POST.get('tabel-quarter')
			choosen_range = tabel_quarter
			selected_period = tabel_quarter
			start_date = end_date = '2023-08-08'
		elif request.POST.get('tabel-date'): #если выбранаа дата
			tabel_date = request.POST.get('tabel-date')
			if tabel_date == 'week': #период этой недели
				start_date, end_date = get_this_week_dates()
				choosen_range = (start_date, end_date)
				selected_period = 'week'
			elif tabel_date == 'month': #период этого месяца
				start_date, end_date = get_this_month_dates()
				choosen_range = (start_date, end_date)
				selected_period = 'month'
			else: #произвольный период
				start_date, end_date = tabel_date.split(' - ')
				choosen_range = (start_date, end_date)
				selected_period = ' '

	else: #если фильтр не использован(первичная загрузка страницы)
		start_date, end_date = get_this_month_dates() #фильтр по умолчанию
		choosen_range = (start_date, end_date)
		selected_period = 'month'

	
	#подробные таблицы
	completed_lessons = filter_lessons(request, 'P', not is_subs_teacher, choosen_range, is_admin, is_teacher)
	all_lessons = filter_lessons(request, 'all', not is_subs_teacher, choosen_range, is_admin, is_teacher)

	completed_changed_lessons = filter_lessons(request, 'P', is_subs_teacher, choosen_range, is_admin, is_teacher)
	all_changed_lessons = filter_lessons(request, 'all', is_subs_teacher, choosen_range, is_admin, is_teacher)

	#суммы табелей
	completed_lessons_total_price = completed_lessons.aggregate(
		total = Sum( F('study_group__group_type__payment') * F('hours')))['total'] or 0
	all_lessons_total_price = all_lessons.aggregate(
		total = Sum( F('study_group__group_type__payment') * F('hours')))['total'] or 0

	completed_changed_lessons_total_price = completed_changed_lessons.aggregate(total = Sum( F('study_group__group_type__payment') * F('hours')))['total'] or 0
	all_changed_lessons_total_price = all_changed_lessons.aggregate(total = Sum( F('study_group__group_type__payment') * F('hours')))['total'] or 0

	#кол-во часов
	completed_lessons_total_hours = completed_lessons.aggregate(Sum('hours'))['hours__sum'] or 0
	completed_changed_lessons_total_hours = completed_changed_lessons.aggregate(Sum('hours'))['hours__sum'] or 0

	all_lessons_total_hours = all_lessons.aggregate(Sum('hours'))['hours__sum'] or 0
	all_changed_lessons_total_hours = all_changed_lessons.aggregate(Sum('hours'))['hours__sum'] or 0

	#hardest part
	#быстрая сводная 
	
	for group_type in group_types:
		complete_lessons_per_group_type[f'{group_type.name}'], complete_hours_per_group_type[f'{group_type.name}'] = calc_lessons_and_hours_count(request, 'P', choosen_range, group_type, is_admin, is_teacher)
		all_lessons_per_group_type[f'{group_type.name}'], all_hours_per_group_type[f'{group_type.name}'] = calc_lessons_and_hours_count(request, 'all', choosen_range, group_type, is_admin, is_teacher)

		complete_payments_per_group_type[f'{group_type.name}'] = complete_hours_per_group_type[f'{group_type.name}'] * group_type.payment
		all_payments_per_group_type[f'{group_type.name}'] = all_hours_per_group_type[f'{group_type.name}'] * group_type.payment 


	context = {
		'complete_lessons_per_group_type': complete_lessons_per_group_type,
		'complete_payments_per_group_type': complete_payments_per_group_type,
		'complete_hours_per_group_type': complete_hours_per_group_type,

		'all_hours_per_group_type': all_hours_per_group_type,
		'all_lessons_per_group_type': all_lessons_per_group_type,
		'all_payments_per_group_type': all_payments_per_group_type,

		'completed_lessons': completed_lessons,
		'completed_lessons_total_price': completed_lessons_total_price,
		'completed_changed_lessons': completed_changed_lessons,
		'completed_changed_lessons_total_price': completed_changed_lessons_total_price,
		
		'all_lessons': all_lessons,
		'all_lessons_total_price': all_lessons_total_price,
		'all_changed_lessons': all_changed_lessons,
		'all_changed_lessons_total_price': all_changed_lessons_total_price,

		'completed_lessons_total_hours': completed_lessons_total_hours,
		'completed_changed_lessons_total_hours': completed_changed_lessons_total_hours,
		'all_lessons_total_hours': all_lessons_total_hours,
		'all_changed_lessons_total_hours': all_changed_lessons_total_hours,


		'start_date': str(start_date),
		'end_date': str(end_date),

		'selected_period': selected_period,
		'choosen_range': choosen_range,

		'teachers': teachers,
		'group_types': group_types,

		'is_admin': is_admin,
		'is_teacher': is_teacher,
	}
	return render(request, 'tabel.html', context)

