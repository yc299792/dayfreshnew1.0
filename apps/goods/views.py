from django.core.cache import cache

# Create your views here.
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner, GoodsSKU
from order.models import OrderGoods


# Create your views here.

class IndexView(View):

    """
       显示首页，如果访问的是/index的话直接调用视图函数去重新查询一遍
           如果直接访问域名的话，那么加载的是celery服务器中已经渲染好的html代码，不需要数据库重新 查询
           当管理员更新后台的时候，会自动celery重新生成静态html网页，不影响使用
    """
    def get(self, request):
        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')
        if context is None:
            # 获取商品的种类信息
            types = GoodsType.objects.all()

            # 获取轮播图信息,默认升序
            banners = IndexGoodsBanner.objects.all().order_by('index')

            # 获取促销信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

            # 获取首页分类商品展示信息
            for type in types:
                # 获取type种类在首页展示的图片信息和文字信息
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

                type.image_banners = image_banners
                type.title_banners = title_banners

            # 上面查询出来的结果都一样，设置缓存
            context = {
            'types': types,
            'goods_banners': banners,
            'promotion_banners': promotion_banners,
            }
            cache.set('index_page_data', context, 3600)
            # print('设置缓存')

        # 获取首页购物车的数目，用户登录才能获取购物车
        if request.user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%s' % request.user.id
            cart_count = conn.hlen(cart_key)
        else:
            cart_count = 0

        context.update(cart_count=cart_count)

        return render(request, 'index.html', context=context)