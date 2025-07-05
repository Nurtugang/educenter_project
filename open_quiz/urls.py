from django.urls import path
from . import views
urlpatterns = [
    path('', views.open_quizer_choose, name='open_quizer_choose'),
    path('start/', views.open_quizer_page, name='open_quizer_page'),
    path('open_quizer_results/<int:quiz_id>/', views.open_quizer_results, name='open_quizer_results'),
    path('open_testing_handle/<int:open_quiz_id>/', views.open_testing_handle, name='open_testing_handle'),
    
    # Новые URL для работы с прогрессом теста
    path('save_progress/<int:quiz_id>/', views.save_test_progress, name='save_test_progress'),
    path('continue/<int:progress_id>/', views.continue_test, name='continue_test'),
    path('cancel_test/<int:progress_id>/', views.cancel_test, name='cancel_test'),
    
]

handler404 = 'users.views.custom_404'