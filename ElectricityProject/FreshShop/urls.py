"""FreshShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path,include,re_path
from Buyer.views import index
from Store.models import Goods
from Store.models import GoodsType
from rest_framework import routers
from Store.views import *


router = routers.DefaultRouter() #声明一个默认的路由注册器
router.register(r'goods',UserViewSet)#注册写好的接口视图
router.register(r'goodsType',TypeViewSet)#注册写好的接口视图

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Store/',include('Store.urls')),
    path('Buyer/',include('Buyer.urls')),
    re_path(r'^API',include(router.urls)), #restful 根路由
    re_path(r'^api-auth',include('rest_framework.urls')),#接口认证
    path('ckeditor/',include('ckeditor_uploader.urls')),
]
urlpatterns +=[
    re_path(r'^$',index),
]