from django.contrib import admin
from .models import *
from .forms import *
from datetime import datetime, time, timedelta
from rangefilter.filters import DateRangeFilterBuilder

from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import HttpResponseRedirect


def view_student_attendance(self, request, queryset):
	# Redirect to the StudentAttendance view for the selected StudyGroup
	url = reverse('admin:eduprocesses_studentattendance_changelist')
	lesson = queryset.first()
	if lesson:
		url += f'?lesson__id={lesson.id}'
	return HttpResponseRedirect(url)
	
class LessonAdmin(admin.ModelAdmin):
	def get_custom_date(self, obj):
		return obj.date.strftime('%d/%m/%Y')
	get_custom_date.short_description = 'Дата'

	def get_fieldsets(self, request, obj=None):
		if obj:  # Detail view or change view
			fieldsets = [
				(None, {'fields': ('study_group', 'status',
				'reason_for_not_held', 'substitute_teacher', 'date', 'hours', 'deadline', 'homework', 'max_grade')}),
			]
		else:   # Add view
			fieldsets = [
				(None, {'fields': ('study_group', 'date')}),  # Только основные поля, остальное в виджете
			]
		return fieldsets

	list_display = ('get_custom_date', 'date', 'status', 'hours', )
	list_editable = ('hours', )
	list_filter = (('date', DateRangeFilterBuilder()), 'study_group__group_type', 'study_group__subject', 'status',)
	search_fields = ['study_group__name']
	
	view_student_attendance.short_description = "Посмотреть оценки"
	actions = [view_student_attendance]
	
	def get_action_choices(self, request):
		choices = super(LessonAdmin, self).get_action_choices(request)
		choices.pop(0)
		choices.reverse()
		return choices

	def get_form(self, request, obj=None, **kwargs):
		if obj is None:
			kwargs['form'] = LessonAdminForm
		return super().get_form(request, obj, **kwargs)

	def save_model(self, request, obj, form, change):
		if not change:
			# Получаем выбранные даты из скрытого поля
			selected_dates_str = form.cleaned_data.get('tmp', '')
			
			if selected_dates_str and selected_dates_str != 'hidden_field_value':
				selected_dates = selected_dates_str.split(',')
			else:
				selected_dates = []
			
			# Основные параметры урока
			study_group = form.cleaned_data['study_group']
			quarter = form.cleaned_data.get('quarter', '1')
			substitute_teacher = form.cleaned_data.get('substitute_teacher')
			reason_for_not_held = form.cleaned_data.get('reason_for_not_held')
			status = form.cleaned_data.get('status', 'NP')
			hours = form.cleaned_data.get('hours', 1)
			
			if selected_dates:
				# Создаем уроки для всех выбранных дат
				for selected_date in selected_dates:
					try:
						# Вычисляем дедлайн (48 часов после даты урока)
						lesson_date = datetime.strptime(selected_date.strip(), '%Y-%m-%d').date()
						deadline = datetime.combine(lesson_date, time(0, 0)) + timedelta(hours=48)
						
						# Создаем урок
						Lesson.objects.create(
							date=lesson_date,
							study_group=study_group,
							quarter=quarter,
							substitute_teacher=substitute_teacher,
							reason_for_not_held=reason_for_not_held,
							status=status,
							hours=hours,
							deadline=deadline
						)
					except ValueError as e:
						# Логируем ошибку парсинга даты
						print(f"Ошибка парсинга даты {selected_date}: {e}")
						continue
			else:
				# Если даты не выбраны, показываем ошибку
				from django.contrib import messages
				messages.error(request, 'Пожалуйста, выберите даты для создания уроков')
				return
		else:
			# Для существующих объектов используем стандартное сохранение
			super().save_model(request, obj, form, change)

class HalfYear1(Lesson):
	class Meta:
		proxy = True
		verbose_name = 'Урок первого полугодия'
		verbose_name_plural = 'Уpоки первого полугодия'

	def save(self, *args, **kwargs):
		if not self.pk:  
			super().save(*args, **kwargs) 
			self.quarter.set('1')
		else:
			super().save(*args, **kwargs)
   

class HalfYear2(Lesson):
	class Meta:
		proxy = True
		verbose_name = 'Урок второго полугодия'
		verbose_name_plural = 'Уроки второго полугодия'

	def save(self, *args, **kwargs):
		if not self.pk:  
			super().save(*args, **kwargs) 
			self.quarter.set('3')
		else:
			super().save(*args, **kwargs)
   

