from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
import requests
import openpyxl
import time
import random
import json
import urllib
import hashlib
from datetime import datetime, timedelta
from django.db.models import Sum

from mercado.models import Listing, ListingTrack, Categories, ApiSetting, TransApiSetting, Keywords, Seller, \
    SellerTrack, MLProduct, Shop, ShopStock, Ship, ShipDetail, ShipBox, Carrier
from mercado.serializers import ListingSerializer, ListingTrackSerializer, CategoriesSerializer, SellerSerializer, \
    SellerTrackSerializer, MLProductSerializer, ShopSerializer, ShopStockSerializer, ShipSerializer, \
    ShipDetailSerializer, ShipBoxSerializer, CarrierSerializer
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
        #
        # Keywords.objects.filter(categ_id='MLM').update(update_time=date)

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
        # 如果目录id是整站, 则请求整站数据
        if categ_id in ['MLM', 'MLC', 'MLB']:
            url = 'https://api.mercadolibre.com/trends/' + site_id
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
                        t_keyword = kw.t_keyword
                    else:
                        t_keyword = tasks.translate(i['keyword'])
                    add_list.append(Keywords(
                        categ_id=categ_id,
                        keyword=i['keyword'],
                        t_keyword=t_keyword,
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


class SellerTrackViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    list:
        卖家跟踪列表,分页,过滤,搜索,排序
    create:
        卖家跟踪新增
    retrieve:
        卖家跟踪详情页
    update:
        卖家跟踪修改
    destroy:
        卖家跟踪删除
    """
    queryset = SellerTrack.objects.all()
    serializer_class = SellerTrackSerializer  # 序列化

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    # filter_fields = ('listing__id', 'health')  # 配置过滤字段
    filterset_fields = {
        'create_time': ['gte', 'lte', 'exact', 'gt', 'lt'],
        'seller__id': ['exact']
    }
    ordering_fields = ('create_time',)  # 配置排序字段


class MLProductViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """
    list:
        ML产品列表,分页,过滤,搜索,排序
    create:
        ML产品新增
    retrieve:
        ML产品详情页
    update:
        ML产品修改
    destroy:
        ML产品删除
    """
    queryset = MLProduct.objects.all()
    serializer_class = MLProductSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('p_status', 'site', 'shop')  # 配置过滤字段
    search_fields = ('sku', 'p_name', 'label_code', 'upc', 'item_id')  # 配置搜索字段
    ordering_fields = ('create_time', 'sku', 'item_id')  # 配置排序字段

    # ML产品批量上传
    @action(methods=['post'], detail=False, url_path='bulk_upload')
    def bulk_upload(self, request):
        import warnings
        warnings.filterwarnings('ignore')

        data = request.data
        wb = openpyxl.load_workbook(data['excel'])
        sheet = wb['上传模板']

        add_list = []
        if sheet.max_row <= 1:
            return Response({'msg': '表格不能为空'}, status=status.HTTP_202_ACCEPTED)

        for cell_row in list(sheet)[1:]:
            row_status = cell_row[0].value and cell_row[1].value and cell_row[2].value
            if not row_status:
                continue

            # 检查型号是否已存在
            is_exist = MLProduct.objects.filter(sku=cell_row[0].value.strip()).count()
            if is_exist:
                continue

            sku = cell_row[0].value
            p_name = cell_row[1].value
            upc = cell_row[2].value
            item_id = cell_row[3].value
            label_code = cell_row[4].value
            site = cell_row[5].value
            shop = cell_row[6].value
            unit_cost = cell_row[7].value
            if not type(unit_cost) in [float, int]:
                unit_cost = 0
            weight = cell_row[8].value
            if not type(weight) in [float, int]:
                weight = 0
            length = cell_row[9].value
            if not type(length) in [float, int]:
                length = 0
            width = cell_row[10].value
            if not type(width) in [float, int]:
                width = 0
            heigth = cell_row[11].value
            if not type(heigth) in [float, int]:
                heigth = 0
            first_ship_cost = cell_row[12].value
            if not type(first_ship_cost) in [float, int]:
                first_ship_cost = 0
            custom_code = cell_row[13].value
            cn_name = cell_row[14].value
            en_name = cell_row[15].value
            brand = cell_row[16].value
            declared_value = cell_row[17].value
            if not type(declared_value) in [float, int]:
                declared_value = 0
            cn_material = cell_row[18].value
            en_material = cell_row[19].value
            use = cell_row[20].value
            buy_url = cell_row[21].value
            sale_url = cell_row[22].value
            refer_url = cell_row[23].value

            add_list.append(MLProduct(
                sku=sku,
                p_name=p_name,
                upc=upc,
                item_id=item_id,
                label_code=label_code,
                site=site,
                shop=shop,
                unit_cost=unit_cost,
                weight=weight,
                length=length,
                width=width,
                heigth=heigth,
                first_ship_cost=first_ship_cost,
                custom_code=custom_code,
                cn_name=cn_name,
                en_name=en_name,
                brand=brand,
                declared_value=declared_value,
                cn_material=cn_material,
                en_material=en_material,
                use=use,
                buy_url=buy_url,
                sale_url=sale_url,
                refer_url=refer_url
            ))
        MLProduct.objects.bulk_create(add_list)

        return Response({'msg': '成功上传'}, status=status.HTTP_200_OK)

    # ML产品图片上传
    @action(methods=['post'], detail=False, url_path='image_upload')
    def image_upload(self, request):
        data = request.data
        product = MLProduct.objects.filter(id=data['id']).first()
        if not product:
            return Response({'msg': '产品不存在'}, status=status.HTTP_202_ACCEPTED)

        path = 'media/ml_product/' + product.sku
        pic = data['pic']
        content = pic.chunks()
        with open(path, 'wb') as f:
            for i in content:
                f.write(i)
        product.image = 'ml_product/' + product.sku
        product.save()

        return Response({'msg': '成功上传'}, status=status.HTTP_200_OK)


class ShopViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        FBM店铺列表,分页,过滤,搜索,排序
    create:
        FBM店铺新增
    retrieve:
        FBM店铺详情页
    update:
        FBM店铺修改
    destroy:
        FBM店铺删除
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('warehouse_type', 'shop_type', 'site', 'is_active')  # 配置过滤字段
    search_fields = ('name', 'seller_id', 'nickname')  # 配置搜索字段
    ordering_fields = ('create_time', 'total_profit', 'total_weight')  # 配置排序字段


class ShopStockViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """
    list:
        店铺库存列表,分页,过滤,搜索,排序
    create:
        店铺库存新增
    retrieve:
        店铺库存详情页
    update:
        店铺库存修改
    destroy:
        店铺库存删除
    """
    queryset = ShopStock.objects.all()
    serializer_class = ShopStockSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('shop', 'p_status', 'is_active', 'is_collect')  # 配置过滤字段
    search_fields = ('sku', 'p_name', 'label_code', 'upc', 'item_id')  # 配置搜索字段
    ordering_fields = ('create_time', 'item_id', 'qty', 'day15_sold', 'day30_sold', 'total_sold', 'total_profit',
                       'total_weight', 'total_cbm', 'stock_value')  # 配置排序字段

    # ML test data
    @action(methods=['get'], detail=False, url_path='test_data')
    def test_data(self, request):
        shop = Shop.objects.get(id=1)
        for i in range(30):
            stock = ShopStock()
            stock.sku = 'MD200' + str(i)
            stock.p_name = '华尔兹皮套' + str(i)
            stock.p_status = 'NORMAL'
            stock.shop = shop
            stock.save()

        return Response({'msg': '成功上传'}, status=status.HTTP_200_OK)


class ShipViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        头程运单列表,分页,过滤,搜索,排序
    create:
        头程运单新增
    retrieve:
        头程运单详情页
    update:
        头程运单修改
    destroy:
        头程运单删除
    """
    queryset = Ship.objects.all()
    serializer_class = ShipSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('s_status', 'shop', 'target', 'ship_type', 'carrier', 'target_FBM')  # 配置过滤字段
    search_fields = ('s_number', 'batch', 'envio_number', 'note')  # 配置搜索字段
    ordering_fields = ('create_time', 'book_date')  # 配置排序字段

    # 创建运单
    @action(methods=['post'], detail=False, url_path='create_ship')
    def create_ship(self, request):
        shop = request.data['shop']
        target = request.data['target']
        ship_type = request.data['ship_type']
        carrier = request.data['carrier']
        end_date = request.data['end_date']
        ship_date = request.data['ship_date']
        note = request.data['note']
        ship_detail = request.data['ship_detail']

        batch = 'P{time_str}'.format(time_str=time.strftime('%m%d'))

        ship = Ship()
        ship.s_status = 'PREPARING'
        ship.batch = batch
        ship.shop = shop
        ship.target = target
        ship.ship_type = ship_type
        ship.carrier = carrier
        if end_date:
            ship.end_date = end_date
        if ship_date:
            ship.ship_date = ship_date
        ship.note = note
        ship.save()

        # 创建运单详情
        for i in ship_detail:
            product = MLProduct.objects.filter(sku=i['sku']).first()
            if product:
                sd = ShipDetail()
                sd.ship = ship
                sd.s_type = i['s_type']
                sd.qty = i['qty']
                sd.note = i['note']
                sd.sku = i['sku']
                sd.p_name = product.p_name
                sd.label_code = product.label_code
                sd.upc = product.upc
                sd.item_id = product.item_id
                sd.custom_code = product.custom_code
                sd.cn_name = product.cn_name
                sd.en_name = product.en_name
                sd.brand = product.brand
                sd.declared_value = product.declared_value
                sd.cn_material = product.cn_material
                sd.en_material = product.en_material
                sd.use = product.use
                sd.image = product.image
                sd.unit_cost = product.unit_cost
                sd.weight = product.weight
                sd.length = product.length
                sd.width = product.width
                sd.heigth = product.heigth
                sd.save()

        return Response({'msg': '成功创建运单'}, status=status.HTTP_200_OK)

    # 运单发货
    @action(methods=['post'], detail=False, url_path='send_ship')
    def send_ship(self, request):
        ship_id = request.data['id']
        ship_note = request.data['note']
        ship_detail = request.data['ship_shipDetail']

        for i in ship_detail:
            if not i['qty']:
                # 发货数量为0的删除
                ShipDetail.objects.filter(id=i['id']).delete()
                continue
            sd = ShipDetail.objects.filter(id=i['id']).first()
            sd.qty = i['qty']
            sd.box_number = i['box_number']
            sd.note = i['note']
            sd.save()

        ship = Ship.objects.filter(id=ship_id).first()
        if ship_note:
            ship.note = ship_note
        ship.s_status = 'SHIPPED'
        # 总箱数
        box_qty = ShipBox.objects.filter(ship=ship).count()
        ship.total_box = box_qty

        sum_weight = ShipBox.objects.filter(ship=ship).aggregate(Sum('weight'))
        ship.weight = sum_weight['weight__sum']

        # 总数量
        result = ShipDetail.objects.filter(ship=ship).aggregate(Sum('qty'))
        ship.total_qty = result['qty__sum']

        # 总体积cbm
        sum_cbm = ShipBox.objects.filter(ship=ship).aggregate(Sum('cbm'))
        ship.cbm = sum_cbm['cbm__sum']

        ship.save()

        return Response({'msg': '成功发货!'}, status=status.HTTP_200_OK)

    # 计算运单数量
    @action(methods=['get'], detail=False, url_path='calc_ships')
    def calc_ships(self, request):
        pre_qty = Ship.objects.filter(s_status='PREPARING').count()
        shipped_qty = Ship.objects.filter(s_status='SHIPPED').count()
        booked_qty = Ship.objects.filter(s_status='BOOKED').count()
        return Response({'pre_qty': pre_qty, 'shipped_qty': shipped_qty, 'booked_qty': booked_qty}, status=status.HTTP_200_OK)


class ShipDetailViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    list:
        运单详情列表,分页,过滤,搜索,排序
    create:
        运单详情新增
    retrieve:
        运单详情详情页
    update:
        运单详情修改
    destroy:
        运单详情删除
    """
    queryset = ShipDetail.objects.all()
    serializer_class = ShipDetailSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('ship', 'box_number', 's_type')  # 配置过滤字段
    search_fields = ('sku', 'p_name', 'label_code', 'upc', 'item_id')  # 配置搜索字段
    ordering_fields = ('create_time', 'qty')  # 配置排序字段


class ShipBoxViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    list:
        包装箱列表,分页,过滤,搜索,排序
    create:
        包装箱新增
    retrieve:
        包装箱详情页
    update:
        包装箱修改
    destroy:
        包装箱删除
    """
    queryset = ShipBox.objects.all()
    serializer_class = ShipBoxSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('ship', )  # 配置过滤字段
    search_fields = ('box_number', 'carrier_box_number')  # 配置搜索字段
    ordering_fields = ('item_qty', 'box_number', 'id')  # 配置排序字段# 创建运单

    # add box
    @action(methods=['post'], detail=False, url_path='add_shipbox')
    def add_shipbox(self, request):
        ship_id = request.data['ship']
        box_number = request.data['box_number']
        length = float(request.data['length'])
        width = float(request.data['width'])
        heigth = float(request.data['heigth'])
        weight = request.data['weight']
        carrier_box_number = request.data['carrier_box_number']
        note = request.data['note']

        ship = Ship.objects.filter(id=ship_id).first()
        if ship:
            box = ShipBox()
            box.ship = ship
            box.box_number = box_number
            box.length = length
            box.width = width
            box.heigth = heigth
            box.weight = weight
            box.carrier_box_number = carrier_box_number
            box.note = note

            cbm = length * width * heigth / 1000000
            box.cbm = cbm
            size_weight = length * width * heigth / 6000
            box.size_weight = size_weight
            box.save()
        return Response({'msg': '成功新增包装箱!'}, status=status.HTTP_200_OK)

    # edit box
    @action(methods=['put'], detail=False, url_path='update_shipbox')
    def update_shipbox(self, request):
        box_id = request.data['id']
        box_number = request.data['box_number']
        length = float(request.data['length'])
        width = float(request.data['width'])
        heigth = float(request.data['heigth'])
        weight = request.data['weight']
        carrier_box_number = request.data['carrier_box_number']
        note = request.data['note']

        box = ShipBox.objects.filter(id=box_id).first()
        box.box_number = box_number
        box.length = length
        box.width = width
        box.heigth = heigth
        box.weight = weight
        box.carrier_box_number = carrier_box_number
        box.note = note

        cbm = length * width * heigth / 1000000
        box.cbm = cbm
        size_weight = length * width * heigth / 6000
        box.size_weight = size_weight
        box.save()

        return Response({'msg': '包装箱已更新!'}, status=status.HTTP_200_OK)

class CarrierViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    list:
        物流商列表,分页,过滤,搜索,排序
    create:
        物流商新增
    retrieve:
        物流商详情页
    update:
        物流商修改
    destroy:
        物流商删除
    """
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('name', )  # 配置过滤字段
    search_fields = ('name', )  # 配置搜索字段
    ordering_fields = ('od_num', 'id')  # 配置排序字段