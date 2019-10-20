from django.shortcuts import render,redirect
from user.models import *
from django.http.response import HttpResponse
from django.urls import reverse
import re

# Create your views here.
#user/register
def register(request):

    return render(request,'register.html')

#/register_handle
def register_handle(request):
    """注册处理"""
    #接受数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')

    #数据校验
    if not all([username, password, email]):
        # 参数不完整
        return render(request, 'register.html', {'errmsg': '数据不完整'})

    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        # 邮箱格式不正确
        return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

    if allow != 'on':
        # 协议不同意
        return render(request, 'register.html', {'errmsg': '请首先同意协议'})

        # 数据处理
        # 业务处理：用户注册，验证用户是否存在
    try:
        # 用户已经存在
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # 用户名不存在可以注册
        user = None

    if user:
        return render(request, 'register.html', {'errmsg': '用户已存在'})

    try:
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        print('111111111111111111')
        user.save()
    except Exception as e:
        return render(request, 'register.html', {'errmsg': '用户注册失败，请重试'})

    #返回应答

    # 返回结果, namespace=goods下面的name=index的视图函数
    return redirect(reverse('goods:index'))
    # return render(request,'register.html')
    # return  HttpResponse('1111111111111111')
