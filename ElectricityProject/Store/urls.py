from django.urls import path,re_path
from Store.views import *
urlpatterns = [
    path('register/', register),
    path('login/', login),
    re_path('^$', index),
    path('blank/', blank),
    path('aj/',ajax),
    path('page404/',page404),
    path('loginOut/',loginOut),
    path('register_store/', register_store),
    path('add_goods/',add_goods),
    path('goods_list/',goods_list)
]