from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser


class WeeklyTest(models.Model):
    """Еженедельный тест"""
    class Meta:
        verbose_name = "Еженедельный тест"
        verbose_name_plural = "Еженедельные тесты"
        ordering = ['-week_start']
    
    week_start = models.DateField(verbose_name='Начало недели')
    week_end = models.DateField(verbose_name='Конец недели')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return f"Тест {self.week_start.strftime('%d.%m.%Y')} - {self.week_end.strftime('%d.%m.%Y')}"


class WeeklyTestSubject(models.Model):
    """Предмет конкретного еженедельного теста"""
    class Meta:
        verbose_name = "Предмет еженедельного теста"
        verbose_name_plural = "Предметы еженедельного теста"
        ordering = ['weekly_test', 'id']
    
    weekly_test = models.ForeignKey(
        WeeklyTest,
        on_delete=models.CASCADE,
        verbose_name='Еженедельный тест',
        related_name='subjects'
    )
    name = models.CharField(max_length=255, verbose_name='Название предмета')
    
    def __str__(self):
        return f"{self.weekly_test} - {self.name}"


class WeeklyTestResult(models.Model):
    """Результат еженедельного теста"""
    class Meta:
        verbose_name = "Результат еженедельного теста"
        verbose_name_plural = "Результаты еженедельного теста"
        unique_together = ['weekly_test', 'student', 'subject']
        ordering = ['weekly_test', 'student', 'subject__id']
    
    weekly_test = models.ForeignKey(
        WeeklyTest,
        on_delete=models.CASCADE,
        verbose_name='Еженедельный тест'
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Студент',
        limit_choices_to={'groups__name': 'Студент'}
    )
    subject = models.ForeignKey(
        WeeklyTestSubject,
        on_delete=models.CASCADE,
        verbose_name='Предмет'
    )
    score = models.PositiveIntegerField(
        verbose_name='Балл',
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True,
        help_text='Балл от 0 до 100'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    
    def __str__(self):
        score_display = self.score if self.score is not None else "не указан"
        return f"{self.student.get_full_name()} - {self.subject.name} - {score_display}"