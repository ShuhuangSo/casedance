from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
import requests
import time
import random
import json
import urllib
import hashlib
from datetime import datetime, timedelta

from mercado.models import Listing, ListingTrack, Categories, ApiSetting, TransApiSetting, Keywords, Seller, SellerTrack
from mercado.serializers import ListingSerializer, ListingTrackSerializer, CategoriesSerializer, SellerSerializer
from mercado import tasks


class DefaultPagination(PageNumberPagination):
    """
    分页设置
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 1000


class ListingViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    list:
        在线产品列表,分页,过滤,搜索,排序
    create:
        在线产品新增
    retrieve:
        在线产品详情页
    update:
        在线产品修改
    destroy:
        在线产品删除
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('site_id', 'listing_status', 'is_cbt', 'seller_id', 'seller_name', 'brand',
                     'collection')  # 配置过滤字段
    search_fields = ('item_id', 'title', 'seller_id', 'seller_name', 'brand')  # 配置搜索字段
    ordering_fields = ('create_time', 'total_sold', 'reviews', 'stock_num', 'profit', 'update_time')  # 配置排序字段

    # test
    @action(methods=['get'], detail=False, url_path='test')
    def test(self, request):
        # import time
        # li = ['MLM1410524222', 'MLM1409963889', 'MLM1385889747', 'MLM1385475588', 'MLM1398690832', 'MLM1410689706', 'MLM1410689702', 'MLM1398684151', 'MLM1429665361']
        # for i in li:
        #     tasks.create_listing(i)
        #     time.sleep(1)
        # tasks.update_categories('MLM')
        # from datetime import datetime, timedelta
        # date = datetime.now() - timedelta(days=1)
        # Listing.objects.all().update(update_time=date)
        # date = datetime.now() - timedelta(days=1)
        # SellerTrack.objects.all().update(create_time=date)

        tasks.track_seller()
        return Response({'msg': 'OK'}, status=status.HTTP_200_OK)

    # 添加商品链接
    @action(methods=['post'], detail=False, url_path='create_listing')
    def create_listing(self, request):
        item_id = request.data['item_id']
        is_exist = Listing.objects.filter(item_id=item_id).count()
        if is_exist:
            return Response({'msg': '商品已存在'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        tasks.create_listing(item_id)

        return Response({'msg': '操作成功'}, status=status.HTTP_200_OK)

    # 计算利润
    @action(methods=['post'], detail=False, url_path='calc_profit')
    def calc_profit(self, request):
        id = request.data['id']
        cost = request.data['cost']
        listing = Listing.objects.filter(id=id).first()
        if not listing:
            return Response({'msg': '商品不存在'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        mercado_fee = listing.price * 0.305 if listing.price >= 299 else listing.price * 0.305 + 25
        shipping_fee = 57 if listing.price >= 299 else 79.8
        if not listing.is_free_shipping:
            shipping_fee = 0
        profit = ((listing.price - mercado_fee - shipping_fee) / 3.1 - cost) * 0.99

        from xToolkit import xstring
        listing.profit = xstring.dispose(profit).humanized_amount(compel=True)
        listing.cost = cost
        listing.save()

        return Response({'msg': '操作成功'}, status=status.HTTP_200_OK)


class ListingTrackViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """
    list:
        商品跟踪列表,分页,过滤,搜索,排序
    create:
        商品跟踪新增
    retrieve:
        商品跟踪详情页
    update:
        商品跟踪修改
    destroy:
        商品跟踪删除
    """
    queryset = ListingTrack.objects.all()
    serializer_class = ListingTrackSerializer  # 序列化

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    # filter_fields = ('listing__id', 'health')  # 配置过滤字段
    filterset_fields = {
        'create_time': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'listing__id': ['exact']
    }
    ordering_fields = ('create_time',)  # 配置排序字段


class CategoriesViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    list:
        站点类目列表,分页,过滤,搜索,排序
    create:
        站点类目新增
    retrieve:
        站点类目详情页
    update:
        站点类目修改
    destroy:
        站点类目删除
    """
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer  # 序列化

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('father_id', 'site_id', 'collection', 'has_children')  # 配置过滤字段
    search_fields = ('categ_id', 'name', 't_name')  # 配置搜索字段
    ordering_fields = ('name', 'update_time')  # 配置排序字段

    # 获取类目
    @action(methods=['get'], detail=False, url_path='get_categories')
    def get_categories(self, request):
        father_id = self.request.query_params.get('father_id')
        site_id = self.request.query_params.get('site_id')
        if father_id != '0':
            is_exist = Categories.objects.filter(father_id=father_id, site_id=site_id).count()
            if not is_exist:
                # 如果类目不在数据库里，则发起请求查询并保存
                at = ApiSetting.objects.all().first()
                token = at.access_token
                headers = {
                    'Authorization': 'Bearer ' + token,
                }
                c_url = 'https://api.mercadolibre.com/categories/' + father_id
                resp = requests.get(c_url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    add_list = []
                    path_from_root = ''
                    for p in data['path_from_root']:
                        path_from_root += p['name'] + ' > '

                    if len(data['children_categories']) == 0:
                        cate = Categories.objects.filter(categ_id=father_id, site_id=site_id).first()
                        cate.has_children = False
                        cate.save()
                    for item in data['children_categories']:
                        result = tasks.translate(item['name'])
                        add_list.append(Categories(
                            categ_id=item['id'],
                            father_id=father_id,
                            site_id=site_id,
                            name=item['name'],
                            t_name=result if result else None,
                            path_from_root=path_from_root + item['name'],
                            total_items=item['total_items_in_this_category'],
                            update_time=datetime.now()
                        ))
                    Categories.objects.bulk_create(add_list)
        else:
            # 如果一级目录不存在，则请求数据
            is_exist = Categories.objects.filter(father_id=father_id, site_id=site_id).count()
            if not is_exist:
                tasks.update_categories(site_id)

        queryset = Categories.objects.filter(father_id=father_id, site_id=site_id)
        data_list = []
        for i in queryset:
            data_list.append({
                'id': i.id,
                'categ_id': i.categ_id,
                'father_id': i.father_id,
                'site_id': i.site_id,
                'name': i.name,
                't_name': i.t_name,
                'path_from_root': i.path_from_root,
                'total_items': i.total_items,
                'has_children': i.has_children,
                'collection': i.collection,
                'update_time': i.update_time,
            })
        return Response(data_list, status=status.HTTP_200_OK)

    # 获取热搜关键词
    @action(methods=['get'], detail=False, url_path='get_trends')
    def get_trends(self, request):
        categ_id = self.request.query_params.get('categ_id')
        site_id = self.request.query_params.get('site_id')
        # 如果当天有数据
        today = datetime.now().date()
        queryset = Keywords.objects.filter(update_time__date=today, categ_id=categ_id)
        if queryset:
            query_list = []
            for i in queryset:
                query_list.append({
                    'id': i.id,
                    'categ_id': i.categ_id,
                    'keyword': i.keyword,
                    't_keyword': i.t_keyword,
                    'url': i.url,
                    'rank': i.rank,
                    'status': i.status,
                    'rank_changed': i.rank_changed,
                    'update_time': i.update_time,
                })
            return Response(query_list, status=status.HTTP_200_OK)

        at = ApiSetting.objects.all().first()
        token = at.access_token
        headers = {
            'Authorization': 'Bearer ' + token,
        }
        url = 'https://api.mercadolibre.com/trends/' + site_id + '/' + categ_id
        resp = requests.get(url, headers=headers)
        query_list = []
        if resp.status_code == 200:
            data = resp.json()
            n = 1
            if data:
                add_list = []
                for i in data:
                    kw = Keywords.objects.filter(keyword=i['keyword'], categ_id=categ_id).first()
                    rank_status = 'NEW'
                    rank_changed = 0
                    if kw:
                        if n == kw.rank:
                            rank_status = 'EQ'
                        elif n < kw.rank:
                            rank_status = 'UP'
                            rank_changed = kw.rank - n
                        elif n > kw.rank:
                            rank_status = 'DOWN'
                            rank_changed = n - kw.rank
                        else:
                            rank_status = None
                    add_list.append(Keywords(
                        categ_id=categ_id,
                        keyword=i['keyword'],
                        url=i['url'],
                        rank=n,
                        status=rank_status,
                        rank_changed=rank_changed
                    ))
                    n += 1
                Keywords.objects.filter(categ_id=categ_id).delete()
                Keywords.objects.bulk_create(add_list)

                keywords_data = Keywords.objects.filter(categ_id=categ_id)
                if keywords_data:
                    for i in keywords_data:
                        query_list.append({
                            'id': i.id,
                            'categ_id': i.categ_id,
                            'keyword': i.keyword,
                            't_keyword': i.t_keyword,
                            'url': i.url,
                            'rank': i.rank,
                            'status': i.status,
                            'rank_changed': i.rank_changed,
                            'update_time': i.update_time,
                        })

        return Response(query_list, status=status.HTTP_200_OK)

    # 翻译类目
    @action(methods=['get'], detail=False, url_path='translate')
    def translate(self, request):
        queryset = Categories.objects.filter(t_name=None)
        for i in queryset:
            result = tasks.translate(i.name)
            i.t_name = result
            i.save()

        return Response({'data': 'OK'}, status=status.HTTP_200_OK)


class SellerViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    list:
        卖家列表,分页,过滤,搜索,排序
    create:
        卖家新增
    retrieve:
        卖家详情页
    update:
        卖家修改
    destroy:
        卖家删除
    """
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('site_id', 'level_id', 'collection')  # 配置过滤字段
    search_fields = ('nickname', 'seller_id')  # 配置搜索字段
    ordering_fields = ('registration_date', 'total')  # 配置排序字段

    # 更新卖家详细信息
    @action(methods=['get'], detail=False, url_path='update_seller')
    def update_seller(self, request):
        seller_id = self.request.query_params.get('seller_id')

        seller = Seller.objects.filter(seller_id=seller_id).first()
        tasks.create_or_update_seller(seller.site_id, seller_id)
        return Response({'msg': '操作成功'}, status=status.HTTP_200_OK)

    # 新增卖家，按昵称
    @action(methods=['get'], detail=False, url_path='create_seller')
    def create_seller(self, request):
        seller_info = self.request.query_params.get('seller_info')
        site_id = self.request.query_params.get('site_id')

        at = ApiSetting.objects.all().first()
        token = at.access_token
        headers = {
            'Authorization': 'Bearer ' + token,
        }

        url = 'https://api.mercadolibre.com/sites/' + site_id + '/search?nickname=' + seller_info
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if 'seller' in data:
                seller_id = str(data['seller']['id'])
                tasks.create_or_update_seller(site_id, seller_id)
                return Response({'msg': '操作成功'}, status=status.HTTP_200_OK)
            else:
                return Response({'msg': '卖家不存在，请检查卖家名称'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({'msg': 'api操作不成功'}, status=status.HTTP_406_NOT_ACCEPTABLE)