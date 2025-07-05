from django.db import models
from users.models import CustomUser
import json

LANG_CHOICES = (
	("RUS", "Русский"),
	("KAZ", "Казахский"),
)


def get_lang_choices(key):
	for k, v in LANG_CHOICES:
		if k == key:
			return v
	return None  


class OpenQuizSubject(models.Model):
	class Meta:
		verbose_name = "Предмет теста (свободное тесирование)"
		verbose_name_plural = "Предметы тестов (свободное тесирование)"
	
	name = models.CharField(max_length=255, verbose_name='Название')
	language = models.CharField(max_length=9, choices=LANG_CHOICES, default='RUS', verbose_name='Язык')
	time_limit_minutes = models.IntegerField(default=10, verbose_name='Лимит времени')
	
	def __str__(self):
		return self.name + '-' + get_lang_choices(self.language)


class OpenQuestion(models.Model):
	class Meta:
		verbose_name = "Тестовый вопрос (cвободное тестирование)"
		verbose_name_plural = "Вопросы тестов (cвободное тестирование)"
	text = models.TextField()
	image = models.ImageField(upload_to='question_images/', null=True, blank=True)
	quiz_subject = models.ForeignKey(OpenQuizSubject, on_delete=models.CASCADE)
	correct_answer = models.TextField(verbose_name='Правильный ответ')
	weight = models.SmallIntegerField(verbose_name='Баллы', default=1)

	def __str__(self):
		return self.text

class OpenUserAnswer(models.Model):
	class Meta:
		verbose_name = "Ответы пользователей (свободное тестирование)"
		verbose_name_plural = "Ответы пользователей (свободное тестирование)"
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	question = models.ForeignKey(OpenQuestion, on_delete=models.CASCADE)
	answer_text = models.TextField()
	attempt_number = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f"User: {self.user.username}, Question: {self.question.text}, Answer: {self.answer_text}, Attempt: {self.attempt_number}"


class OpenExcelFile(models.Model):
	class Meta:
		verbose_name = "Файл Excel (свободное тестирование)"
		verbose_name_plural = "Файлы Excel (свободное тестирование)"
	file = models.FileField(upload_to='open_excel_files/')
	uploaded_at = models.DateTimeField(auto_now_add=True)
	quiz_subject = models.ForeignKey(OpenQuizSubject, on_delete=models.CASCADE)

	def __str__(self):
		return f"Файл {self.id} загружен в {self.uploaded_at}"


class OpenTestProgress(models.Model):
	class Meta:
		verbose_name = "Прогресс теста (свободное тестирование)"
		verbose_name_plural = "Прогресс тестов (свободное тестирование)"
		
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	quiz_subject = models.ForeignKey(OpenQuizSubject, on_delete=models.CASCADE)
	remaining_seconds = models.IntegerField(default=0, verbose_name='Оставшееся время в секундах')
	start_time = models.DateTimeField(auto_now_add=True)
	last_update = models.DateTimeField(auto_now=True)
	
	# Сохраняем вопросы в виде JSON, чтобы использовать те же вопросы при продолжении
	question_ids = models.TextField(default='[]', help_text='JSON массив с ID выбранных вопросов')
	current_question_index = models.IntegerField(default=0, verbose_name='Текущий вопрос')
	
	# Временно сохраненные ответы (до финальной отправки)
	temp_answers = models.TextField(default='{}', help_text='JSON объект с временными ответами {question_id: answer_text}')
	
	is_completed = models.BooleanField(default=False, verbose_name='Тест завершен')
	
	def get_question_ids(self):
		"""Получить список ID вопросов"""
		try:
			return json.loads(self.question_ids)
		except:
			return []
	
	def set_question_ids(self, ids_list):
		"""Сохранить список ID вопросов"""
		self.question_ids = json.dumps(ids_list)
		
	def get_temp_answers(self):
		"""Получить временные ответы"""
		try:
			return json.loads(self.temp_answers)
		except:
			return {}
	
	def set_temp_answers(self, answers_dict):
		"""Сохранить временные ответы"""
		self.temp_answers = json.dumps(answers_dict)
	
	def __str__(self):
		return f"Прогресс теста: {self.user.username} - {self.quiz_subject.name} - {'Завершен' if self.is_completed else 'В процессе'}"