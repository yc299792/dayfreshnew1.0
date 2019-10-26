from django.conf.urls import url,include
from goods.views import *

app_name='[goods]'
urlpatterns = [
    url(r'^index$', IndexView.as_view(), name='index'),  # 首页

]
