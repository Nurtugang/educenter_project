from django.urls import path
from . import views

urlpatterns = [
    path('leaderboard/', views.weekly_leaderboard, name='weekly_leaderboard'),
]