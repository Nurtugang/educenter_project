from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, validate_email, MaxLengthValidator, RegexValidator
from users.models import CustomUser
from django.db.models import Avg

from datetime import timedelta

class SystemFeedback(models.Model):
	class Meta:
		verbose_name = "Пожелание по улучшению системы"
		verbose_name_plural = "Пожелания по улучшению системы"
	CATEGORY_CHOICES = [
		('idea', 'Идея'),
		('bug', 'Ошибка'),
		('question', 'Вопрос'),
		('other', 'Другое'),
	]

	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
	message = models.TextField(verbose_name="Сообщение")
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.user} ({self.category}) – {self.created_at.strftime('%Y-%m-%d')}"
	
class Student(models.Model):
	class Meta:
		verbose_name = "Студент"
		verbose_name_plural = "Студенты"

	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
	grade = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
	def __str__(self):
		return self.user.username
	def full_name(self):
		return f"{self.user.first_name} {self.user.last_name}"
	def email(self):
		return self.user.email

class VideoLesson(models.Model):
	class Meta:
		verbose_name = "Видеоурок"
		verbose_name_plural = "Видеоуроки"

	name = models.CharField(max_length=255)
	course = models.ForeignKey('VideoCourse', on_delete=models.CASCADE)
	link_rus = models.CharField(max_length=255)
	dur_rus = models.DurationField(default=timedelta(minutes=10, seconds=0))
	link_kaz = models.CharField(max_length=255) 
	dur_kaz = models.DurationField(default=timedelta(minutes=10, seconds=0))

	def __str__(self):
		return self.name


SEMESTERS = (
		('1', '1'),
		('2', '2'),
		('3', '3'),
		('4', '4'),
	)

class VideoCourse(models.Model):
	class Meta:
		verbose_name = "Видеокурс"
		verbose_name_plural = "Видеокурсы"

	subject = models.CharField(max_length=255, verbose_name='Название курса')
	name = models.CharField(max_length=255, verbose_name='Предмет')
	description = models.TextField(default='Нет описания')
	teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	grade = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(12)])
	semester = models.CharField(max_length=1, choices=SEMESTERS, default='1')
	price = models.PositiveIntegerField(default=10000, validators=[MinValueValidator(0), MaxValueValidator(1000000)])
	image = models.ImageField(default='cu-1.webp', upload_to='courses', verbose_name='Фото')
	is_target_course = models.BooleanField(default=False)  # Курс для таргетированной рекламы
	def __str__(self):
		return self.name + '(' + str(self.grade) + ' класс, ' + str(self.semester) + ' четверть)'


class RegularVideoCourse(VideoCourse):
	class Meta:
		proxy = True
		verbose_name = "Обычный видеокурс"
		verbose_name_plural = "Обычные видеокурсы"

class TargetVideoCourse(VideoCourse):
	class Meta:
		proxy = True
		verbose_name = "Курс для таргета"
		verbose_name_plural = "Курсы для таргета"


class Subscription(models.Model):
	class Meta:
		verbose_name = "Подписка"
		verbose_name_plural = "Подписки"

	student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	course = models.ForeignKey(VideoCourse, on_delete=models.CASCADE)

	def __str__(self):
		return self.student.username + '|' + self.course.name

RATINGS = (
	('1', '1'),
	('2', '2'),
	('3', '3'),
	('4', '4'),
	('5', '5'),
)
class Feedback(models.Model):
	class Meta:
		verbose_name = "Отзыв"
		verbose_name_plural = "Отзывы"

	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	course = models.ForeignKey(VideoCourse, on_delete=models.CASCADE)
	comment = models.TextField()
	rating = models.CharField(max_length=1, choices=RATINGS)
	def __str__(self):
		return self.user.username + '|' + self.course.name
	def get_avg_rating(self, course):
		course_feedbacks = Feedback.objects.filter(course=course)		
		total_ratings = course_feedbacks.aggregate(avg_rating=models.Avg('rating'))
		return total_ratings['avg_rating'] or 0


class CourseRequest(models.Model):
	class Meta:
		verbose_name = "Заявка"
		verbose_name_plural = "Заявки"

	name = models.CharField(max_length=255)
	email = models.EmailField(default='', validators=[validate_email, MaxLengthValidator(limit_value=100)])
	phone_regex = RegexValidator(
		regex=r'^[\d()+]+$',
		message="Телефонный номер может содержать только числа, символы '(', ')', и '+'."
	)
	phone = models.CharField(
		max_length=20,
		validators=[phone_regex]
	)
	subject = models.CharField(max_length=255)
	message = models.TextField(default='')
	
	def __str__(self):
		return self.name + '|' + self.subject

class TargetModel(models.Model):
	class Meta:
		verbose_name = "Таргет"
		verbose_name_plural = "Таргет"

	name = models.CharField(max_length=255, verbose_name='Имя')
	phone = models.CharField(
		max_length=20,
		verbose_name='Телефон',
	)
	def __str__(self):
		return self.name + '|' + self.phone