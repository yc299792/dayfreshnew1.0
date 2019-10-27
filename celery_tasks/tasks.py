#使用celery
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
import time

# 初始化环境，在任务处理者那一端加
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dayfreshnew.settings')
django.setup()
#创建一个celery的对象,并命名，指定broker
app = Celery('celery_tasks.tasks',broker='redis://192.168.116.128:6379/8')

@app.task
def send_register_active_email(to_email, username, token):
    """发送激活邮件"""
    # 发送邮件
    subject = '天天生鲜激活信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
        username, token, token)

    try:
        send_mail(subject,
                  message,
                  sender,
                  receiver,
                  html_message=html_message, fail_silently=False)
    except Exception as e:
        print(e)

# 类的导入写在celery配置完成的下方
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner

@app.task
def generate_static_index_html():
    """产生首页静态化页面"""

    # 获取商品的种类信息
    types = GoodsType.objects.all()

    # 获取轮播图信息
    banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取促销信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')

        type.image_banners = image_banners
        type.title_banners = title_banners

    context = {
        'types': types,
        'goods_banners': banners,
        'promotion_banners': promotion_banners,
    }

    # 产生静态界面
    temp = loader.get_template('staticindex.html')
    static_index_html = temp.render(context)

    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')

    with open(save_path, 'w') as f:
        f.write(static_index_html)

