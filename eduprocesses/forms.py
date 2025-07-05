from django import forms
from .models import Lesson, StudyGroup
from django.contrib.auth.models import Group


class MultiDatePickerWidget(forms.TextInput):
	template_name = 'custom_widgets/multi_date_picker_widget.html'

# Новый улучшенный виджет для выбора дат по диапазону и дням недели
class DateRangeWeekdayWidget(forms.TextInput):
	template_name = 'custom_widgets/date_range_weekday_widget.html'

class LessonAdminForm(forms.ModelForm):
	tmp = forms.CharField(widget=forms.HiddenInput())
	
	class Meta:
		model = Lesson
		fields = '__all__'
		widgets = {
			'date': DateRangeWeekdayWidget,  # Заменяем на новый виджет
			'temp': forms.HiddenInput(),
		}


class ZamenaForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('substitute_teacher', )


class StudyGroupAdminForm(forms.ModelForm):
	class Meta:
		model = StudyGroup
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['teacher'].queryset = Group.objects.get(name='Преподаватель').user_set.all()
		self.fields['students'].queryset = Group.objects.get(name='Студент').user_set.all()