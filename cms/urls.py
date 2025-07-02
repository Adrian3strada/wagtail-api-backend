from django.urls import path
from .views import  NavbarAPIView

urlpatterns = [
  
    path('api/navbar/', NavbarAPIView.as_view(), name='navbar_api'),
]