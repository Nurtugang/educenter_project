from django.urls import path 
from .views import *
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', index, name='index'),
    path('contact', contact, name='contact'),
    path('elessons', elessons, name='elessons'),
    path('videolessons/<int:courseid>/', videolessons, name='videolessons'),

    path('videocourses/<int:courseid>/', videocourses, name='videocourses'), #таргет
    path('videocourses/access', vidaccess, name='vidaccess'),
    
    path('ajax/feedback/', feedback_ajax, name='feedback_ajax'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'), #индексация
]