from django.db import models
# 导入manage模块
from django.db.models import Manager

# Create your models here.
class Buyer(models.Model):
    username = models.CharField(max_length=30,verbose_name='用户名')
    password = models.CharField(max_length=30,verbose_name='密码')
    email = models.EmailField(verbose_name='用户邮箱')
    phone = models.CharField(max_length=30,verbose_name='用户电话',blank=True,null=True)
    connect_address = models.TextField(verbose_name='联系地址',blank=True,null=True)


class Address(models.Model):
    address = models.TextField(verbose_name='收货地址')
    receive = models.CharField(max_length=30,verbose_name='收货人')
    rece_phone = models.CharField(max_length=30,verbose_name='收货电话')
    post_num = models.CharField(max_length=30,verbose_name='邮编')
    buyer_id = models.ForeignKey(to=Buyer,on_delete=models.CASCADE,verbose_name='用户id')


class Order(models.Model):
    order_id = models.CharField(max_length=30,verbose_name='id订单编号')
    order_count = models.IntegerField(verbose_name='商品数量')
    order_user = models.ForeignKey(to=Buyer,verbose_name='订单用户',on_delete=models.CASCADE)
    order_address = models.ForeignKey(to=Address,verbose_name='订单地址',on_delete=models.CASCADE,blank=True,null=True)
    order_price = models.FloatField(verbose_name='商品总价')
    order_status = models.IntegerField(default=1,verbose_name='订单状态')#1.未支付2.待发货3.已发货4.已收货0.已退货

class OrderDetail(models.Model):
    order_id = models.ForeignKey(to=Order,on_delete=models.CASCADE,verbose_name='订单编号')
    goods_id = models.IntegerField(verbose_name='商品id')
    goods_name = models.CharField(max_length=32,verbose_name='商品名称')
    goods_price = models.FloatField(verbose_name='商品价格')
    goods_number = models.IntegerField(verbose_name='商品数量')
    goods_total = models.FloatField(verbose_name='商品总价')
    goods_store = models.IntegerField(verbose_name='商店id')
    goods_images = models.ImageField(verbose_name='商品图片')


class Cart(models.Model):
    goods_name = models.CharField(max_length=30,verbose_name='商品名称')
    goods_price = models.FloatField(verbose_name='商品价格')
    goods_total = models.FloatField(verbose_name='商品总价')
    goods_number = models.IntegerField(verbose_name='商品数量')
    goods_picture = models.ImageField(upload_to='buyer/images',verbose_name='商品图片')
    goods_id = models.IntegerField(verbose_name='商品id')
    goods_store = models.IntegerField(verbose_name='商品的商店id')
    user_id = models.IntegerField(verbose_name='用户id')