# Базовый класс для семестров
class HalfYearAdminBase(LessonAdmin):
	def get_custom_date(self, obj):
		return obj.__str__() 
	get_custom_date.short_description = 'Урок' 
	
	list_display = ('get_custom_date', 'date', 'status', 'hours', 'deadline')
	list_editable = ('hours', )
	
	def get_form(self, request, obj=None, **kwargs):
		# Используем ту же форму что и для основного LessonAdmin
		if obj is None:
			kwargs['form'] = LessonAdminForm
		return super().get_form(request, obj, **kwargs)
	
	def save_model(self, request, obj, form, change):
		if not change:
			# Получаем выбранные даты из скрытого поля
			selected_dates_str = form.cleaned_data.get('tmp', '')
			
			if selected_dates_str and selected_dates_str != 'hidden_field_value':
				selected_dates = selected_dates_str.split(',')
			else:
				selected_dates = []
			
			# Основные параметры урока
			study_group = form.cleaned_data['study_group']
			quarter = self.get_quarter()  # Получаем номер четверти для конкретного семестра
			substitute_teacher = form.cleaned_data.get('substitute_teacher')
			reason_for_not_held = form.cleaned_data.get('reason_for_not_held')
			status = form.cleaned_data.get('status', 'NP')
			hours = form.cleaned_data.get('hours', 1)
			
			if selected_dates:
				# Создаем уроки для всех выбранных дат
				for selected_date in selected_dates:
					try:
						# Вычисляем дедлайн (48 часов после даты урока)
						lesson_date = datetime.strptime(selected_date.strip(), '%Y-%m-%d').date()
						deadline = datetime.combine(lesson_date, time(0, 0)) + timedelta(hours=48)
						
						# Создаем урок с правильной четвертью
						Lesson.objects.create(
							date=lesson_date,
							study_group=study_group,
							quarter=quarter,
							substitute_teacher=substitute_teacher,
							reason_for_not_held=reason_for_not_held,
							status=status,
							hours=hours,
							deadline=deadline
						)
					except ValueError as e:
						# Логируем ошибку парсинга даты
						print(f"Ошибка парсинга даты {selected_date}: {e}")
						continue
			else:
				# Если даты не выбраны, показываем ошибку
				from django.contrib import messages
				messages.error(request, 'Пожалуйста, выберите даты для создания уроков')
				return
		else:
			# Для существующих объектов используем стандартное сохранение
			super().save_model(request, obj, form, change)
	
	def get_quarter(self):
		"""Переопределяется в каждом дочернем классе"""
		return '1'


class HalfYear1Admin(HalfYearAdminBase):
	def get_quarter(self):
		return '1'
		
	def get_queryset(self, request):
		return self.model.objects.filter(quarter='1')


class HalfYear2Admin(HalfYearAdminBase):
	def get_quarter(self):
		return '2'
		
	def get_queryset(self, request):
		return self.model.objects.filter(quarter='2')

admin.site.register(HalfYear1, HalfYear1Admin)
admin.site.register(HalfYear2, HalfYear2Admin)

class TeacherFilter(admin.SimpleListFilter):
	title = 'Преподаватель'
	parameter_name = 'teacher'

	def lookups(self, request, model_admin):
		# Получаем список уникальных идентификаторов пользователей из группы "Преподаватель"
		teacher_ids = CustomUser.objects.filter(groups__name='Преподаватель').values_list('id', flat=True).distinct()
		# Получаем имена и фамилии преподавателей
		teachers = CustomUser.objects.filter(id__in=teacher_ids)
		return [(str(teacher.id), f'{teacher.first_name} {teacher.last_name}') for teacher in teachers]

	def queryset(self, request, queryset):
		if self.value():
			return queryset.filter(teacher__id=self.value())
			
			
class StudyGroupAdmin(admin.ModelAdmin):
	form = StudyGroupAdminForm
	filter_horizontal = ('students',)
	search_fields = ['name', 'teacher__username', 'subject__name']
	list_display = ('name', 'group_type', 'teacher', 'subject')
	list_filter = ('group_type', 'subject', TeacherFilter)
	ordering = ('name',)



admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(StudyGroupType)
admin.site.register(Subject)

class StudentAttendanceAdmin(admin.ModelAdmin):
	def get_custom_date(self, obj):
		return obj.lesson.date.strftime('%d/%m/%Y')
	get_custom_date.short_description = 'Дата'  
	
	def get_subject_name(self, obj):
		return obj.lesson.study_group.subject.name if obj.lesson.study_group.subject else ''
	get_subject_name.short_description = 'Предмет' 
	
	def get_stgroup_name(self, obj):
		return obj.lesson.study_group.name if obj.lesson.study_group else ''
	get_stgroup_name.short_description = 'Группа' 
	
	def get_custom_quarter(self, obj):
		return obj.lesson.quarter
	get_custom_quarter.short_description = 'Полугодие'  
	
	list_display = ('student', 'lesson', 'attendance_status', 'mark', 'get_subject_name', 'get_custom_date', 'get_custom_quarter')
	list_filter = (('lesson__date', DateRangeFilterBuilder()), 'lesson__study_group', 'lesson__study_group__subject', 'lesson__quarter')


admin.site.register(StudentAttendance, StudentAttendanceAdmin)