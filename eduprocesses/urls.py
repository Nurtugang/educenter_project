from django.urls import path, include
from .views import *
from .json_views import *
from .tabel_views import tabel

urlpatterns = [
    path('journal/', journal, name='journal'),
    path('journal/<int:group_id>', journal_single, name='journal_single'),
    path('journal_student/', journal_student, name='journal_student'),

    path('tabel/', tabel, name='tabel'),
    path('attendancy/', attendancy, name='attendancy'),

    path('lesson_single/<int:lesson_id>', lesson_single, name='lesson_single'),
    path('lesson_student/<int:lesson_id>', lesson_student, name='lesson_student'),
    path('lessons/<int:lesson_id>/add_homework/', add_homework_view, name='add_homework'),
    path('lessons/<int:lesson_id>/add_max_grade/', add_max_grade_view, name='add_max_grade'),
    
    path('add_mark', add_mark, name='add_mark'),
    path('add_comment', add_comment, name='add_comment'),
    path('add_abs', add_abs, name='add_abs'),
    path('add_coins', add_coins, name='add_coins'),
    path('add_homework_status', add_homework_status, name='add_homework_status'),
    
    path('add-student-to-group/', add_student_to_group, name='add_student_to_group'),
    path('remove-student-from-group/', remove_student_from_group, name='remove_student_from_group'),
    
    path('student_profile/<int:student_id>/', student_profile, name='student_profile'),
    
    path('students_management/', students_management, name='students_management'),
    path('get_students_by_group/<int:group_id>/', get_students_by_group, name='get_students_by_group'),

]

handler404 = 'users.views.custom_404'