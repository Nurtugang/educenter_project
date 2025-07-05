from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.db.models import Q
from eduapp.forms import CourseRequestForm, TargetForm, SystemFeedbackForm
from eduapp.models import TargetModel, VideoCourse, Subscription, VideoLesson, CourseRequest, Feedback, SystemFeedback
from django.core.paginator import Paginator
from datetime import timedelta
from django.contrib import messages
from django.db.models import Avg
from . import amo_functions as amo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def feedback_ajax(request):
    if request.method == 'POST' and request.user.is_authenticated:
        category = request.POST.get('category')
        message = request.POST.get('message')
        if message:
            SystemFeedback.objects.create(user=request.user, category=category, message=message)
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


def index(request):
	vc = VideoCourse.objects.all().select_related('teacher').order_by('id')
	context = {
		'courses': vc,
		'page_name': 'index',
	}
	return render(request, 'index.html', context)

def contact(request):
	if request.method == 'POST':
		form = CourseRequestForm(request.POST)
		if form.is_valid():
			messages.success(request, 'Ваша заявка успешно отправлена.')
			name = form.cleaned_data['name']
			email = form.cleaned_data['email']
			phone = form.cleaned_data['phone']
			subject = form.cleaned_data['subject']
			message = form.cleaned_data['message']

			CourseRequest.objects.create(name=name, email=email, phone=phone, subject=subject, message=message)
		else:
			messages.error(request, 'Ваша заявка не отправлена.')
		redirect('contact')

	else:
		form = CourseRequestForm()

	context = {
		'form': form,
		'page_name': 'contact',
	}
	return render(request, 'contact.html', context)


def elessons(request):
	if request.user.is_authenticated:
		if request.user.groups.all()[0] == Group.objects.get(name='Преподаватель'): #если это препод
			courses = VideoCourse.objects.filter(teacher=request.user, is_target_course=False)
		elif request.user.groups.all()[0] == Group.objects.get(name='Администратор'): #если это админ
			courses = VideoCourse.objects.filter(is_target_course=False)
		else:
			courses = VideoCourse.objects.filter(grade=request.user.grade, is_target_course=False)
	else:
		courses = VideoCourse.objects.filter(is_target_course=False)

	paginate_by = 6
	paginator = Paginator(courses, paginate_by)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	context = {
		'courses': courses.select_related('teacher'),
		'page_obj': page_obj,
		'paginate_by': paginate_by,
		'page_name': 'elessons',
	}

	return render(request, 'elessons.html', context)


def videolessons(request, courseid): 
	# Получаем курс
	course = VideoCourse.objects.get(id=courseid)
	lessons = VideoLesson.objects.filter(course=course)

	# Проверка доступов (подписка, админ)
	is_auth = request.user.is_authenticated 
	is_subscribed = is_admin = is_teacher_of_this_course = False
	if is_auth:
		is_subscribed = Subscription.objects.filter(course=course, student=request.user).exists()
		is_admin = request.user.groups.filter(name__in=['Администратор']).exists()
		is_teacher_of_this_course = VideoCourse.objects.get(id=courseid).teacher == request.user
	
	# Отзывы курсов
	course_feedbacks = Feedback.objects.filter(course=course)
	feedbacks_int = int(course_feedbacks.aggregate(average_rating=Avg('rating'))['average_rating'] or 0)

	if request.method == 'POST' and is_auth and 'rating' in request.POST:
		rating = request.POST.get('rating')
		comment = request.POST.get('comment')
		has_rated_course = Feedback.objects.filter(user=request.user, course = course).exists()
		if (is_subscribed or is_admin) and not has_rated_course:
			Feedback.objects.create(user=request.user, course = course, comment=comment, rating=rating)
			messages.success(request, "Спасибо за оставленный отзыв!")
			return redirect('videolessons', courseid=courseid)
		elif has_rated_course:
			messages.error(request, "Вы уже оставляли отзыв!")
			return redirect('videolessons', courseid=courseid)
		else:
			messages.error(request, "Вы не можете оставить отзыв!")
			return redirect('videolessons', courseid=courseid)
	
	#Доступен ли курс пользователю
	is_available = is_subscribed or is_admin or is_teacher_of_this_course

	#Длина курса
	dur_total = timedelta(0)
	for l in lessons:
		dur_total += l.dur_rus

	# Извлекаем часы и минуты из total_seconds()
	total_seconds = int(dur_total.total_seconds())
	hours = total_seconds // 3600
	minutes = (total_seconds % 3600) // 60

	# Форматируем строку
	if hours == 0:
		duration_total = f"{minutes} мин"
	else:
		duration_total = f"{hours} ч. {minutes} мин"


	context = {
		'page_name': 'videolessons',
		'course': course,
		'subs_count': Subscription.objects.filter(course=course).count(),
		'teacher': course.teacher,
		'lessons': lessons,
		'others': VideoCourse.objects.filter(~Q(semester=course.semester), name=course.name, grade=course.grade),
		'others2': VideoCourse.objects.filter(~Q(name=course.name), grade=course.grade, semester=course.semester),
		'duration_total': duration_total,
		'is_available': is_available,
		'courseid': courseid,
		'course_feedbacks': course_feedbacks,
		'feedbacks_int': feedbacks_int,
	}
	return render(request, 'videolessons.html', context)


#таргет

