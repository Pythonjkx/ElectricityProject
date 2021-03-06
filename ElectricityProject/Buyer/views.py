from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Manager
from django.db.models import Sum,Max,Min,Avg
from alipay import AliPay
from django.shortcuts import HttpResponseRedirect
from Store.views import setPassword
from Buyer.models import *
from Store.models import *
import time
# Create your views here.

def base(request):
    return render(request,'buyer/base.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        buyer = Buyer()
        buyer.username = username
        buyer.password = setPassword(password)
        buyer.email = email
        buyer.save()
        return HttpResponseRedirect('/Buyer/login/')
    return render(request,'buyer/register.html')

def loginValid(fun):
    def inner(request,*args,**kwargs):
        c_name = request.COOKIES.get('username')#接收cookies
        s_name = request.session.get('username')#接收session
        if c_name and s_name:
            user = Buyer.objects.filter(username=c_name).first()#判断数据库中是否有用户名第一层
            if user and user.username == s_name:#判断数据库中是否有用户名第二层
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect('/Buyer/login/')
    return inner

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        if username and password:
            buyer = Buyer.objects.filter(username=username).first()
            if buyer:
                web_password = setPassword(password)
                if web_password == buyer.password:
                    response = HttpResponseRedirect('/Buyer/index/')
                    response.set_cookie('username',username)
                    response.set_cookie('user_id', buyer.id)
                    request.session['username'] = buyer.username
                    return response
    return render(request,'buyer/login.html')

@loginValid
def index(request):
    result = []
    goodsType_list = GoodsType.objects.all()
    for goods_type in goodsType_list:
        goods_list = goods_type.goods_set.values()[:4]#取物品类型所对应的物品前四个，通过反向查询（一里面查多）
        if goods_list:#如果列表不为空
            good_type = {'type_id':goods_type.id,
                        'name': goods_type.name,
                         'description': goods_type.description,
                         'picture': goods_type.picture,
                         'goods_list':goods_list}
            result.append(good_type)
    return render(request,'buyer/index.html',locals())

def loginOut(request):
    response = HttpResponseRedirect('/Buyer/login/')
    for key in request.COOKIES:
        response.delete_cookie(key)
    del request.session['username']
    return response

def goods_list(request):
    goodslist = []
    type_id = request.GET.get('type_id')
    goods_type = GoodsType.objects.filter(id = type_id).first()
    if goods_type:
        goodslist = goods_type.goods_set.filter(goods_under = 1)
    return render(request,'buyer/goods_list.html',locals())

def order_pay(request):
    money = request.GET.get('money')
    order_id = request.GET.get('order_id')

    alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnfsiQjfqKfaMFqd7VFBqu7yvK6NLO1y9eRjmA1eOTBDKcmy0qaq6/Xgwfz5FohJRD+zLGzQOvYhyVjIDzdxXQWaClB+fiS0+dz1IMVLBsWP6dhAIjjq/96EicDr+57V8ZMpuJneyS94wJfqDyFRj/fz9TciW7LQvzUMwg0tlXLPqDeTvO0CxKzNdwfCR6FIGC0MtzL1lGvI1c8YAcV3/6YrnO+O5YPKENHbdUKAZyj+jUlBqy6ojv9W4s1+gmcrtWev5cdY4KTEB4zBwK9p7vijFagAh/kOF79J0MvGpaWWsIMPlNxBzexSh1wvHhlzZSsE5PDfTXu/nHpfT2RjFmwIDAQAB
    -----END PUBLIC KEY-----"""

    app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEAnfsiQjfqKfaMFqd7VFBqu7yvK6NLO1y9eRjmA1eOTBDKcmy0qaq6/Xgwfz5FohJRD+zLGzQOvYhyVjIDzdxXQWaClB+fiS0+dz1IMVLBsWP6dhAIjjq/96EicDr+57V8ZMpuJneyS94wJfqDyFRj/fz9TciW7LQvzUMwg0tlXLPqDeTvO0CxKzNdwfCR6FIGC0MtzL1lGvI1c8YAcV3/6YrnO+O5YPKENHbdUKAZyj+jUlBqy6ojv9W4s1+gmcrtWev5cdY4KTEB4zBwK9p7vijFagAh/kOF79J0MvGpaWWsIMPlNxBzexSh1wvHhlzZSsE5PDfTXu/nHpfT2RjFmwIDAQABAoIBAQCSLS0l2FbzPQ2iaJXVDhO0YoIy/oU+CDHJOyCZNwqTl3W7Kpp/41nh7rPxCM2liQ04jwHfyetZtEcXOnAKqzaRbSilph0X8KU775g9CzXtzXSSiYNhFztJBe+3qN7zxxmyqRwCu/5d9NjYS1RkqLFc8hnvPwtnOdKBOwpIchr4Coy/bClEKTxF6SYwO3UEOiiWM9KJ07OnoL3v7hzOPiJ8lbQ1VC2Xqg0t52ec5i9we/v8AtQLFpKNcfLuT7Q5MSC+l8BAQ7PhL+4WMVCW7sr/14fv6rAssbfJGDA7kJCZVNxpA4mLch3Gcr3CveRD79LN5JLLjbJ9mYcW3xuVNu4BAoGBANCBuH6EC98aZLKFI7HS1qEa//wlq8fKxhC3KOBeMU/UB7WcOPBZRjpLnoR/xOAKn0ZtXCgePH9DvjnxaJbIo8Id9W05iINxqPU1VYjUUqbjWo1KZVngf+Q4SAu+DooSdDqEuo6OLx2Mc22bSJ4kF4yfkq7zJKyknXG4wbsBxzsDAoGBAMH3MlkBbdPkm/VLyeGSPkdIw1wU317rk971b9DKhCg0E4ljHEAhpWDowhnYOmnhfILBBkuI6JYl4kRljPrrVpylO1CK9p8U3TpzF6qmj+3I9nGkL8nGFM2k1JoWUbYyLMrqHr1m1p/b6s/E5kGOxDC21g1BxxpAawaNhv13dbuJAoGAcrjdJSdMTN39x8e/owjJtOzhKgAkKxKjtfDBGepZoX2dHEyve3bzUAHpXyfZ0BeoGRz01tIEIVXJpaHxFP2iNJ09O3KrbP8tonVM8bM5Ir/3Q8RKTZBbbduVsHhLEacjskrzRppuzAhKPmVxKCndly75iy8W37LXOgoY9eb9krcCgYAPRY9JQruK+2zsG1OB1yngIvJ+xYXwy0uROnHbVpahM7h2EL+grQWAY9MkhcnTnFVZVilQuS7W45S1HenDt9PR8ZCB/u78B4CDoZwza3nZlwEQYYUBtf7dUiULHMbCOaEdOOHCt94eKAqM4UvfzYXU8BBaattqTbgfg/Uk78rtQQKBgC3aZQzmb20+x0S9AwnMRnPi66smqQ95Xx3d4Hb0RqDQJSSivMCrs8URe4V6a9QVsr4rVPxHpQaSblw4reIIRcrIbBLX2naHJhO9yCT373JQ85VG6j9+p3nsHxknYqn+LwVSqmIkBO+WzqhEDpDgLRhrEk9PGIpY+IpWBN5aob6w
    -----END RSA PRIVATE KEY-----"""

    alipay = AliPay(
        appid='2016101000652535',
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type='RSA2',
    )

    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount=str(money),
        subject='良心铺子百货大全',
        return_url='http://127.0.0.1:8000/Buyer/pay_result/',
        notify_url='http://127.0.0.1:8000/Buyer/pay_result/',
    )
    order = Order.objects.get(order_id=order_id)
    order.order_status = 2
    order.save()
    return HttpResponseRedirect('https://openapi.alipaydev.com/gateway.do?' + order_string)

