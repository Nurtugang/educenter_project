from django.urls import path, include
from .views import check_journal, missed_lessons, deadline_full
urlpatterns = [
    path('check_journal/', check_journal, name='check_journal'),
    path('missed_lessons/<str:teacher_id>/<str:selected_period>/<str:start_date>/<str:end_date>', missed_lessons, name='missed_lessons'),
    path('deadline_full/<str:selected_period>/<str:start_date>/<str:end_date>', deadline_full, name='deadline_full'),

]

handler404 = 'users.views.custom_404'