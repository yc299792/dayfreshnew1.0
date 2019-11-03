from django.conf.urls import url,include
from order.views import OrderPlaceView,OrderCommitView, OrderPayView,CommentView
app_name='[order]'
urlpatterns = [
    url('^place$',OrderPlaceView.as_view(), name='place'),#订单页面
    url('^commit$', OrderCommitView.as_view(), name='commit'),#创建订单
    url('^pay$', OrderPayView.as_view(), name='pay'),#订单支付
    url('^comment/(?P<order_id>.+)$', CommentView.as_view(), name='comment'),#评论
]
