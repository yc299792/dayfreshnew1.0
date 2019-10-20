from django.conf.urls import url,include
from goods import views

app_name='[goods]'
urlpatterns = [
    url(r'^$',views.index,name='index'),

]