def vidaccess(request):
	# Время таймера — 9 минут
	timer_duration = 9 * 60  # 9 минут в секундах

	# Получаем доступ к таргет-курсу
	vc = VideoCourse.objects.filter(is_target_course=True)[0]
	courseid = vc.id
	AVAILABLE_COURSES_COUNT = 17
	lessons = VideoLesson.objects.filter(course=vc)[:AVAILABLE_COURSES_COUNT]

	# Проверяем, существует ли уже таймер в сессии
	if 'timer_start' not in request.session:
		# Если нет, устанавливаем начальное время таймера
		request.session['timer_start'] = timezone.now().timestamp()
		request.session.modified = True

	# Получаем текущее время и время старта таймера
	current_time = timezone.now().timestamp()
	timer_start = request.session['timer_start']

	# Вычисляем, сколько времени осталось
	elapsed_time = current_time - timer_start
	remaining_time = max(0, timer_duration - elapsed_time)

	# Обработка формы для таргетированных пользователей
	form = None
	if request.method == 'POST' and 'name' in request.POST and 'phone' in request.POST:
		form = TargetForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			phone = form.cleaned_data['phone']

			if TargetModel.objects.filter(phone=phone).exists():
				messages.error(request, 'Этот номер телефона уже зарегистрирован!')
			else:
				# Сохраняем данные в модель TargetModel
				TargetModel.objects.create(
					name=form.cleaned_data['name'],
					phone=form.cleaned_data['phone'],
				)

				# Интеграция с amoCRM
				new_contact = amo.create_contact(name, phone)
				pipeline_id = amo.get_pipeline_id()
				_ = amo.create_lead(pipeline_id, new_contact)

				# Устанавливаем флаг в сессии, что пользователь получил доступ к видео
				request.session['has_access'] = True
		
				messages.success(request, "Отлично! Вы получили доступ к 17 бесплатным видео.")
				
				# Сбрасываем таймер при успешной регистрации
				request.session.pop('timer_start', None)

				return redirect('videocourses', courseid=courseid)
		else:
			messages.error(request, "Ошибка при отправке данных. Попробуйте еще раз.")
	else:
		form = TargetForm()

	context = {
		'form': form,  # Форма для таргета
		'lessons': lessons,  # Уроки курса
		'remaining_time': remaining_time  # Оставшееся время таймера
 	}

	return render(request, 'vidaccess.html', context)


def videocourses(request, courseid): 
	if not request.session.get('has_access', False):
		# Если доступа нет, перенаправляем на страницу с формой
		messages.error(request, "У вас нет доступа к видео. Пожалуйста, заполните форму для получения доступа.")
		return redirect('vidaccess')
	
	timer_duration = 4 * 24 * 60 * 60

	# Проверяем, существует ли уже таймер в сессии
	if 'timer_start' not in request.session:
		# Если нет, устанавливаем начальное время таймера
		request.session['timer_start'] = timezone.now().timestamp()
		request.session.modified = True

	# Получаем текущее время и время старта таймера
	current_time = timezone.now().timestamp()
	timer_start = request.session['timer_start']

	# Вычисляем, сколько времени осталось
	elapsed_time = current_time - timer_start
	remaining_time = max(0, timer_duration - elapsed_time)

	# Получаем курс и убеждаемся, что он таргетированный
	course = VideoCourse.objects.get(id=courseid)
	if not course.is_target_course:
		messages.error(request, "Этот курс недоступен в данной категории.")
		return redirect('elessons')

	AVAILABLE_COURSES_COUNT = 17
	# Если курс таргетированный, показываем первые 2 урока, остальные блокируем
	lessons = VideoLesson.objects.filter(course=course)
	for i, lesson in enumerate(lessons):
		# Первые два урока доступны, остальные блокируем
		lesson.is_locked = i >= AVAILABLE_COURSES_COUNT

	
	# Обработка формы для таргетированных пользователей
	form = None
	if request.method == 'POST' and 'name' in request.POST and 'phone' in request.POST:
		form = TargetForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			phone = form.cleaned_data['phone']

			# Сохраняем данные в модель TargetModel
			TargetModel.objects.create(
				name=form.cleaned_data['name'],
				phone=form.cleaned_data['phone'],
			)

			new_contact = amo.create_contact(name, phone) 
			pipeline_id = amo.get_pipeline_id()
			_ = amo.create_lead(pipeline_id, new_contact)
			messages.success(request, "Спасибо! Мы свяжемся с вами.")
			return redirect('videocourses', courseid=courseid)
		else:
			messages.error(request, "Ошибка при отправке данных. Попробуйте еще раз.")
	else:
		form = TargetForm()

	#Длина курса
	dur_total = timedelta(0)
	for l in lessons:
		dur_total += l.dur_rus

	dur_total = str(dur_total)
	minutes = dur_total[dur_total.find(':')+1:dur_total.find(':')+3]
	hours = dur_total[:dur_total.find(':')]
	duration_total = ''
	if hours == '0':
		duration_total = minutes + ' мин'
	else:
		duration_total = hours + ' ч. ' + minutes + ' мин'


	context = {
		'page_name': 'videolessons',
		'course': course,
		'subs_count': Subscription.objects.filter(course=course).count(),
		'teacher': course.teacher,
		'lessons': lessons,
		'duration_total': duration_total,
		'courseid': courseid,
		'form': form, # Форма для таргета
		'AVAILABLE_COURSES_COUNT': AVAILABLE_COURSES_COUNT,
		'remaining_time': remaining_time
	}
	return render(request, 'videocourses.html', context)