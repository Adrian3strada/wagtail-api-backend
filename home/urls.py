# home/urls.py
from django.urls import path
from .views import NavbarMenuAPI

urlpatterns = [
    path("api/navbar/", NavbarMenuAPI.as_view(), name="navbar-api"),
    # otras vistas si tienes
]
