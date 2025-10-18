from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from django.http import HttpResponse
from django.views.static import serve as mediaserve


def robots_txt(request):
    content = """User-agent: *
    Disallow: /admin/
    Sitemap: https://senim-school.com/sitemap.xml
    """
    return HttpResponse(content, content_type="text/plain")

    
urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('eduapp.urls')),
    path('', include('users.urls')),
    path('', include('eduprocesses.urls')),
    path('', include('check_journal.urls')),
    path('quiz/', include('quizer.urls')),
    path('open_quiz/', include('open_quiz.urls')),
    path('game/', include('fractions_game.urls')),
    path('store/', include('senim_store.urls')),
    path('weekly-tests/', include('weekly_tests.urls')),
    prefix_default_language=True,
)


urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
    path('robots.txt', robots_txt, name='robots_txt'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
 
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 
else:
    urlpatterns += [
        url(f'^{settings.MEDIA_URL.lstrip("/")}(?P<path>.*)$',
            mediaserve, {'document_root': settings.MEDIA_ROOT}),
        url(f'^{settings.STATIC_URL.lstrip("/")}(?P<path>.*)$',
            mediaserve, {'document_root': settings.STATIC_ROOT}),
    ]