from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models import Avg, Q
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from users.models import CustomUser
from senim_store.models import UserCoins
from .models import *
from quizer.models import UserAnswer, QuizSubject

from eduprocesses.date_utils import get_this_month_dates, get_this_week_dates
import json


def journal(request):
	my_groups = StudyGroup.objects.filter(teacher=request.user)
	substitute_lessons = Lesson.objects.filter(substitute_teacher = request.user).select_related('study_group').order_by('-status')
	context = {
		'my_groups': my_groups,
		'substitute_lessons': substitute_lessons
	}
	return render(request, 'journal.html', context)


def journal_single(request, group_id):
	if request.method == 'POST':
		for key, value in request.POST.items():
			if key.startswith('Q'):
				selected_quarter = value
				break
		lessons = Lesson.objects.filter(quarter = selected_quarter, study_group_id=group_id)
		
	else:
		lessons = Lesson.objects.filter(study_group_id=group_id)
		if lessons:
			random_lesson = lessons[0]
			lessons = lessons.filter(quarter = random_lesson.quarter, study_group=random_lesson.study_group)
			selected_quarter = random_lesson.quarter
		else:
			selected_quarter = 'Q1'

	group = StudyGroup.objects.get(id=group_id)
	all_students = CustomUser.objects.filter(groups = Group.objects.get(name='Студент')).order_by('last_name')
	students_not_in_study_group = all_students.exclude(id__in=group.students.all().values('id')).order_by('last_name')

	students = group.students.annotate(
		avg_mark=Avg(
			'studentattendance__mark',
			filter=Q(studentattendance__lesson__study_group=group)
		)
	) 
	context = {
		'students': students,
		'group_id': group_id,
		'lessons': lessons.order_by('date'),
		'group': group,
		'selected_quarter': selected_quarter,
		'students_not_in_study_group': students_not_in_study_group,
	}
	
	
	return render(request, 'journal_single.html', context)


def journal_student(request):
	is_student = request.user.groups.filter(name__in=['Студент']).exists()

	if is_student:
		lessons_data = {}
		dates = set()
		subjects = set()

		if request.method == 'POST':
			for key, value in request.POST.items():
				if key.startswith('Q'):
					selected_quarter = value
					break	
			student_attendances = StudentAttendance.objects.filter(student=request.user, lesson__quarter = selected_quarter)	
		else:
			student_attendances = StudentAttendance.objects.filter(student=request.user)
			selected_quarter = '1'
			
		for sa in student_attendances:
			dates.add(sa.lesson.date)
			subjects.add(sa.lesson.study_group.subject)
		for subject in subjects:
			sa_subjects = student_attendances.filter(lesson__study_group__subject = subject)
			lessons_data[subject.name] = sa_subjects

		all_groups = StudyGroup.objects.filter(students__id = request.user.id)
		all_teachers_ids = all_groups.values_list('teacher', flat=True).distinct()
		all_teachers = []
		for teacher_id in all_teachers_ids:
			all_teachers.append(CustomUser.objects.get(id=teacher_id))  # Replace 'CustomUser' with your teacher model
		context = {
			'subjects': subjects,
			'dates': sorted(dates),
			'lessons_data': lessons_data,

			'all_groups': all_groups,
			'all_teachers': all_teachers,
			'selected_quarter': selected_quarter

		}
	
	return render(request, 'journal_student.html', context)


def lesson_student(request, lesson_id):
	sa = StudentAttendance.objects.get(student=request.user, lesson_id = lesson_id)
	context = {
		'lesson_id': lesson_id,
		'lesson': Lesson.objects.get(id=lesson_id),
		'has_subs_teacher': Lesson.objects.filter(id=lesson_id, substitute_teacher__isnull = False, status='Z').exists(),
		'sa': sa,
	}
	return render(request, 'lesson_student.html', context)


