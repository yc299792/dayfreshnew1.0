"""dayfresh URL Configuration

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
from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^user/',include('user.urls',namespace='user')),#用户模块
    url(r'^cart/',include('cart.urls',namespace='cart')),
    url(r'^order/',include('order.urls',namespace='order')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^', include('goods.urls',namespace='goods')), #放在最后匹配首页

]
