"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^release/', 'release.views.Release'),
    url(r'^onerelease/', 'release.views.OneRelease'),
    url(r'^accounts/profile/', 'release.views.OneRelease'),
    url(r'^select_project/', 'release.views.SelectProject'),
    url(r'^switch/', 'release.views.Switch'),
    url(r'^$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    #url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}),
    url(r'^accounts/logout/$', 'release.views.logout'),

]
