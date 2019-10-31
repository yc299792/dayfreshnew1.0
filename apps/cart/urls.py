from django.conf.urls import url,include
from cart.views import CartAddView,CartInfoView


app_name='[cart]'
urlpatterns = [
    url(r'^add$', CartAddView.as_view(), name='add'),#添加购物车
    url(r'^$',CartInfoView.as_view(),name='show'),#显示购物车信息
]