def lesson_single(request, lesson_id):
	if request.method == 'POST':
		almaty_tz = timezone.pytz.timezone(settings.TIME_ZONE)
		server_time = timezone.now().astimezone(almaty_tz)
		post_lesson = Lesson.objects.get(id=lesson_id)
		next_day_start = post_lesson.deadline.astimezone(almaty_tz)	
		post_lesson = Lesson.objects.get(id=lesson_id)
  
		if request.POST.get('reason'): 
		#форма для отмены урока
			if server_time < next_day_start:
				post_lesson.status = 'O'
				post_lesson.reason_for_not_held = request.POST.get('reason')
				post_lesson.save()
				messages.success(request, "Этот урок успешно отменен")
			else:
				messages.error(request, "Доступ к уроку закрыт")
		elif request.POST.get('zamena-teacher'):
			if server_time < next_day_start:
				zamena_teacher = CustomUser.objects.get(id=request.POST.get('zamena-teacher'))
				post_lesson.status = 'Z'
				post_lesson.substitute_teacher = zamena_teacher
				post_lesson.save()
				messages.success(request, "Этот урок успешно заменен другим учителем")
			else:
				messages.error(request, "Доступ к уроку закрыт")
		else:
			if server_time < next_day_start:
				post_student_attendances = StudentAttendance.objects.filter(lesson_id=lesson_id)
				group_students = post_lesson.study_group.students.all()
				
				# Отфильтруем посещаемость только для студентов, которые числятся в группе
				valid_attendances = post_student_attendances.filter(student__in=group_students)

				if valid_attendances.filter(attendance_status=None).exists():
					# если есть неотмеченные студенты в уроке
					messages.error(request, "У вас есть неотмеченные студенты")
				elif not post_lesson.homework:
					messages.error(request, "Заполните домвашнее задание")
				else:
					# если все студенты в уроке отмечены
					post_lesson.status = 'P'
					post_lesson.save()

					#присуждение коинов
					for vd in valid_attendances:
						if UserCoins.objects.filter(user=vd.student).exists() == False:
							UserCoins.objects.create(user=vd.student)
						uc = UserCoins.objects.get(user=vd.student)
						uc.balance += vd.coins
						uc.save()


					messages.success(request, "Этот урок успешно отмечен как проведенный")
			else:
				messages.error(request, f"Доступ к уроку закрыт. Дедлайн: {str(next_day_start)[:-9]}")
	
	lesson = Lesson.objects.get(id=lesson_id)
	study_group = lesson.study_group
	teacher = study_group.teacher
	
	# Получаем всех студентов, которые связаны с текущей учебной группой урока
	group_students = study_group.students.all()
	
	# Фильтруем посещаемость только тех студентов, которые входят в группу
	student_attendances = StudentAttendance.objects.filter(lesson_id=lesson_id, student__in=group_students)
# 	student_attendances = StudentAttendance.objects.filter(lesson_id=lesson_id) #старый баг аман удалить удалить студент когда оставался
	teachers = CustomUser.objects.filter(groups = Group.objects.get(name='Преподаватель')).exclude(pk=request.user.pk)
	
	is_substituted_teacher = Lesson.objects.filter(id=lesson_id, substitute_teacher=request.user, status='Z').exists()
	is_asked_substitute_teacher = Lesson.objects.filter(id=lesson_id, 
		substitute_teacher__isnull = False, study_group__teacher = request.user, status='Z').exists()
	
	
	context = {
		'lesson_id': lesson_id,
		'lesson': lesson,
		'teacher': teacher,
		'study_group': study_group,
		'student_attendances': student_attendances,
		'teachers': teachers,
		'is_substituted_teacher': is_substituted_teacher,
		'is_asked_substitute_teacher': is_asked_substitute_teacher,
	}
 
	return render(request, 'lesson_single.html', context)


def attendancy(request):
	is_admin = request.user.groups.filter(name__in=['Администратор']).exists()
	is_teacher = request.user.groups.filter(name__in=['Преподаватель']).exists()  

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

	if selected_period in ["1", '2', '3', '4']:
		attendances = StudentAttendance.objects.filter(lesson__quarter=choosen_range)
	else:
		attendances = StudentAttendance.objects.filter(lesson__date__range=choosen_range)

	if is_teacher:
		attendances = attendances.filter(lesson__study_group__teacher = request.user)
	students_ids = attendances.values_list('student', flat=True).distinct()
	students = [CustomUser.objects.get(id=student_id) for student_id in students_ids]

 
	context = {
		'start_date': str(start_date),
		'end_date': str(end_date),
		'choosen_range': choosen_range, 
		'selected_period': selected_period,

		'students': students,
		'attendance_status_choices': [
			('PR', 'Пришел на урок'),
			('ABS-R', 'Не пришел на урок с причиной'),
			('ABS-NR', 'Не пришел на урок без причины')
		],
		'is_admin': is_admin,
		'is_teacher': is_teacher,
	}
	return render(request, 'attendancy.html', context)


def add_student_to_group(request):
	if request.method == 'POST':
		group_id = request.POST.get('group_id')
		student_id = request.POST.get('student')
		group = get_object_or_404(StudyGroup, id=group_id)
		student = get_object_or_404(CustomUser, id=student_id)
		
		group.students.add(student)
		group.update_group_type()

  
		return redirect('journal_single', group_id=group_id)
	else:
		pass


