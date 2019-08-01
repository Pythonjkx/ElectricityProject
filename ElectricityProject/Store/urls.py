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
    re_path('goods_list/(?P<state>\w+)',goods_list),
    re_path(r'^goods/(?P<goods_id>\d+)',goods),
    re_path(r'update_goods/(?P<goods_id>\d+)', update_goods),
    re_path(r'set_goods/(?P<state>\w+)/',set_goods),
    path('goods_list_type/',goods_list_type),
    re_path(r'delete_type/(?P<state>\w+)',delete_type),
    path('order_list/',order_list),
    re_path(r'set_order/(?P<states>\w+)/',set_order),
    re_path(r'order_result/',order_result),
    path('delete_order/',delete_order),
    path('api_request/',api_request),
    path('get_add/',get_add)

]