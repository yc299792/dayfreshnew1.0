from django.conf.urls import url,include
from cart.views import CartAddView,CartInfoView,CartUpdateView,CartDeleteView


app_name='[cart]'
urlpatterns = [
    url(r'^add$', CartAddView.as_view(), name='add'),#添加购物车
    url('^update$', CartUpdateView.as_view(), name='update'),#更新购物车信息
    url('^delete$', CartDeleteView.as_view(), name='delete'),#删除
    url(r'^$',CartInfoView.as_view(),name='show'),#显示购物车信息

]
