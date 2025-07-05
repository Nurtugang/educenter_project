from django.urls import path, include

from users.views import profile, log_out, CustomPasswordChangeView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('log_out/', log_out, name='log_out'),
    path('profile/', profile, name='profile'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('', include('django.contrib.auth.urls')),
]

handler404 = 'users.views.custom_404'