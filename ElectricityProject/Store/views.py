import hashlib

from Store.models import * #导入数据模型
from Buyer.models import *
from django.shortcuts import render
from django.core.paginator import Paginator #导入页码模块
from django.http import HttpResponseRedirect,JsonResponse

# Create your views here.

# 设置md5加密
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest()

# 用户注册
def register(request):
    result = {'content':''}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            seller = Seller.objects.filter(username=username).first()
            if not seller:
                seller=Seller()
                seller.username = username
                seller.password = setPassword(password)
                seller.nickname = username
                seller.save()
                return HttpResponseRedirect('/Store/login/')#跳转登录页面
            else:
                result['content'] = '用户名已存在'
        else:
            result['content'] = '用户名或密码不能为空'
    return render(request,'store/register.html',locals())

# 用户登录
def login(request):
    response = render(request,'store/login.html') #先捕获登录界面
    response.set_cookie('login_form','login_page')#设置登录界面的cookie
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:#判断输入框是否为空
            user = Seller.objects.filter(username=username).first()
            if user:#判断用户是否存在
                web_password = setPassword(password)
                cookies = request.COOKIES.get('login_form')#获取登录界面的设置的cookie
                if user.password == web_password and cookies == 'login_page':#判断密码和cookie
                    response = HttpResponseRedirect('/Store/')#跳转到主页
                    response.set_cookie('username',username)#设置主页用户的cookie
                    response.set_cookie('user_id', user.id)#设置主页店铺的cookie
                    request.session['username'] = username#设置主页用户的session
                    store = Store.objects.filter(user_id = user.id).first()#校验是否有店铺
                    if store:#如果有店铺下发店铺id
                        response.set_cookie('has_store',store.id)
                    else:#如果没有店铺下发空
                        response.set_cookie('has_store', '')
                    return response
    return response

# 登录验证装饰器
def loginValid(fun):
    def inner(request,*args,**kwargs):
        c_name = request.COOKIES.get('username')#接收cookies
        s_name = request.session.get('username')#接收session
        if c_name and s_name:
            user = Seller.objects.filter(username=c_name).first()#判断数据库中是否有用户名第一层
            if user and user.username == s_name:#判断数据库中是否有用户名第二层
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect('/Store/login/')
    return inner

@loginValid
# 主页
def index(request):
    user_id = request.COOKIES.get('user_id')#获取店铺id
    if user_id:
        user_id = int(user_id)
    else:
        user_id = 0
    store = Store.objects.filter(user_id=user_id).first()
    if store:
        is_store = 1
    else:
        is_store = 0
    return render(request,'store/index.html',{'is_store':is_store})

def register_store(request):
    type_list = StoreType.objects.all()#获取所有种类
    if request.method == 'POST':
        post_data = request.POST
        store_name = post_data.get('store_name')
        store_address = post_data.get('store_adress')
        store_description = post_data.get('store_description')
        store_phone = post_data.get('store_phone')
        store_money = post_data.get('store_money')

        user_id = int(request.COOKIES.get('user_id'))
        type_lists = post_data.getlist('type')

        store_logo = request.FILES.get('store_logo')

        store = Store()#实例化数据库
        store.store_name = store_name
        store.store_address = store_address
        store.store_description = store_description
        store.store_phone = store_phone
        store.store_money = store_money
        store.user_id = user_id
        store.store_logo = store_logo
        store.save()#保存数据库

        for i in type_lists:#一对多的数据库保存
            store_type = StoreType.objects.get(id=i)
            store.type.add(store_type)
        store.save()
        response = HttpResponseRedirect('/Store/')
        response.set_cookie('has_store',store.id)#商铺注册成功下发cookie
        return response
    return render(request,'store/register_store.html',locals())

# 添加商品
def add_goods(request):
    goods_type_list = GoodsType.objects.all()
    if request.method == 'POST':
        goods_name = request.POST.get('goods_name')
        goods_price = request.POST.get('goods_price')
        goods_number = request.POST.get('goods_number')
        goods_description = request.POST.get('goods_description')
        goods_date = request.POST.get('goods_date')
        goods_safeDate = request.POST.get('goods_safeDate')
        goods_store = request.POST.get('goods_store')
        goods_image = request.FILES.get('goods_image')
        goods_type = request.POST.get('goods_type')

        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.goods_type = GoodsType.objects.get(id = int(goods_type))
        goods.store_id = Store.objects.get(id=int(goods_store))
        goods.save()
        return HttpResponseRedirect('/Store/goods_list/up/')
    return render(request,'store/add_goods.html',locals())

