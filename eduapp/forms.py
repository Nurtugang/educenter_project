from django import forms
from django.core.exceptions import ValidationError
import phonenumbers
from .models import SystemFeedback

class SystemFeedbackForm(forms.ModelForm):
    class Meta:
        model = SystemFeedback
        fields = ['category', 'message']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


def phone_validator(value):
    # Преобразуем номер, если он начинается с 8
    if value.startswith('8') and len(value) == 11:
        value = '+7' + value[1:]  # Заменяем первую 8 на +7
    
    try:
        # Парсим номер телефона как международный
        phone_number = phonenumbers.parse(value, "KZ")  # KZ — это регион для Казахстана
        # Проверяем валидность номера
        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError('Неверный формат номера телефона.', code='invalid')
    except phonenumbers.NumberParseException:
        raise ValidationError('Неверный формат номера телефона.', code='invalid')
    

def validate_name(value):
    if len(value) < 3:
        raise ValidationError("Name must be at least 3 characters long.")


class CourseRequestForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваше имя',  
            'required': 'required',
            'data-error':"Представтесь пожалуйста.",
            'id': 'idname'
        })
    )

    email = forms.EmailField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваша эл. почта',  
            'required': 'required',
            'autocomplete': 'off',
            'id': 'idemail'

        })
    )
    phone = forms.CharField(
        max_length=255,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваш телефон',  
            'required': 'required',
            'autocomplete': 'off',
            'id': 'idphone'
        })
    )
    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Тема',  
            'autocomplete': 'off',
            'id': 'idsubject'


        })
    )
    message = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Сообщение(необязательно)', 
            'autocomplete': 'off',
        })
    )


# Форма с валидатором номера телефона
class TargetForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваше имя',
            'required': 'required',
            'id': 'idname'
        })
    )

    phone = forms.CharField(
        max_length=20, 
        validators=[phone_validator], 
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваш телефон',
            'required': 'required',
            'id': 'idphone'
        })
    )