from django.urls import path,re_path
from Buyer.views import *
urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('loginOut/', loginOut),
    path('goods_list/',goods_list),
    re_path(r'goods_detail/(?P<good_id>\d+)',goods_detail),
    path('place_order/',place_order),
    path('cart/',cart),
    path('add_cart/',add_cart)
]

urlpatterns += [
    path('base/',base),
    path('order_pay/',order_pay),
    path('pay_result/',pay_result)
]