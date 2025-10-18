from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import ExcelFile, Question, UserAnswer, AnswerOption, QuizSubject
import pandas as pd
import os
import re


@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
	list_display = ['id', 'uploaded_at', 'file', 'quiz_subject']
	list_filter = ['uploaded_at', 'quiz_subject']
	search_fields = ['quiz_subject__name']
	readonly_fields = ['uploaded_at']
	fieldsets = (
		('Информация о файле', {
			'fields': ('file', 'uploaded_at')
		}),
		('Связь с предметом', {
			'fields': ('quiz_subject',)
		}),
	)

	def save_model(self, request, obj, form, change):
		_, file_extension = os.path.splitext(obj.file.name)

		if file_extension not in ['.xls', '.xlsx']:
			raise ValidationError("Неверный формат файла. Требуется файл Excel (.xls или .xlsx).")
		super().save_model(request, obj, form, change)

		df = pd.read_excel(obj.file)
		for index, row in df.iterrows():
			question_text = str(row['Вопрос']).replace('\r', ' ').replace('\n', ' ')
			question = Question.objects.create(text=question_text, quiz_subject=obj.quiz_subject)

			# Первый вариант ответа всегда правильный
			correct_answer_text = row['Правильный']
			AnswerOption.objects.create(question=question, text=correct_answer_text, is_correct=True)

			# Находим все колонки с вариантами ответа, имена которых начинаются с "Вариант" и за которыми следует число
			option_columns = [col for col in df.columns if re.match(r'^Вариант\d+', col)]
   
			# Сортируем столбцы по числовой части, чтобы порядок вариантов был корректным
			option_columns.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))
			
			for col in option_columns:
				option_text = row[col]
				if pd.notna(option_text):
					AnswerOption.objects.create(question=question, text=option_text, is_correct=False)

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
	list_display = ['user_username', 'question_preview', 'answer_text', 'is_correct_answer', 'attempt_number']
	list_filter = ['attempt_number', 'question__quiz_subject', 'user']
	search_fields = ['question__text', 'answer__text', 'user__username']
	readonly_fields = ['user', 'question', 'answer', 'attempt_number']
	
	def user_username(self, obj):
		return obj.user.username
	user_username.short_description = 'Пользователь'
	
	def question_preview(self, obj):
		text = obj.question.text
		return text[:35] + '...' if len(text) > 35 else text
	question_preview.short_description = 'Вопрос'
	
	def answer_text(self, obj):
		return obj.answer.text
	answer_text.short_description = 'Ответ пользователя'
	
	def is_correct_answer(self, obj):
		return obj.answer.is_correct
	is_correct_answer.boolean = True
	is_correct_answer.short_description = 'Правильный ответ'
	
	def has_add_permission(self, request):
		return False

@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
	list_display = ['text', 'question_text', 'is_correct']
	list_filter = ['is_correct', 'question__quiz_subject']
	search_fields = ['text', 'question__text']
	list_editable = ['is_correct']
	
	def question_text(self, obj):
		return obj.question.text[:40] + '...' if len(obj.question.text) > 40 else obj.question.text
	question_text.short_description = 'Вопрос'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ['text_preview', 'quiz_subject', 'options_count']
	list_filter = ['quiz_subject']
	search_fields = ['text', 'quiz_subject__name']
	readonly_fields = ['options_count']
	
	def text_preview(self, obj):
		return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
	text_preview.short_description = 'Текст вопроса'
	
	def options_count(self, obj):
		return obj.options.count()
	options_count.short_description = 'Кол-во вариантов'


class AnswerOptionInline(admin.TabularInline):
	model = AnswerOption
	extra = 1
	fields = ['text', 'is_correct']
	
	
@admin.register(QuizSubject)
class QuizSubjectAdmin(admin.ModelAdmin):
	list_display = ['name', 'language', 'time_limit_minutes', 'shuffle_options']
	list_filter = ['language', 'time_limit_minutes']
	search_fields = ['name']
	fieldsets = (
		('Основная информация', {
			'fields': ('name', 'language')
		}),
		('Настройки теста', {
			'fields': ('time_limit_minutes', 'shuffle_options')
		}),
	)