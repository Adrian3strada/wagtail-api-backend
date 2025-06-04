from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

from home.api import CustomPagesAPIViewSet, FooterAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter

# API
api_router = WagtailAPIRouter('wagtailapi')
api_router.register_endpoint('pages', CustomPagesAPIViewSet)
api_router.register_endpoint('footer', FooterAPIViewSet)

from django.conf.urls.i18n import i18n_patterns  # 👈 necesario para traducción

urlpatterns = [
    # Para permitir cambiar idioma con {% url 'set_language' %}
    path('i18n/', include('django.conf.urls.i18n')),

    # API no necesita i18n
    path('api/v2/', api_router.urls),
]

# Aquí definimos las rutas multilingües
urlpatterns += i18n_patterns(
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    
    path("", include("home.urls")), 
    path("", include(wagtail_urls)),  
)

# Archivos estáticos y media en desarrollo
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
