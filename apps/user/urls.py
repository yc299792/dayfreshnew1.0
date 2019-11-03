from django.conf.urls import url
from user import views
from apps.user.views import *

app_name='[user]'

urlpatterns = [
    # url(r'^register$',views.register,name='register'),
    # url(r'^register_handle$',views.register_handle,name='register_handle'),
    url(r'^register$',RegisterView.as_view(),name='register'),#注册as_view返回函数引用，根据请求方法匹配不同的函数
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'),#激活
    url(r'^login$', LoginView.as_view(), name='login'),  # 登录
    url(r'^order/(?P<page>\d+)$',UserOrderView.as_view(),name='order'),#订单
    url(r'^address$',AddressView.as_view(),name='address'),#地址
    url(r'^$',UserInfoView.as_view(),name='user'),#信息
    url(r'^logout$', LogoutView.as_view(), name='logout'),  # 注销登录
]
