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


class DetailView(View):
    """详情页"""
    def get(self,request,goods_id):
        """显示详情页"""
        try:
            sku = GoodsSKU.objects.get(id = goods_id)
        except GoodsSKU.DoesNotExist:
            #商品不存在
            return redirect(reverse('goods:index'))


        #获取商品分类
        types = GoodsType.objects.all()

        # 获取商品的评论信息,排除掉空评论的
        sku_order = OrderGoods.objects.filter(sku=sku).exclude(comment='')
        # 获取新品信息，排序降序，默认升序，再切片两个
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

        # 获取同一spu下面的其他商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

        # 获取首页购物车的数目
        cart_count = 0
        if request.user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%s' % request.user.id
            cart_count = conn.hlen(cart_key)

            # 向用户浏览历史中添加
            conn = get_redis_connection('default')
            history_key = 'history_%s' % request.user.id
            # 移除列表中的goods_id如果已经存在, 大于0表示从左移除几个，等于0表示移除所有存在的元素
            conn.lrem(history_key, 0, goods_id)
            # 左侧进行插入
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的5条数据
            conn.ltrim(history_key, 0, 4)

        context = {
            'sku': sku,
            'sku_order': sku_order,
            'types': types,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'same_spu_skus': same_spu_skus,
        }

        return render(request, 'detail.html', context)