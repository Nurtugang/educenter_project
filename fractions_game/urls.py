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
    
    path('fractions-easy/', views.fractions_easy, name='fractions_easy'),
    path('percentages/', views.percentages, name='percentages'),
    path('proportions/', views.proportions, name='proportions'),
    
    path('api/fractions/generate/', views.fractions_generator, name='fractions_generator'),
    path('api/percentages/generate/', views.percent_generator, name='percent_generator'),
    path('api/proportions/generate/', views.proportion_generator, name='proportion_generator'),
    
    path('api/fractions/check/', views.fractions_checker, name='fractions_checker'),
    path('api/percentages/check/', views.percent_checker, name='percent_checker'),
    path('api/proportions/check/', views.proportion_checker, name='proportion_checker'),
]