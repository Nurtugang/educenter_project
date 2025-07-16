from django.contrib import admin
from django.forms import ModelForm
from django import forms
from .models import WeeklyTestSubject, WeeklyTest, WeeklyTestResult
from eduprocesses.models import StudyGroup
from users.models import CustomUser


class WeeklyTestForm(ModelForm):
    """Форма для создания еженедельного теста с выбором учебных групп"""
    study_groups = forms.ModelMultipleChoiceField(
        queryset=StudyGroup.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Учебные группы",
        help_text="Выберите группы для автоматического добавления студентов"
    )
    
    class Meta:
        model = WeeklyTest
        fields = ['week_start', 'week_end']


class WeeklyTestSubjectInline(admin.TabularInline):
    """Inline для управления предметами теста"""
    model = WeeklyTestSubject
    extra = 5
    fields = ['name']


@admin.register(WeeklyTest)
class WeeklyTestAdmin(admin.ModelAdmin):
    form = WeeklyTestForm
    inlines = [WeeklyTestSubjectInline]
    list_display = ['__str__', 'week_start', 'week_end', 'created_at', 'subjects_count', 'results_count']
    list_filter = ['week_start', 'created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('week_start', 'week_end')
        }),
        ('Добавление студентов', {
            'fields': ('study_groups',),
            'description': 'Выберите учебные группы для автоматического добавления всех студентов групп'
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def subjects_count(self, obj):
        """Показывает количество предметов для данного теста"""
        return WeeklyTestSubject.objects.filter(weekly_test=obj).count()
    subjects_count.short_description = 'Количество предметов'
    
    def results_count(self, obj):
        """Показывает количество результатов для данного теста"""
        return WeeklyTestResult.objects.filter(weekly_test=obj).count()
    results_count.short_description = 'Количество результатов'

    def save_related(self, request, form, formsets, change):
        """Вызывается после сохранения inline форм"""
        super().save_related(request, form, formsets, change)
        
        # Создаем результаты для студентов из выбранных групп
        weekly_test = form.instance
        selected_groups = form.cleaned_data.get('study_groups', [])
        
        if selected_groups:
            all_students = set()
            for study_group in selected_groups:
                students = study_group.students.all()
                all_students.update(students)
            
            subjects = WeeklyTestSubject.objects.filter(weekly_test=weekly_test)
            existing_results = set(
                WeeklyTestResult.objects.filter(weekly_test=weekly_test)
                .values_list('student_id', 'subject_id')
            )

            results_to_create = []
            for student in all_students:
                for subject in subjects:
                    if (student.id, subject.id) not in existing_results:
                        results_to_create.append(
                            WeeklyTestResult(
                                weekly_test=weekly_test,
                                student=student,
                                subject=subject,
                                score=None
                            )
                        )

            if results_to_create:
                WeeklyTestResult.objects.bulk_create(results_to_create)


@admin.register(WeeklyTestSubject)
class WeeklyTestSubjectAdmin(admin.ModelAdmin):
    list_display = ['weekly_test', 'name']
    list_filter = ['weekly_test', 'weekly_test__week_start']
    list_editable = ['name']
    ordering = ['weekly_test', 'id']


@admin.register(WeeklyTestResult)
class WeeklyTestResultAdmin(admin.ModelAdmin):
    list_display = ['weekly_test', 'student_name', 'subject', 'score', 'updated_at']
    list_filter = ['weekly_test', 'subject', 'weekly_test__week_start']
    list_editable = ['score']
    search_fields = ['student__first_name', 'student__last_name', 'student__username']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('weekly_test', 'student', 'subject', 'score')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def student_name(self, obj):
        """Отображает полное имя студента"""
        return obj.student.get_full_name() or obj.student.username
    student_name.short_description = 'Студент'
    student_name.admin_order_field = 'student__first_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'weekly_test', 'student', 'subject'
        )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ограничиваем выбор студентов"""
        if db_field.name == "student":
            kwargs["queryset"] = CustomUser.objects.filter(
                groups__name='Студент'
            ).order_by('first_name', 'last_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)