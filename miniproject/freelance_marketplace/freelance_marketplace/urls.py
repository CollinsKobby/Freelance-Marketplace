"""
URL configuration for freelance_marketplace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
import django
from django.contrib import admin
from django.urls import include, path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_marketplace.settings')
django.setup()

from GigGh import views

urlpatterns = [
    path('', include('GigGh.urls')),
    path('admin/', admin.site.urls),
    path('registration/login/', views.login_View, name='login'),
    path('registration/signup/', views.signup, name='signup'),
    path('registration/logout/', views.logout_view, name='logout'),
]
