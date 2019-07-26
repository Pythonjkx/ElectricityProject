from django.http import HttpResponse
from django.shortcuts import render
from alipay import AliPay
from django.shortcuts import HttpResponseRedirect
from Store.views import setPassword
from Buyer.models import *
from Store.models import *
import random
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
        subject='python课程',
        return_url='http://127.0.0.1:8000/Buyer/pay_result/',
        notify_url='http://127.0.0.1:8000/Buyer/pay_result/',
    )
    return HttpResponseRedirect('https://openapi.alipaydev.com/gateway.do?' + order_string)

def pay_result(request):
    return render(request,'buyer/pay_result.html',locals())


def goods_detail(request,good_id):
    order_id = random.randint(100000,1000000000000)
    goods_data = Goods.objects.filter(id = int(good_id),goods_under=1).first()
    return render(request, 'buyer/goods_detail.html', locals())