# 商品列表
@loginValid
def goods_list(request,state):
    if state == 'up':
        state_num = 1
    else:
        state_num = 0
    keywords = request.GET.get('keywords','')#没有搜索关键词默认为空
    page_num = int(request.GET.get('page_num',1))#有跳转的页码是page_num，没有默认为1
    store_id = request.COOKIES.get('has_store')#获取店铺id
    store = Store.objects.filter(id = int(store_id)).first()#获取店铺
    if keywords:
        goods_list = store.goods_set.filter(goods_name__contains = keywords,goods_under = state_num)#过滤，获取所有包含关键字的内容
    else:
        goods_list = store.goods_set.filter(goods_under = state_num)
    paginator = Paginator(goods_list,4)#对goods_list设置一页显示4条数据
    page = paginator.page(int(page_num))#第page_num页的内容
    page_range = paginator.page_range#获取页数范围
    page_totle = goods_list.count()#总页数
    page_all = page_totle//4 if page_totle % 4 == 0 else page_totle // 4 +1 #求出所有页数
    list_goods = len(goods_list)#商品种类数
    if page_num == page_all:#判断下一页按钮的取值
        next_page = page_all
    else:
        next_page = page_num + 1
    if page_num == 1:#判断上一页按钮的取值
        before_page = 1
    else:
        before_page = page_num - 1
    return render(request,'store/goods_list.html',locals())

# 商品详情
def goods(request,goods_id):
    goods_data = Goods.objects.filter(id=goods_id).first()
    return render(request,'store/goods.html',locals())

def goods_list_type(request):
    goodsTypes = GoodsType.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        picture = request.POST.get('picture')

        goodsType = GoodsType()
        goodsType.name = name
        goodsType.description = description
        goodsType.picture = picture
        goodsType.save()
    return render(request,'store/goods_list_type.html',locals())

# 修改商品信息
def update_goods(request,goods_id):
    goods_data = Goods.objects.get(id = goods_id)#获取要修改商品的id
    if request.method == 'POST':
        goods_name = request.POST.get('goods_name')
        goods_price = request.POST.get('goods_price')
        goods_number = request.POST.get('goods_number')
        goods_description = request.POST.get('goods_description')
        goods_date = request.POST.get('goods_date')
        goods_safeDate = request.POST.get('goods_safeDate')
        goods_image = request.FILES.get('goods_image')

        goods = Goods.objects.get(id = int(goods_id))
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        if goods_image:#判断是否修改图片
            goods.goods_image = goods_image
        goods.save()
        return HttpResponseRedirect('/Store/goods/%s/'%goods_id)#重定向到修改好的商品的详情页
    return render(request,'store/update_goods.html',locals())

# 退出
def loginOut(request):
    response = HttpResponseRedirect('/Store/login/')
    for key in request.COOKIES:
        response.delete_cookie(key)#删除cookie
    return response

def set_goods(request,state):
    if state == 'up':
        state_num = 1
    else:
        state_num = 0
    id = request.GET.get('id')
    referer = request.META.get('HTTP_REFERER')
    if id:
        goods = Goods.objects.filter(id = id).first()
        if state == 'delete':
            goods.delete()
        else:
            goods.goods_under = state_num
            goods.save()
    return HttpResponseRedirect(referer)


def delete_type(request,state):
    id = request.GET.get('id')
    referer = request.META.get('HTTP_REFERER')
    if id:
        goods_list_type = GoodsType.objects.get(id = id)
        if state == 'delete':
            goods_list_type.delete()
    return HttpResponseRedirect(referer)








# base页面
def blank(request):
    return render(request,'store/blank.html')

# ajak注册校验
def ajax(request):
    result = {'status':'error','content':''}
    username = request.GET.get('username')
    if username:
        user = Seller.objects.filter(username=username).first()
        if user:
            result['content'] = '用户名已存在'
        else:
            result['content'] = '用户名可以使用'
            result['status'] = 'success'
    else:
        result['content'] = '用户名不可为空'
    return JsonResponse(result)

def order_list(request):
    store_id = request.COOKIES.get('has_store')
    order_list = OrderDetail.objects.filter(order_id__order_status = 2,goods_store = store_id)
    return render(request,'store/order_list.html',locals())


def order_result(request):
    id = request.GET.get('order_id')
    store_id = request.COOKIES.get('has_store')
    order_list = OrderDetail.objects.filter(order_id__order_status= 3, goods_store=store_id)
    return render(request, 'store/order_result.html', locals())

def delete_order(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(order_id=order_id)
    order.delete()
    return HttpResponseRedirect('/Store/order_result/')
def set_order(request,states):
    if states == 'ok':
        states_num = 3
    else:
        states_num = 0
    id = request.GET.get('order_id')
    order = Order.objects.filter(order_id=id).first()
    order.order_status = states_num
    order.save()
    return HttpResponseRedirect('/Store/order_result/')


def page404(request):
    return render(request,'store/page404.html')


from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from Store.serializers import *


class UserViewSet(viewsets.ModelViewSet):

    queryset = Goods.objects.all()#具体返回的数据
    print(queryset)
    serializer_class = UserSerializer#指定过滤的类
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['goods_name','goods_price']



class TypeViewSet(viewsets.ModelViewSet):
    # 返回具体查询的内容
    queryset = GoodsType.objects.all()
    serializer_class = GoodsTypeSerializer

def api_request(request):

    return render(request,'store/api_request.html')

from django.core.mail import send_mail
def sendMail(request):
    send_mail('邮件主题','邮件内容','from_email',['to_email'],fail_silently=False)

from CeleryTask.tasks import add
def get_add(request):
    add.delay(100,200)
    return JsonResponse({'status':200})


