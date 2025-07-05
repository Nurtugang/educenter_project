from django.urls import path
from . import views
urlpatterns = [
    path('', views.quizer_choose, name='quizer_choose'),
    path('start/', views.quiz_page, name='quiz_page'),
    path('testing_handle/<int:quiz_id>/', views.testing_handle, name='testing_handle'),
    path('generate-document<int:quiz_id>/<int:attempt_number>/', views.generate_document, name='generate-document'),
    path('generate-random-test/<int:quiz_id>/', views.generate_random_test, name='generate-random-test'),

    path('quiz_results/<int:quiz_id>/', views.quiz_results, name='quiz_results')
]

handler404 = 'users.views.custom_404'