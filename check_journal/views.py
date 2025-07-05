from django.shortcuts import render
from users.models import CustomUser
from django.contrib.auth.models import Group
from eduprocesses.models import Lesson
from eduprocesses.views import get_this_month_dates, get_this_week_dates
from django.shortcuts import redirect
from datetime import datetime, timezone, time, timedelta, date


def deadline_full(request, selected_period, start_date, end_date):
	is_admin = request.user.groups.filter(name__in=['Администратор']).exists()
	if not is_admin:
		return redirect('index')

	if selected_period in ['1', '2', '3', '4']:
		lessons = Lesson.objects.filter(quarter=selected_period)
	elif selected_period in ['week', 'month', 'customrange']:
		start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
		end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
		lessons = Lesson.objects.filter(date__range=(start_date, end_date) )
	missed_lessons = lessons.filter(status = 'NP', date__lte=datetime.now(timezone.utc).date())
	for lesson in missed_lessons:
		today = datetime.now(timezone.utc).date()
		lesson.deadline = datetime.combine(today, time(0, 0)) + timedelta(days=1) 
		lesson.save()
	return redirect('check_journal')

def missed_lessons(request, teacher_id, selected_period, start_date, end_date):
	is_admin = request.user.groups.filter(name__in=['Администратор']).exists()
	if not is_admin:
		return redirect('index')
	if request.method == 'POST':
		selected_lessons = request.POST.getlist('selected_lessons')
		selected_lessons = selected_lessons[:-1]
		selected_lessons = [int(lesson) for lesson in selected_lessons]
		for sel_id in selected_lessons:
			lesson = Lesson.objects.get(id=sel_id)
			today = datetime.now(timezone.utc).date()
			lesson.deadline = datetime.combine(today, time(0, 0)) + timedelta(days=1) 
			lesson.save()

	lessons = Lesson.objects.filter(study_group__teacher_id = teacher_id)
	if selected_period in ['1', '2', '3', '4']:
		lessons = lessons.filter(quarter=selected_period)
	elif selected_period in ['week', 'month', 'customrange']:
		start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
		end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
		lessons = lessons.filter(date__range=(start_date, end_date) )
	missed_lessons = lessons.filter(status = 'NP')
	context = {
		'missed_lessons': missed_lessons.select_related('study_group').order_by('-date'),
		'lessons_cnt': lessons.count(),
		'missed_lessons_cnt': missed_lessons.count(),
		'teacher': CustomUser.objects.get(id=teacher_id)
	}
	return render(request, 'missed_lessons.html', context)

def check_journal(request):
	is_admin = request.user.groups.filter(name__in=['Администратор']).exists()
	if not is_admin:
		return redirect('index')
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
				selected_period = 'customrange'

	else: #если фильтр не использован(первичная загрузка страницы)
		start_date, end_date = get_this_week_dates() #фильтр по умолчанию
		choosen_range = (start_date, end_date)
		selected_period = 'week'


	teachers = CustomUser.objects.filter(groups = Group.objects.get(name='Преподаватель'))
	teachers_percentage = {}
	for t in teachers:
		all_lessons = Lesson.objects.filter(study_group__teacher=t)
		missed_lessons = all_lessons.filter(study_group__teacher=t, status='NP')
		if type(choosen_range) == tuple:
			all_lessons = all_lessons.filter(date__range=choosen_range).count()
			missed_lessons = missed_lessons.filter(date__range=choosen_range).count()
		elif choosen_range in ['1', '2', '3', '4']:
			all_lessons = all_lessons.filter(quarter=choosen_range).count()
			missed_lessons = missed_lessons.filter(quarter=choosen_range).count()
		if all_lessons == 0:
			teachers_percentage[t] = -1
		else:
			teachers_percentage[t] = 100 - int(missed_lessons/all_lessons * 100)



	context = {
		'start_date': str(start_date),
		'end_date': str(end_date),
		'selected_period': selected_period,
		'choosen_range': choosen_range,

		'teachers_percentage': teachers_percentage,
		'selected_period': selected_period,
	}
	return render(request, 'check_journal.html', context)