def pay_result(request):
    return render(request,'buyer/pay_result.html',locals())

@loginValid
def goods_detail(request,good_id):
    goods_data = Goods.objects.filter(id=int(good_id), goods_under=1).first()
    return render(request, 'buyer/goods_detail.html', locals())

def setOrder(user_id,good_id,store_id):
    order_id = time.strftime('%Y%m%d%H%M%S',time.localtime())
    return order_id+str(user_id)+str(good_id)+str(store_id)

def place_order(request):
    if request.method == 'POST':
        count = int(request.POST.get('count'))
        good_id = request.POST.get('good_id')
        goods = Goods.objects.get(id = good_id)
        user_id = request.COOKIES.get('user_id')
        store_id = goods.store_id.id
        price = goods.goods_price


        order = Order()
        order.order_id=setOrder(str(user_id),str(good_id),str(store_id))
        order.order_count = count
        order.order_user = Buyer.objects.get(id = user_id)
        order.order_price = count*price
        order.order_status = 1
        order.save()

        order_detial = OrderDetail()
        order_detial.order_id = order
        order_detial.goods_id = good_id
        order_detial.goods_name = goods.goods_name
        order_detial.goods_price = goods.goods_price
        order_detial.goods_number = count
        order_detial.goods_total = count*goods.goods_price
        order_detial.goods_store = store_id
        order_detial.goods_images = goods.goods_image
        order_detial.save()

        detail = [order_detial]
        return render(request,'buyer/place_order.html',locals())
    else:
        order_id = request.GET.get('order_id')
        if order_id:
            order = Order.objects.get(id = order_id)
            detail = order.orderdetail_set.all()
            return render(request,'buyer/place_order.html',locals())
        else:
            return HttpResponseRedirect('非法请求')


