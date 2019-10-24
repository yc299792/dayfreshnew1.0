from django.shortcuts import render,redirect
from user.models import *
from django.http.response import HttpResponse
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
import re

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired#加解密类
from django.conf import settings
from django.core.mail import send_mail
from utils.Mixin import LoginRequiredMixin


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

    def post(self,request):
        """使用django内置的认证系统来处理认证和login后的记录登录状态到session"""

        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remember')

        # 参数验证
        if not all([username, password]):
            # 参数不完整
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 业务处理：用户注册，验证用户是否存在
        # 业务处理:登录校验，使用自带的校验
        user = User.objects.get(username=username)
        print(user.username,user.password)
        user = authenticate(username=username, password=password)

        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态，这里自动设置session
                login(request, user)

                # 获取登录后所要跳转到的地址,在登录后跳转，get函数可以设置默认值
                # 默认跳转到首页
                next_url = request.GET.get('next', reverse('goods:index'))

                # 跳转到next_url
                response = redirect(next_url)  # HttpResponseRedirect

                # 判断是否需要记住用户名

                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')

                # 返回response
                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})

# /user
class UserInfoView(LoginRequiredMixin,View):
    """用户中心信息页"""

    # LoginRequiredMixin的自定义扩展类中的login_required装饰器是配合当初的自带login()，登陆后存储session到cache中的
    # 因为自己的user类是继承自自带的认证user类，所以每次请求都会存在一个request.user对象
    # 登陆的话，request.user返回的是一个真实的user对象，否则返回的是一个anonymousUser对象
    # 真实对象的is_authenticated方法返回的是true，匿名对象的这个方法返回的是false
    # django自动会吧request.user对象返回给模板中，不需要手动传递，只需要在模板中调用user即可

    def get(self,request):
        """显示"""
        address = Address.objects.get_default_address(request.user)
        return render(request,'user_center_info.html',{'page':'user','address':address})

# /user/order
class UserOrderView(LoginRequiredMixin,View):
    """用户中心订单页"""


    def get(self, request):
        """显示"""


        return render(request, 'user_center_order.html',{'page':'order'})

# /user/address
class AddressView(LoginRequiredMixin,View):
    """用户中心订单页"""

    def get(self, request):
        """显示"""
        # 获取登录用户对应User对象
        user = request.user
        #
        # # 数据库获取用户的默认和其他地址信息
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)

        return render(request, 'user_center_site.html',{'page':'address','address':address})

    def post(self,request):
        """地址的添加"""
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据
        if not all([receiver, addr, phone, type]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        # 业务处理：地址添加
        # 如果用户已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        # 获取登录用户对应User对象
        user = request.user

        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)

        if address == None:
            is_default = True
        else:
            is_default = False

        # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)

        # 返回应答,get方式刷新地址页面
        return redirect(reverse('user:address'))


class LogoutView(View):
    """退出登录"""

    def get(self, request):

        # 自带logout方法清除session信息
        logout(request)
        # 跳转到首页
        return redirect(reverse('goods:index'))





