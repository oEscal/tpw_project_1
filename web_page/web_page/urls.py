"""web_page URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from page.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('add_stadium/', add_stadium, name='add_stadium'),
    path('add_team/', add_team, name='add_team'),
    path('add_player/', add_player, name='add_player'),
    path('add_game/', add_game, name='add_game'),

    path('teams/', teams, name='teams'),
    url(r'^team/(?P<name>\w+)/$', team, name='team'),
    url(r'^player/(?P<id>\w+)/$', player, name='player'),
    url(r'^stadium/(?P<name>[\w\s]+)/$', stadium, name='stadium'),
]
