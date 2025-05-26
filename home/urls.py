from django.urls import path
from .views import menu_api

urlpatterns = [
    path('api/menu/', menu_api, name='menu_api'),
]   