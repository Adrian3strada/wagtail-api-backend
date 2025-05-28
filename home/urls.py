from django.urls import path
from .views import menu_api, NavbarAPIView

urlpatterns = [
    path('api/menu/', menu_api, name='menu_api'),
    path('api/navbar/', NavbarAPIView.as_view(), name='navbar_api'),
]