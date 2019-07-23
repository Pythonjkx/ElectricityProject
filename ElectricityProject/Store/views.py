import hashlib

from  Store.models import *
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect,JsonResponse

# Create your views here.


def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest()

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
                return HttpResponseRedirect('/Store/login/')
            else:
                result['content'] = '用户名已存在'
        else:
            result['content'] = '用户名或密码不能为空'
    return render(request,'store/register.html',locals())

def login(request):
    response = render(request,'store/login.html')
    print(response)
    response.set_cookie('login_form','login_page')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = Seller.objects.filter(username=username).first()
            if user:
                web_password = setPassword(password)
                cookies = request.COOKIES.get('login_form')
                if user.password == web_password and cookies == 'login_page':
                    response = HttpResponseRedirect('/Store/')
                    response.set_cookie('username',username)
                    response.set_cookie('user_id', user.id)
                    request.session['username'] = username
                    return response
    return response

def loginValid(fun):
    def inner(request,*args,**kwargs):
        c_name = request.COOKIES.get('username')
        s_name = request.session.get('username')
        if c_name and s_name:
            user = Seller.objects.filter(username=c_name).first()
            if user and user.username == s_name:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect('/Store/login/')
    return inner

@loginValid
def index(request):
    user_id = request.COOKIES.get('user_id')

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
    type_list = StoreType.objects.all()
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

        store = Store()
        store.store_name = store_name
        store.store_address = store_address
        store.store_description = store_description
        store.store_phone = store_phone
        store.store_money = store_money
        store.user_id = user_id
        store.store_logo = store_logo
        store.save()

        for i in type_lists:
            store_type = StoreType.objects.get(id=i)
            store.type.add(store_type)
        store.save()
    return render(request,'store/register_store.html',locals())

def add_goods(request):
    if request.method == 'POST':
        goods_name = request.POST.get('goods_name')
        goods_price = request.POST.get('goods_price')
        goods_number = request.POST.get('goods_number')
        goods_description = request.POST.get('goods_description')
        goods_date = request.POST.get('goods_date')
        goods_safeDate = request.POST.get('goods_safeDate')
        goods_store = request.POST.get('goods_store')
        goods_image = request.FILES.get('goods_image')

        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.save()

        goods.store_id.add(
            Store.objects.get(id = int(goods_store))
        )
        goods.save()
    return render(request,'store/add_goods.html')

def goods_list(request):
    list_goods = (Goods.objects.all()).count()
    keywords = request.GET.get('keywords','')#没有默认为空
    page_num = int(request.GET.get('page_num',1))#有是page_num，没有默认为1
    if keywords:
        goods_list = Goods.objects.filter(goods_name__contains=keywords)
    else:
        goods_list = Goods.objects.all()
    paginator = Paginator(goods_list,3)#对goods_list设置一个界面显示三页
    page = paginator.page(int(page_num))
    page_range = paginator.page_range
    page_totle = goods_list.count()
    page_all = page_totle//3 if page_totle // 3 == 0 else page_totle // 3 +1
    if page_num == page_all:
        next_page = page_all
    else:
        next_page = page_num + 1
    if page_num == 1:
        before_page = 1
    else:
        before_page = page_num - 1
    return render(request,'store/goods_list.html',locals())


def blank(request):
    return render(request,'store/blank.html')

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



def page404(request):
    return render(request,'store/page404.html')


def loginOut(request):
    response = HttpResponseRedirect('/Store/login/')
    response.delete_cookie('username')
    return response