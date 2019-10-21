from django.shortcuts import render,redirect
from user.models import *
from django.http.response import HttpResponse
from django.urls import reverse
from django.views.generic import View
import re

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired#加解密类
from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.tasks import send_register_active_email

# Create your views here.
#user/register
def register(request):

    if request.method == 'GET':

        return render(request,'register.html')
    elif request.method == 'POST':
        #注册处理
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 数据校验
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

        # 返回应答

        # 返回结果, namespace=goods下面的name=index的视图函数
        return redirect(reverse('goods:index'))
        # return render(request,'register.html')
        # return  HttpResponse('1111111111111111')

class RegisterView(View):
    """注册类"""
    def get(self,request):
        """显示注册页面"""
        return render(request,'register.html')

    def post(self,request):
        """post方式被调用"""
        # 注册处理
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 数据校验
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
            user.save()
        except Exception as e:
            return render(request, 'register.html', {'errmsg': '用户注册失败，请重试'})

        # 设置激活链接/user/active/user_id,对用户信息进行加密并设置过期时间
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode('utf8')


        # 发邮件
        # subject = '激活信息'
        # msg = ''
        # sender = settings.EMAIL_FROM
        # recvier = [email]
        # html_msg = '<h3>用户：%s你好，欢饮成为天天生鲜会员，请点击连接激活！<a href = "http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a></h3>'%(username,token,token)

        #阻塞发送，用户体验不好，网站得使用异步执行任务，优化用户体验，使用celery
        # send_mail(subject,msg,sender,recvier,html_message=html_msg)
        # 使用celery发送
        send_register_active_email.delay(email,username,token)

        # 返回结果, namespace=goods下面的name=index的视图函数
        return redirect(reverse('goods:index'))
        # return render(request,'register.html')
        # return  HttpResponse('1111111111111111')

class ActiveView(View):
    """用户激活"""

    def get(self, request, token):
        # token揭密，获取用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']

            # 根据id更改数据库胡is_active
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转登录页面
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            # 激活链接一过期
            return HttpResponse('激活链接已经过期')

class LoginView(View):
    """登陆界面"""

    def get(self, request):

        # 判断是否已经记录了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        return render(request, 'login.html', {'username': username, 'checked': checked})




