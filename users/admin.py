from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from users.models import CustomUser
from users.forms import CustomUserCreationForm_Admin, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
	add_form = CustomUserCreationForm_Admin 
	form = CustomUserChangeForm
	model = CustomUser 
	fieldsets =( 
	   (None, {'fields':('username', 'email', 'password', 'is_staff')}), 
	   ('Персональная информация', {'fields':('first_name', 
					  'last_name' ,'middle_name', 'gender', 
					  'birth_date', 'groups')}),
	)
	add_fieldsets = ( 
	   (None, { 
			'classes':('wide',), 
			'fields':('username', 'email', 'first_name', 
					  'last_name' ,'middle_name', 'gender', 
					  'birth_date', 'password1', 'password2', 
					  'groups')} 
		), 
	) 

class Student(CustomUser):
	class Meta:
		proxy = True
		verbose_name = 'Студент'
		verbose_name_plural = 'Студенты'
	def save(self, *args, **kwargs):
		if not self.pk:  # If this is a new instance being created
			super().save(*args, **kwargs)  # Save the instance to get an id
			student_group = Group.objects.get(name='Студент')
			self.groups.set([student_group])
		else:
			super().save(*args, **kwargs)

class Teacher(CustomUser):
	class Meta:
		proxy = True
		verbose_name = 'Преподаватель'
		verbose_name_plural = 'Преподаватели'
	def save(self, *args, **kwargs):
		if not self.pk:  # If this is a new instance being created
			super().save(*args, **kwargs)  # Save the instance to get an id
			student_group = Group.objects.get(name='Преподаватель')
			self.groups.set([student_group])
		else:
			super().save(*args, **kwargs)

class Parent(CustomUser):
	class Meta:
		proxy = True
		verbose_name = 'Родитель'
		verbose_name_plural = 'Родители'
	def save(self, *args, **kwargs):
		if not self.pk:  # If this is a new instance being created
			super().save(*args, **kwargs)  # Save the instance to get an id
			student_group = Group.objects.get(name='Родитель')
			self.groups.set([student_group])
		else:
			super().save(*args, **kwargs)

class Administrator(CustomUser):
	class Meta:
		proxy = True
		verbose_name = 'Администратор'
		verbose_name_plural = 'Администраторы'
	def save(self, *args, **kwargs):
		if not self.pk:  # If this is a new instance being created
			super().save(*args, **kwargs)  # Save the instance to get an id
			student_group = Group.objects.get(name='Администратор')
			self.groups.set([student_group])
		else:
			super().save(*args, **kwargs)


class StudentAdmin(CustomUserAdmin):
	fieldsets =( 
	   (None, {'fields':('username', 'email', 'password', 'is_staff')}), 
	   ('Персональная информация', {'fields':('first_name', 
					  'last_name' ,'middle_name', 'phone', 'gender', 
					  'birth_date','image', 'groups')}),
	   ('Student Info', {'fields':('grade', 'bio')}),
	)
	add_fieldsets = ( 
	   (None, { 
			'classes':('wide',), 
			'fields':('username', 'email', 'first_name', 
					  'last_name' ,'middle_name', 'phone', 'gender', 
					  'birth_date', 'image', 'grade', 'bio', 'password1', 'password2', 
					  'is_staff',)} 
		), 
	)
	
	def get_queryset(self, request):
		group = Group.objects.get(name='Студент')
		return self.model.objects.filter(groups=group)


class TeacherAdmin(CustomUserAdmin):
	fieldsets =( 
	   (None, {'fields':('username', 'email', 'password', 'teacher_status', 'is_staff')}), 
	   ('Персональная информация', {'fields':('first_name', 
					  'last_name' ,'middle_name', 'phone', 'gender', 
					  'birth_date','image', 'groups')}),
	   ('Информация о учителе', {'fields':('bio',)}),
	)
	add_fieldsets = ( 
	   (None, { 
			'classes':('wide',), 
			'fields':('username', 'email', 'first_name', 
					  'last_name' ,'middle_name', 'teacher_status', 'phone', 'gender', 
					  'birth_date', 'image', 'bio', 'password1', 'password2', 
					  'is_staff')} 
		), 
	) 

	list_display = ('username', 'first_name', 'last_name', 'teacher_status', 'is_staff')
	list_filter = ('teacher_status',)
	
	def get_queryset(self, request):
		group = Group.objects.get(name='Преподаватель')
		return self.model.objects.filter(groups=group)

class ParentAdmin(CustomUserAdmin):
	fieldsets =( 
	   (None, {'fields':('username', 'email', 'password', 'is_staff')}), 
	   ('Персональная информация', {'fields':('first_name', 
					  'last_name' ,'middle_name', 'phone', 'gender', 
					  'birth_date','image', 'groups')}),
	)
	add_fieldsets = ( 
	   (None, { 
			'classes':('wide',), 
			'fields':('username', 'email', 'first_name', 
					  'last_name' ,'middle_name', 'phone', 'gender', 
					  'birth_date', 'image', 'password1', 'password2', 'is_staff',
					  )} 
		), 
	) 
	def get_queryset(self, request):
		group = Group.objects.get(name='Родитель')
		return self.model.objects.filter(groups=group)

class AdminAdmin(CustomUserAdmin):
	fieldsets =( 
	   (None, {'fields':('username', 'email', 'password', 'is_staff')}), 
	   ('Персональная информация', {'fields':('first_name', 
					  'last_name' ,'middle_name', 'phone', 'gender', 
					  'birth_date','image', 'groups')}),
	)
	add_fieldsets = ( 
	   (None, { 
			'classes':('wide',), 
			'fields':('username', 'email', 'first_name', 
					  'last_name' ,'middle_name', 'phone', 'gender', 
					  'birth_date', 'image', 'password1', 'password2', 'is_staff')} 
		), 
	) 
	def get_queryset(self, request):
		group = Group.objects.get(name='Администратор')
		return self.model.objects.filter(groups=group)
		
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Parent, ParentAdmin)
admin.site.register(Administrator, AdminAdmin)




