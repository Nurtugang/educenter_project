from django.db import models
from users.models import CustomUser
LANG_CHOICES = (
	("RUS", "Русский"),
	("KAZ", "Казахский"),
)

def get_lang_choices(key):
    for k, v in LANG_CHOICES:
        if k == key:
            return v
    return None  

class QuizSubject(models.Model):
	class Meta:
		verbose_name = "Предмет теста"
		verbose_name_plural = "Предметы тестов"
	
	name = models.CharField(max_length=255, verbose_name='Название предмета')
	language = models.CharField(max_length=9, choices=LANG_CHOICES, default='RUS', verbose_name='Язык теста')
	time_limit_minutes = models.IntegerField(default=10, verbose_name='Время на тест (минуты)')
	shuffle_options = models.BooleanField(default=True, verbose_name='Перемешать варианты ответов')
	
	def __str__(self):
		return self.name + '-' + get_lang_choices(self.language)


class ExcelFile(models.Model):
	class Meta:
		verbose_name = "Файл Excel"
		verbose_name_plural = "Файлы Excel"
	file = models.FileField(upload_to='excel_files/', verbose_name='Файл Excel с контентом тестирования')
	uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
	quiz_subject = models.ForeignKey(QuizSubject, on_delete=models.CASCADE, verbose_name='Предмет теста')

	def __str__(self):
		return f"Файл {self.id} загружен в {self.uploaded_at}"



class Question(models.Model):
	class Meta:
		verbose_name = "Тестовый вопрос"
		verbose_name_plural = "Вопросы тестов"
	text = models.TextField()
	image = models.ImageField(upload_to='question_images/', null=True, blank=True)
	quiz_subject = models.ForeignKey(QuizSubject, on_delete=models.CASCADE)

	def __str__(self):
		return self.text

class AnswerOption(models.Model):
	class Meta:
		verbose_name = "Вариант ответа"
		verbose_name_plural = "Варианты ответов"
	question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
	text = models.CharField(max_length=255)
	is_correct = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.question.text[:20]} - {self.text}"


class UserAnswer(models.Model):
	class Meta:
		verbose_name = "Ответы пользователей"
		verbose_name_plural = "Ответы пользователей"
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	answer = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)
	attempt_number = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f"User: {self.user.username}, Question: {self.question.text}, Answer: {self.answer.text}, Attempt: {self.attempt_number}"