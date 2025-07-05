from django import forms
from django.db.models import Q
from users.models import CustomUser
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm


class CustomUserCreationForm(UserCreationForm):
	groups = forms.ModelChoiceField(queryset=Group.objects.filter(~Q(name__contains='Админ') & ~Q(name__contains='Преподаватель')))
	class Meta:
		model = CustomUser

		fields = ('username', 'email', 'first_name', 'last_name', 'middle_name', 
				'gender', 'birth_date', 'groups')


class CustomUserCreationForm_Admin(UserCreationForm):
	class Meta:
		model = CustomUser
		fields = ('username', 'email', 'first_name', 'last_name', 'middle_name', 
				'gender', 'birth_date', 'groups')


class CustomUserChangeForm(UserChangeForm):
	class Meta:
		model = CustomUser
		fields = ('username', 'email', 'first_name', 'last_name', 'middle_name', 
				'gender', 'birth_date', 'groups')


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Текущий пароль'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Новый пароль'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подтвердите новый пароль'})