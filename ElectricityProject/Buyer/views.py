from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from Store.views import setPassword
from Buyer.models import *
from Store.models import *
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
    goodsType = GoodsType.objects.all()
    return render(request,'buyer/index.html',locals())

def loginOut(request):
    response = HttpResponseRedirect('/Buyer/login/')
    for key in request.COOKIES:
        response.delete_cookie(key)
    del request.session['username']
    return response

