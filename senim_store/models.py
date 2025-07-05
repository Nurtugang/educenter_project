from django.db import models
from users.models import CustomUser


class Product(models.Model):
	class Meta:
		verbose_name = "Продукт"
		verbose_name_plural = "Продукты"
		  
	name = models.CharField(max_length=255, verbose_name='Название')
	description = models.TextField(blank=True, null=True, verbose_name='Описание')
	price = models.IntegerField(verbose_name='Цена')
	image = models.ImageField(upload_to='products/', verbose_name='Изображение')
	
	def __str__(self):
		return self.name


class Order(models.Model):
	class Meta:
		verbose_name = "Заказ"
		verbose_name_plural = "Заказы"
			
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
	products = models.ManyToManyField(Product, through='OrderItem', verbose_name='Продукты')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
	completed = models.BooleanField(default=False, verbose_name='Завершен')

	def __str__(self):
		return f"Заказ {self.id} от {self.user.username}"

class OrderItem(models.Model):
	class Meta:
		verbose_name = "Продукт в заказе"
		verbose_name_plural = "Продукты в заказе"
			
	order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
	product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
	quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')


class UserCoins(models.Model):
	class Meta:
		verbose_name = "Коины пользователя"
		verbose_name_plural = "Коины пользователей"
	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='coins', verbose_name='Пользователь')
	balance = models.PositiveIntegerField(default=0, verbose_name='Баланс')
	last_updated = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

	def __str__(self):
		return f"{self.user.username}'s Coins: {self.balance}"

