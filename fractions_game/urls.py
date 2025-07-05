from django.urls import path
from . import views

urlpatterns = [
    path('play/', views.play_game, name='play_game'),
    path('play/<path:path>', views.get_file_game),
    path('expressions/', views.expressions, name='expressions'),
    path('expressions_generator/', views.expressions_generator, name='expressions_generator'),
    path('expressions_checker/', views.expressions_checker, name='expressions_checker'),

    path('equations/', views.equations, name='equations'),
    path('equations_generator/', views.equations_generator, name='equations_generator'),
    path('equations_checker/', views.equations_checker, name='equations_checker'),
]