from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.utils import timezone

GENDERS = (
	('M', 'Мужчина'),
	('W', 'Женщина')
)
	
TEACHER_STATUS_CHOICES = (
	('ML1', 'Младший тренер 1'),
	('ML2', 'Младший тренер 2'),
	('ST1', 'Старший тренер 1'),
	('ST2', 'Старший тренер 2'),
	('V', 'Высший тренер')
)

class CustomUser(AbstractUser):
	class Meta:
		verbose_name = "Пользователь"
		verbose_name_plural = "Все пользователи"

	first_name = models.CharField('Имя', max_length=20, default='')
	last_name = models.CharField('Фамилия', max_length=20, default='')
	middle_name = models.CharField('Отчество', max_length=20, blank=True)
	birth_date = models.DateField('Дата рождения', default='2000-01-01')
	phone = models.CharField('Телефон', max_length=20, blank=True)
	gender = models.CharField('Пол', max_length=1, choices=GENDERS, blank=True)
	image = models.ImageField(default='default.webp', upload_to='profile_pics', verbose_name='Фото')
	grade = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], default=1, blank=True, verbose_name='Класс')
	bio = models.TextField(default='Нет биографии', verbose_name='Био')
	teacher_status = models.CharField(max_length=3, choices=TEACHER_STATUS_CHOICES, null=True, blank=True, verbose_name='Статус учителя')
 
	def get_fio(self):
		parts = [self.last_name, self.first_name, self.middle_name]
		return ' '.join(filter(None, parts))