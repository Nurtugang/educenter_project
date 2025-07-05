from django.contrib import admin
from .models import OpenQuestion, OpenUserAnswer, OpenQuizSubject, OpenExcelFile
from django.contrib import admin
from django.core.exceptions import ValidationError
import pandas as pd
import os

@admin.register(OpenExcelFile)
class OpenExcelFileAdmin(admin.ModelAdmin):
	list_display = ['uploaded_at', 'file', 'quiz_subject']

	def save_model(self, request, obj, form, change):
		_, file_extension = os.path.splitext(obj.file.name)

		# Проверяем, что это Excel файл
		if file_extension not in ['.xls', '.xlsx']:
			raise ValidationError("Неверный формат файла. Требуется файл Excel (.xls или .xlsx).")
		super().save_model(request, obj, form, change)

		df = pd.read_excel(obj.file)
		for index, row in df.iterrows():
			OpenQuestion.objects.create(text=str(row['Вопрос']).replace('\r', ' ').replace('\n', ' '), 
                               			correct_answer=row['Правильный'], 
                               			quiz_subject=obj.quiz_subject, 
                               			weight=row['Баллы'])

@admin.register(OpenUserAnswer)
class OpenUserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer_text', 'attempt_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

admin.site.register(OpenQuestion)
admin.site.register(OpenQuizSubject)