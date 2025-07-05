from django.contrib import admin
from eduapp.models import VideoLesson, VideoCourse, Subscription, CourseRequest, Feedback, TargetVideoCourse, TargetModel, RegularVideoCourse, SystemFeedback
from django import forms


from django.utils.html import format_html

class VideoLessonAdmin(admin.ModelAdmin):
    # Отображение полей в списке видеороликов
    list_display = ('name', 'link_rus_clickable', 'dur_rus', 'link_kaz_clickable', 'dur_kaz', 'course')
    
    # Разрешаем редактировать продолжительность видео прямо из списка
    list_editable = ('dur_rus', 'dur_kaz')
    
    # Фильтр по курсам в правой части админки
    list_filter = ('course',)

    # Функции для создания кликабельных ссылок
    def link_rus_clickable(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.link_rus, obj.link_rus)
    link_rus_clickable.short_description = 'Russian Video Link'
    
    def link_kaz_clickable(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.link_kaz, obj.link_kaz)
    link_kaz_clickable.short_description = 'Kazakh Video Link'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.first().name == 'Администратор':
            return qs
        return qs.filter(course__teacher=request.user)

admin.site.register(VideoLesson, VideoLessonAdmin)



class VideoCourseAdminForm(forms.ModelForm):
	class Meta:
		model = VideoCourse
		exclude = []

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Get the group name you want to filter by (replace 'YourGroupName' with the actual group name)
		# Get the queryset of CustomUser instances who are members of the specified group
		self.fields['teacher'].queryset = self.fields['teacher'].queryset.filter(groups__name__in=['Преподаватель', 'Администратор'])



class VideoCourseAdmin(admin.ModelAdmin):
	form = VideoCourseAdminForm
		
	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.groups.first().name == 'Администратор':
			return qs
		return qs.filter(teacher=request.user)

# Админ-класс для обычных видеокурсов
class RegularVideoCourseAdmin(admin.ModelAdmin):
    form = VideoCourseAdminForm

    # Исключаем поле is_target_course из формы
    exclude = ('is_target_course',)

    # При сохранении автоматически ставим is_target_course = False
    def save_model(self, request, obj, form, change):
        obj.is_target_course = False
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # Отображаем только курсы, где is_target_course=False
        qs = super().get_queryset(request)
        return qs.filter(is_target_course=False)

class TargetVideoCourseAdmin(admin.ModelAdmin):
	list_display = ('name', 'grade', 'semester', 'is_target_course')
	list_filter = ('grade', 'semester')
	search_fields = ('name',)

	form = VideoCourseAdminForm


	# Исключаем поле is_target_course из формы
	exclude = ('is_target_course',)

	# При сохранении автоматически ставим is_target_course = True
	def save_model(self, request, obj, form, change):
		obj.is_target_course = True
		super().save_model(request, obj, form, change)
		
	def get_queryset(self, request):
		# Переопределяем метод, чтобы отображать только курсы с таргетом
		qs = super().get_queryset(request)
		return qs.filter(is_target_course=True)

class TargetModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')  # Поля, которые отображаются в списке
    search_fields = ('name', 'phone')  # Поиск по этим полям
    list_filter = ('name',)  # Фильтрация по имени

    fieldsets = (
        (None, {
            'fields': ('name', 'phone')
        }),
    )

admin.site.register(RegularVideoCourse, RegularVideoCourseAdmin)
admin.site.register(TargetVideoCourse, TargetVideoCourseAdmin)
admin.site.register(Subscription)
admin.site.register(CourseRequest)
admin.site.register(Feedback)
admin.site.register(TargetModel, TargetModelAdmin)
admin.site.register(SystemFeedback)