def remove_student_from_group(request):
	if request.method == 'POST':
		group_id = request.POST.get('group_id')
		student_id = request.POST.get('student')
		group = get_object_or_404(StudyGroup, id=group_id)
		student = get_object_or_404(CustomUser, id=student_id)
	
		
		group.students.remove(student)
		group.update_group_type()
  
		return redirect('journal_single', group_id=group_id)
	else:
		pass

@login_required
def student_profile(request, student_id):
	"""Досье ученика с визуализацией данных"""
	
	# Проверка прав доступа
	is_admin = request.user.groups.filter(name='Администратор').exists()
	is_teacher = request.user.groups.filter(name='Преподаватель').exists()
	is_student = request.user.groups.filter(name='Студент').exists()
	
	student = get_object_or_404(CustomUser, id=student_id)
	
	# Проверка прав доступа к досье
	if is_student and request.user != student:
		# Студент может видеть только свое досье
		return redirect('profile')
	elif is_teacher:
		# Учитель может видеть досье только своих студентов
		teacher_groups = StudyGroup.objects.filter(teacher=request.user)
		if not teacher_groups.filter(students=student).exists():
			return redirect('journal')
	elif not is_admin:
		# Если не админ, не учитель и не студент - нет доступа
		return redirect('index')
	
	# Получение всех групп студента
	student_groups = StudyGroup.objects.filter(students=student)
	
	# Получение всех посещений студента
	all_attendances = StudentAttendance.objects.filter(student=student).select_related(
		'lesson', 'lesson__study_group', 'lesson__study_group__subject'
	)
	
	# Система фильтрации как в проверке журнала
	if request.method == 'POST': #если использован фильтр
		if request.POST.get('tabel-quarter'): #если выбрана четверть
			tabel_quarter = request.POST.get('tabel-quarter')
			choosen_range = tabel_quarter
			selected_period = tabel_quarter
			start_date = end_date = '2023-08-08'
		elif request.POST.get('tabel-date'): #если выбранаа дата
			tabel_date = request.POST.get('tabel-date')
			if tabel_date == 'week': #период этой недели
				from eduprocesses.date_utils import get_this_week_dates, get_this_month_dates
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
		from eduprocesses.date_utils import get_this_month_dates
		start_date, end_date = get_this_month_dates() #фильтр по умолчанию
		choosen_range = (start_date, end_date)
		selected_period = 'month'
	
	# Применяем фильтр к посещениям
	if selected_period in ['1', '2', '3', '4']:
		attendances = all_attendances.filter(lesson__quarter=selected_period)
	else:
		attendances = all_attendances.filter(lesson__date__range=choosen_range)
	
	# Общая статистика
	total_lessons = attendances.count()
	present_count = attendances.filter(attendance_status='PR').count()
	absent_with_reason = attendances.filter(attendance_status='ABS-R').count()
	absent_without_reason = attendances.filter(attendance_status='ABS-NR').count()
	
	# Расчет процентов посещаемости
	attendance_percentage = (present_count / total_lessons * 100) if total_lessons > 0 else 0
	
	# Статистика по оценкам
	graded_attendances = attendances.filter(mark__isnull=False)
	total_grades = graded_attendances.count()
	average_grade = graded_attendances.aggregate(avg_mark=Avg('mark'))['avg_mark'] or 0
	
	# Распределение оценок для диаграммы
	grade_distribution = {}
	for i in range(0, 11):  # Оценки от 0 до 10
		count = graded_attendances.filter(mark=i).count()
		if count > 0:
			grade_distribution[str(i)] = count
	
	# Статистика по предметам
	subjects_stats = {}
	for attendance in attendances:
		subject_name = attendance.lesson.study_group.subject.name
		if subject_name not in subjects_stats:
			subjects_stats[subject_name] = {
				'total_lessons': 0,
				'present': 0,
				'grades': [],
				'avg_grade': 0
			}
		
		subjects_stats[subject_name]['total_lessons'] += 1
		if attendance.attendance_status == 'PR':
			subjects_stats[subject_name]['present'] += 1
		if attendance.mark is not None:
			subjects_stats[subject_name]['grades'].append(attendance.mark)
	
	# Вычисляем средние оценки по предметам
	for subject in subjects_stats:
		grades = subjects_stats[subject]['grades']
		if grades:
			subjects_stats[subject]['avg_grade'] = sum(grades) / len(grades)
		subjects_stats[subject]['attendance_rate'] = (
			subjects_stats[subject]['present'] / subjects_stats[subject]['total_lessons'] * 100
			if subjects_stats[subject]['total_lessons'] > 0 else 0
		)
	
	# Данные для графика динамики оценок (последние 10 уроков с оценками)
	recent_grades = graded_attendances.order_by('-lesson__date')[:10]
	grade_timeline = []
	for attendance in reversed(recent_grades):
		grade_timeline.append({
			'date': attendance.lesson.date.strftime('%d.%m'),
			'grade': attendance.mark,
			'subject': attendance.lesson.study_group.subject.name
		})
	
	# Статистика выполнения домашних заданий
	homework_completed_count = attendances.filter(homework_completed=True).count()
	homework_not_completed_count = attendances.filter(homework_completed=False).count()
	homework_total_count = attendances.filter(homework_completed__isnull=False).count()
	
	homework_stats = {
		'completed': homework_completed_count,
		'not_completed': homework_not_completed_count,
		'total': homework_total_count,
		'completion_rate': (homework_completed_count / homework_total_count * 100) if homework_total_count > 0 else 0
	}
	
	# Статистика по тестированиям
	quiz_stats = {
		'total_attempts': 0,
		'subjects_tested': 0,
		'average_score': 0,
		'best_score': 0,
		'recent_tests': [],
		'subjects_performance': {}
	}
	
	# Получаем все попытки тестирования студента
	user_attempts = UserAnswer.objects.filter(user=student).values_list('attempt_number', 'question__quiz_subject_id').distinct()
	
	if user_attempts:
		quiz_stats['total_attempts'] = len(user_attempts)
		
		# Статистика по каждой попытке
		attempt_scores = []
		subjects_tested = set()
		recent_tests_data = []
		
		for attempt_number, quiz_subject_id in user_attempts:
			# Получаем ответы для этой попытки
			attempt_answers = UserAnswer.objects.filter(
				user=student, 
				attempt_number=attempt_number,
				question__quiz_subject_id=quiz_subject_id
			)
			
			if attempt_answers.exists():
				total_questions = attempt_answers.count()
				correct_answers = attempt_answers.filter(answer__is_correct=True).count()
				score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
				
				attempt_scores.append(score_percentage)
				subjects_tested.add(quiz_subject_id)
				
				# Получаем информацию о предмете
				try:
					quiz_subject = QuizSubject.objects.get(id=quiz_subject_id)
					subject_name = f"{quiz_subject.name} ({quiz_subject.get_language_display()})"
					
					# Добавляем в статистику по предметам
					if subject_name not in quiz_stats['subjects_performance']:
						quiz_stats['subjects_performance'][subject_name] = []
					quiz_stats['subjects_performance'][subject_name].append(score_percentage)
					
					# Добавляем в последние тесты
					recent_tests_data.append({
						'subject': subject_name,
						'score': score_percentage,
						'correct': correct_answers,
						'total': total_questions,
						'attempt': attempt_number
					})
				except QuizSubject.DoesNotExist:
					pass
		
		# Вычисляем общую статистику
		if attempt_scores:
			quiz_stats['average_score'] = sum(attempt_scores) / len(attempt_scores)
			quiz_stats['best_score'] = max(attempt_scores)
			quiz_stats['subjects_tested'] = len(subjects_tested)
			
			# Сортируем последние тесты и берем 5 последних
			quiz_stats['recent_tests'] = sorted(recent_tests_data, key=lambda x: x['attempt'], reverse=True)[:5]
			
			# Вычисляем средние баллы по предметам
			for subject, scores in quiz_stats['subjects_performance'].items():
				quiz_stats['subjects_performance'][subject] = {
					'average': sum(scores) / len(scores),
					'best': max(scores),
					'attempts': len(scores),
					'scores': scores
				}
	
	# Подготовка данных для JSON (для диаграмм)
	chart_data = {
		'attendance': {
			'present': present_count,
			'absent_with_reason': absent_with_reason,
			'absent_without_reason': absent_without_reason
		},
		'grades': grade_distribution,
		'subjects': subjects_stats,
		'grade_timeline': grade_timeline,
		'homework': homework_stats,
		'quiz_performance': quiz_stats['subjects_performance']
	}
	
	context = {
		'student': student,
		'student_groups': student_groups,
		'selected_period': selected_period,
		'start_date': str(start_date),
		'end_date': str(end_date),
		'choosen_range': choosen_range,
		'total_lessons': total_lessons,
		'present_count': present_count,
		'absent_with_reason': absent_with_reason,
		'absent_without_reason': absent_without_reason,
		'attendance_percentage': round(attendance_percentage, 1),
		'total_grades': total_grades,
		'average_grade': round(average_grade, 2),
		'grade_distribution': grade_distribution,
		'subjects_stats': subjects_stats,
		'homework_stats': homework_stats,
		'quiz_stats': quiz_stats,
		'chart_data': json.dumps(chart_data),
		'is_admin': is_admin,
		'is_teacher': is_teacher,
		'is_student': is_student,
	}
	
	return render(request, 'student_profile.html', context)