def cart(request):
    user_id = request.COOKIES.get('user_id')
    goods_list = Cart.objects.filter(user_id=user_id)
    if request.method == 'POST':
        post_data = request.POST
        cart_data = []
        for k,v in post_data.items():
            if k.startswith('goods_'):
                cart_data.append(Cart.objects.get(id=int(v)))
        goods_count = len(cart_data)
        goods_total = sum([int(i.goods_total) for i in cart_data])

        # cart_data = []
        # for k,v in post_data.items():
        #     if k.startswith('goods_'):
        #         cart_data.append(int(v))
        # cart_goods = Cart.objects.filter(id__in=cart_data).aggregate(Sum('goods_total'))
        # print(cart_goods)

        order = Order()
        order.order_id = setOrder(user_id,goods_count,'2')

        order.order_count = goods_count
        order.order_user = Buyer.objects.get(id = user_id)
        order.order_price = goods_total
        order.order_status = 1
        order.save()

        for detail in cart_data:
            order_deatil = OrderDetail()
            order_deatil.order_id = order
            order_deatil.goods_id = detail.goods_id
            order_deatil.goods_price = detail.goods_price
            order_deatil.goods_name = detail.goods_name
            order_deatil.goods_number = detail.goods_number
            order_deatil.goods_total = detail.goods_total
            order_deatil.goods_store = detail.goods_store
            order_deatil.goods_images =detail.goods_picture
            order_deatil.save()
        url = '/Buyer/place_order/?order_id=%s'%order.id
        return HttpResponseRedirect(url)
    return render(request,'buyer/cart.html',locals())

def add_cart(request):
    result = {'state':'error','data':''}
    if request.method == 'POST':
        count = int(request.POST.get('count'))
        goods_id = request.POST.get('goods_id')
        goods = Goods.objects.get(id=int(goods_id))

        user_id = request.COOKIES.get('user_id')

        cart = Cart()
        cart.goods_name = goods.goods_name
        cart.goods_price = goods.goods_price
        cart.goods_total = count*goods.goods_price
        cart.goods_number = count
        cart.goods_picture = goods.goods_image
        cart.goods_id = goods_id
        cart.goods_store = goods.store_id.id
        cart.user_id = user_id
        cart.save()
        result['state'] = 'success'
        result['data'] = '添加成功'
    else:
        result['data'] = '请求错误'
    return JsonResponse(result)






