from django.urls import path,re_path
from Buyer.views import *
urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('loginOut/', loginOut),

]

urlpatterns += [
    path('base/',base),
]