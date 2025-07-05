from django.db import models
from users.models import CustomUser
from django.core.validators import MaxValueValidator, MinValueValidator


class StudyGroupType(models.Model):
	class Meta:
		verbose_name = "Тип учебной группы"
		verbose_name_plural = "Типы учебных групп"

	name = models.CharField(max_length=255, verbose_name='Наименование типа группы')
	payment = models.PositiveIntegerField(verbose_name='Оплата за час')

	def __str__(self):
		return self.name


class Subject(models.Model):
	class Meta:
		verbose_name = "Учебный предмет"
		verbose_name_plural = "Учебные предметы"

	name = models.CharField(max_length=255, verbose_name='Наименование предмета')

	def __str__(self):
		return self.name


class StudyGroup(models.Model):
	class Meta:
		verbose_name = "Учебная группа"
		verbose_name_plural = "Учебные группы"

	name = models.CharField(max_length=255, verbose_name='Наименование типа группы')
	group_type = models.ForeignKey(StudyGroupType, on_delete=models.CASCADE, verbose_name='Тип группы')
	teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Учитель', related_name='teacher')
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
	students = models.ManyToManyField(CustomUser, verbose_name='Студенты', related_name='students')

	def __str__(self):
		return self.name

STATUS_CHOICES = (
	('P', 'Проведен'),
	('NP', 'Не проведен'),
	('Z', 'Замена'),
	('O', 'Отменен')
)

QUARTER_CHOICES = (
	('1', 'Первое полугодие'),
	('2', 'Второе полугодие'),
)

class Lesson(models.Model):
	class Meta:
		verbose_name = "Урок"
		verbose_name_plural = "Уроки"

	study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, verbose_name='Учебная группа')
	quarter = models.CharField(max_length=1, choices=QUARTER_CHOICES, verbose_name='Полугодие')
	date = models.DateField(verbose_name='Дата проведения урока', blank=True, null=True)
	status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='NP', verbose_name='Статус урока')
	reason_for_not_held = models.TextField(blank=True, null=True, verbose_name='Причина непроведения урока')
	substitute_teacher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Замененный учитель')
	hours = models.FloatField(default=1, verbose_name='Часы')
	deadline = models.DateTimeField(verbose_name='Дедлайн', blank=True, null=True)
	homework = models.TextField(blank=True, null=True, verbose_name='Домашнее задание')
	max_grade = models.SmallIntegerField(verbose_name='Максимальная оценка', default=10)

	def __str__(self):
		return f"Урок в {self.date} группы {self.study_group}"
	

class StudentAttendance(models.Model):
	class Meta:
		verbose_name = "Успеваемость ученика"
		verbose_name_plural = "Успеваемость учеников"

	lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='Урок')
	student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Студент')
	attendance_status = models.CharField(
		max_length=10,
		blank=True,
		null=True,
		choices=[
			('PR', 'Пришел на урок'),
			('ABS-R', 'Не пришел на урок с причиной'),
			('ABS-NR', 'Не пришел на урок без причины')
		],
		verbose_name='Статус посещения'
	)
	reason_for_absent = models.CharField(max_length=100, blank=True, null=True, verbose_name='Причина непосещения')
	mark = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Оценка')
	comment = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Комментарий')
	coins = models.PositiveIntegerField(
        default=0,
        verbose_name='Монеты',
        validators=[MinValueValidator(0)]
    )
	homework_completed = models.BooleanField(
		null=True, 
		blank=True, 
		verbose_name='Выполнил домашнее задание',
		help_text='Отметка о выполнении домашнего задания к этому уроку'
	)

	def __str__(self):
		return f"{self.student} - {self.lesson}"



	
