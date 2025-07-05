from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import ExcelFile, Question, UserAnswer, AnswerOption, QuizSubject
import pandas as pd
import os
import re


@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
	list_display = ['uploaded_at', 'file', 'quiz_subject']

	def save_model(self, request, obj, form, change):
		_, file_extension = os.path.splitext(obj.file.name)

		# Проверяем, что это Excel файл
		if file_extension not in ['.xls', '.xlsx']:
			raise ValidationError("Неверный формат файла. Требуется файл Excel (.xls или .xlsx).")
		super().save_model(request, obj, form, change)

		df = pd.read_excel(obj.file)
		for index, row in df.iterrows():
			# Создаем вопрос
			question_text = str(row['Вопрос']).replace('\r', ' ').replace('\n', ' ')
			question = Question.objects.create(text=question_text, quiz_subject=obj.quiz_subject)

			# Первый вариант ответа всегда правильный
			correct_answer_text = row['Правильный']
			AnswerOption.objects.create(question=question, text=correct_answer_text, is_correct=True)

			# Добавляем остальные варианты ответов, на случай если их 3 (общий 4)
			# for option in ['Вариант2', 'Вариант3', 'Вариант4']:
			# 	option_text = row[option]
			# 	AnswerOption.objects.create(question=question, text=option_text, is_correct=False)

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
    search_fields = ['question__text', 'answer__text']

@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    search_fields = ['text', 'question__text']

admin.site.register(Question)
admin.site.register(QuizSubject)