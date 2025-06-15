from django.urls import path
from . import views

urlpatterns = [
    path('giggh', views.giggh, name='giggh')
]