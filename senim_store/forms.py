from django import forms
from senim_store.models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['products']  # Можно добавить дополнительные поля, если нужно
