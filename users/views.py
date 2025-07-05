from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView

from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from eduapp.models import CustomUser, Subscription, VideoCourse
from users.forms import CustomUserCreationForm, CustomPasswordChangeForm


def register(request):
	if request.method == 'POST':
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			print(form.cleaned_data)
		else:
			print('form isnt valid')
	else:
		form = CustomUserCreationForm()
 
	return render(request, 'register.html', {'form': form})


def log_out(request):
	logout(request)


@login_required
def profile(request):
	my_courses = []
	if request.user.groups.all()[0] == Group.objects.get(name='Преподаватель'): #если это препод
		my_courses = VideoCourse.objects.filter(teacher=request.user)
	elif request.user.groups.all()[0] == Group.objects.get(name='Администратор'):
		my_courses = VideoCourse.objects.all()
	elif request.user.groups.all()[0] == Group.objects.get(name='Студент'): #если это студент
		subs = Subscription.objects.filter(student=request.user)
		for s in subs:
			my_courses.append(s.course)
	context={
		'my_courses': my_courses,
	}
	return render(request, 'profile.html', context)


def custom_404(request, exception):
    return render(request, '404.html', status=404)

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'change_password.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Пароль успешно изменен!')
        return super().form_valid(form)