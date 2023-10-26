from __future__ import absolute_import
from celery import shared_task
import requests
import random
import time
import json
import urllib
import hashlib
import os
from datetime import datetime, timedelta
from django.utils import dateparse
from bs4 import BeautifulSoup
from django.db.models import Sum, Avg, Q

from casedance.settings import MEDIA_ROOT, BASE_DIR
from mercado.models import ApiSetting, Listing, Seller, ListingTrack, Categories, TransApiSetting, SellerTrack, Shop, \
    MLOrder, ShopStock, ShopReport, TransStock, Ship, ShipDetail, MLProduct, CarrierTrack, ExRate, StockLog, \
    FileUploadNotify, ShipAttachment, ShipBox, MLOperateLog
from setting.models import TaskLog

user_agent_list = [

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",

    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",

    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",

    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",

    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",

    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",

    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",

    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",

    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",

    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",

    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",

    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",

    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",

    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",

    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",

    "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) App leWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53"

]
UA = random.choice(user_agent_list)  # 获取随机的User_Agent
main_headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
}
# 商品api获取字段
attributes = 'id,site_id,title,thumbnail,permalink,price,currency_id,start_time,status,health,shipping,tags,seller_id'


# 添加跟踪商品
@shared_task
def create_listing(item_id):
    is_exist = Listing.objects.filter(item_id=item_id).count()
    if is_exist:
        return 'exist'
    at = ApiSetting.objects.all().first()
    token = at.access_token
    headers = {
        'Authorization': 'Bearer ' + token,
    }

    url = 'https://api.mercadolibre.com/items?ids=' + item_id + '&attributes=' + attributes
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()[0]['body']
        listing = Listing()
        listing.item_id = data['id']
        listing.site_id = data['site_id']
        listing.title = data['title']
        listing.image = data['thumbnail']
        listing.link = data['permalink']
        listing.price = data['price']
        listing.currency = data['currency_id']
        listing.start_date = dateparse.parse_datetime(data['start_time'])
        listing.listing_status = data['status']
        listing.health = data['health']
        listing.ship_type = data['shipping']['logistic_type']
        listing.is_free_shipping = data['shipping']['free_shipping']
        listing.is_cbt = 'cbt_item' in data['tags']
        listing.seller_id = data['seller_id']
        listing.update_time = datetime.now()
        listing.save()

        ss = Seller.objects.filter(seller_id=data['seller_id'])
        if not ss:
            # 获取卖家信息
            seller_url = 'https://api.mercadolibre.com/users/' + str(data['seller_id'])
            resp2 = requests.get(seller_url, headers=headers)
            if resp2.status_code == 200:
                seller_data = resp2.json()
                seller = Seller()
                seller.seller_id = seller_data['id']
                seller.nickname = seller_data['nickname']
                seller.registration_date = dateparse.parse_datetime(seller_data['registration_date'])
                seller.site_id = seller_data['site_id']
                seller.link = seller_data['permalink']
                seller.level_id = seller_data['seller_reputation']['level_id']
                seller.total = seller_data['seller_reputation']['transactions']['total']
                seller.canceled = seller_data['seller_reputation']['transactions']['canceled']
                seller.negative = seller_data['seller_reputation']['transactions']['ratings']['negative']
                seller.neutral = seller_data['seller_reputation']['transactions']['ratings']['neutral']
                seller.positive = seller_data['seller_reputation']['transactions']['ratings']['positive']
                seller.save()
                listing.seller_name = seller_data['nickname']
                listing.save()
        else:
            seller = Seller.objects.filter(seller_id=data['seller_id']).first()
            listing.seller_name = seller.nickname
            listing.save()

        # 抓取listing总销量
        resp3 = requests.get(data['permalink'], headers=main_headers)
        if resp3:
            resp3.encoding = "utf-8"
            page = BeautifulSoup(resp3.text, 'html.parser')
            sold = page.find('span', class_='ui-pdp-subtitle')
            import re
            sold_qty = re.findall("\d+", sold.text)
            if sold_qty:
                listing.total_sold = int(sold_qty[0])
                listing.save()

        # 获取评价信息
        review_url = 'https://api.mercadolibre.com/reviews/item/' + item_id
        resp4 = requests.get(review_url, headers=headers)
        if resp4.status_code == 200:
            review_data = resp4.json()
            listing.reviews = review_data['paging']['total']
            listing.rating_average = review_data['rating_average']
            listing.save()
    return 'OK'


# 跟踪商品
@shared_task
def track_listing():
    date = datetime.now().date()
    queryset = Listing.objects.filter(update_time__date__lt=date)
    attributes2 = 'id,title,thumbnail,price,status,health,shipping'
    api_url = 'https://api.mercadolibre.com/items?ids='
    url = ''
    n = 0
    for i in queryset:
        # 拼接item_id
        if n == 0:
            url = api_url + i.item_id
        else:
            url = url + ',' + i.item_id
        n += 1

        if n == 20:
            req_url = url + '&attributes=' + attributes2
            url = ''
            n = 0
            get_listing_info(req_url)

    if n != 0:
        req_url = url + '&attributes=' + attributes2
        get_listing_info(req_url)

    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 9
    task_log.note = '美客多listing跟踪'
    task_log.save()

    return 'OK'


# 获取链接追踪信息
def get_listing_info(url):
    at = ApiSetting.objects.all().first()
    token = at.access_token
    headers = {
        'Authorization': 'Bearer ' + token,
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        add_list = []
        for i in data:
            listing = Listing.objects.filter(item_id=i['body']['id']).first()
            listing.title = i['body']['title']
            listing.image = i['body']['thumbnail']
            listing.price = i['body']['price']
            listing.listing_status = i['body']['status']
            listing.health = i['body']['health']
            listing.ship_type = i['body']['shipping']['logistic_type']
            listing.update_time = datetime.now()
            listing.save()

            # 获取评价信息
            review_url = 'https://api.mercadolibre.com/reviews/item/' + i['body']['id']
            resp4 = requests.get(review_url, headers=headers)
            if resp4.status_code == 200:
                review_data = resp4.json()
                listing.reviews = review_data['paging']['total']
                listing.rating_average = review_data['rating_average']
                listing.save()

            # 爬取销量
            resp2 = requests.get(listing.link, headers=main_headers)
            if resp2:
                resp2.encoding = "utf-8"
                page = BeautifulSoup(resp2.text, 'html.parser')
                sold = page.find('span', class_='ui-pdp-subtitle')
                import re
                sold_qty = re.findall("\d+", sold.text)
                if sold_qty:
                    listing.total_sold = int(sold_qty[0])
                    listing.save()

            # 补充计算昨天当天销量
            lt = ListingTrack.objects.filter(listing=listing,
                                             create_time__date=datetime.now().date() - timedelta(days=1)).first()
            if lt:
                lt.today_sold = listing.total_sold - lt.total_sold
                lt.save()

            is_exits = ListingTrack.objects.filter(listing=listing, create_time__date=datetime.now().date()).count()
            if not is_exits:
                add_list.append(ListingTrack(
                    listing=listing,
                    currency=listing.currency,
                    price=listing.price,
                    total_sold=listing.total_sold,
                    reviews=listing.reviews,
                    rating_average=listing.rating_average,
                    health=listing.health
                ))
            else:
                listing_track = ListingTrack.objects.filter(listing=listing,
                                                            create_time__date=datetime.now().date()).first()
                today_sold = listing.total_sold - listing_track.total_sold
                listing_track.today_sold = today_sold
                listing_track.reviews = listing.reviews
                listing_track.price = listing.price
                listing_track.rating_average = listing.rating_average
                listing_track.health = listing.health
                listing_track.save()
            time.sleep(0.5)
        ListingTrack.objects.bulk_create(add_list)


# 更新一级类目信息
@shared_task
def update_categories(site_id):
    at = ApiSetting.objects.all().first()
    token = at.access_token
    headers = {
        'Authorization': 'Bearer ' + token,
    }

    url = 'https://api.mercadolibre.com/sites/' + site_id + '/categories'
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        for i in data:
            categories = Categories.objects.filter(categ_id=i['id'], site_id=site_id).first()
            # 如果目录存在，则检查需不需要更新
            if categories:
                if categories.name != i['name']:
                    categories.name = i['name']
                    categories.update_time = datetime.now()
                    categories.save()
            else:
                cate_g = Categories()
                cate_g.categ_id = i['id']
                cate_g.father_id = '0'
                cate_g.site_id = site_id
                cate_g.name = i['name']
                t_name = translate(i['name'])
                if t_name:
                    cate_g.t_name = t_name
                cate_g.path_from_root = i['name']
                cate_g.has_children = True
                cate_g.update_time = datetime.now()
                cate_g.save()


# 翻译
def translate(q):
    ta = TransApiSetting.objects.all().first()
    appid = ta.appid  # 填写你的appid
    secretKey = ta.secretKey  # 填写你的密钥
    myurl = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    fromLang = 'auto'  # 原文语种
    toLang = 'zh'  # 译文语种
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign
    resp = requests.get(myurl)
    time.sleep(0.01)
    if resp.status_code == 200:
        resp.encoding = "utf-8"
        result = json.loads(resp.text)
        return result['trans_result'][0]['dst']
    else:
        return ''


# 更新卖家详细信息
def create_or_update_seller(site_id, seller_id):
    at = ApiSetting.objects.all().first()
    token = at.access_token
    headers = {
        'Authorization': 'Bearer ' + token,
    }

    url = 'https://api.mercadolibre.com/sites/' + site_id + '/search?seller_id=' + seller_id
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        seller = Seller.objects.filter(seller_id=seller_id).first()
        if seller:
            seller.level_id = data['seller']['seller_reputation']['level_id']
            seller.total = data['seller']['seller_reputation']['transactions']['total']
            seller.canceled = data['seller']['seller_reputation']['transactions']['canceled']
            seller.negative = data['seller']['seller_reputation']['transactions']['ratings']['negative']
            seller.neutral = data['seller']['seller_reputation']['transactions']['ratings']['neutral']
            seller.positive = data['seller']['seller_reputation']['transactions']['ratings']['positive']
            seller.link = data['seller']['permalink']
            seller.sold_60d = data['seller']['seller_reputation']['metrics']['sales']['completed']
            seller.total_items = data['paging']['total']
            seller.update_time = datetime.now()
            seller.save()
        else:
            seller = Seller()
            seller.seller_id = seller_id
            seller.site_id = site_id
            seller.nickname = data['seller']['nickname']
            seller.registration_date = dateparse.parse_datetime(data['seller']['registration_date'])
            seller.level_id = data['seller']['seller_reputation']['level_id']
            seller.total = data['seller']['seller_reputation']['transactions']['total']
            seller.canceled = data['seller']['seller_reputation']['transactions']['canceled']
            seller.negative = data['seller']['seller_reputation']['transactions']['ratings']['negative']
            seller.neutral = data['seller']['seller_reputation']['transactions']['ratings']['neutral']
            seller.positive = data['seller']['seller_reputation']['transactions']['ratings']['positive']
            seller.link = data['seller']['permalink']
            seller.sold_60d = data['seller']['seller_reputation']['metrics']['sales']['completed']
            seller.total_items = data['paging']['total']
            seller.update_time = datetime.now()
            seller.save()


# 跟踪卖家
@shared_task
def track_seller():
    today = datetime.now().date()
    # 跟踪所有卖家
    queryset = Seller.objects.all()
    at = ApiSetting.objects.all().first()
    token = at.access_token
    headers = {
        'Authorization': 'Bearer ' + token,
    }
    url = 'https://api.mercadolibre.com/sites/'
    for i in queryset:
        resp = requests.get(url + i.site_id + '/search?seller_id=' + i.seller_id, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            # 更新卖家信息
            i.level_id = data['seller']['seller_reputation']['level_id']
            i.total = data['seller']['seller_reputation']['transactions']['total']
            i.canceled = data['seller']['seller_reputation']['transactions']['canceled']
            i.negative = data['seller']['seller_reputation']['transactions']['ratings']['negative']
            i.neutral = data['seller']['seller_reputation']['transactions']['ratings']['neutral']
            i.positive = data['seller']['seller_reputation']['transactions']['ratings']['positive']
            i.link = data['seller']['permalink']
            i.sold_60d = data['seller']['seller_reputation']['metrics']['sales']['completed']
            i.total_items = data['paging']['total']
            i.update_time = datetime.now()
            i.save()

            # 补充计算昨天当天销量
            st = SellerTrack.objects.filter(seller=i, create_time__date=today - timedelta(days=1)).first()
            if st:
                st.today_sold = i.total - st.total
                st.save()

            seller_track = SellerTrack.objects.filter(seller=i, create_time__date=today).first()
            if seller_track:
                seller_track.today_sold = i.total - seller_track.total
                seller_track.negative = i.negative
                seller_track.neutral = i.neutral
                seller_track.positive = i.positive
                seller_track.total_items = i.total_items
                seller_track.save()
            else:
                seller_track = SellerTrack()
                seller_track.seller = i
                seller_track.total = i.total
                seller_track.negative = i.negative
                seller_track.neutral = i.neutral
                seller_track.positive = i.positive
                seller_track.total_items = i.total_items
                seller_track.save()

        time.sleep(0.5)

    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 1
    task_log.note = '美客多seller跟踪'
    task_log.save()

    return 'OK'


# 跟踪运单物流运输
@shared_task
def ship_tracking(num):
    url = 'https://client.morelink56.com/baiduroute/get_routeinfo'
    carrier = 'SHENGDE'

    resp = requests.post(url, {'num': num})
    if resp.status_code == 200:
        data = resp.json()
        if data['message'] == 'SUCCESS':
            if len(data['data']):
                for i in data['data']:
                    is_exist = CarrierTrack.objects.filter(carrier_name=carrier, carrier_number=num, context=i['context']).first()
                    if not is_exist:
                        ct = CarrierTrack()
                        ct.carrier_name = carrier
                        ct.carrier_number = num
                        ct.context = i['context']
                        ct.location = i['location']
                        if i['time']:
                            ct.time = datetime.strptime(i['time'], '%Y-%m-%d %H:%M:%S')
                        if i['optime']:
                            ct.optime = datetime.strptime(i['optime'], '%Y-%m-%d %H:%M:%S')
                        ct.save()
                    else:
                        is_exist.create_time = datetime.now()
                        is_exist.save()
                return 'SUCCESS'
        else:
            return data['message']
    else:
        return '网络异常'


# 批量更新运单物流运输跟踪
@shared_task
def bulk_ship_tracking():
    queryset = Ship.objects.filter(send_from='CN', carrier='盛德物流').filter(Q(s_status='SHIPPED') | Q(s_status='BOOKED'))
    for i in queryset:
        if i.s_number:
            ship_tracking(i.s_number)
            time.sleep(0.2)
    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 14
    task_log.note = '美客多物流跟踪信息更新'
    task_log.save()
    return 'SUCCESS'


# 计算mercado产品销量
@shared_task
def calc_product_sales():
    shops = Shop.objects.filter(warehouse_type='FBM', is_active=True)
    for s in shops:
        is_exist = MLOrder.objects.filter(shop=s).count()
        if not is_exist:
            continue
        shop_stocks = ShopStock.objects.filter(shop=s, is_active=True)
        for st in shop_stocks:
            # 7天销量
            day7 = datetime.now().date() - timedelta(days=7)
            sum_day7 = MLOrder.objects.filter(shop=s,
                                              sku=st.sku,
                                              item_id=st.item_id,
                                              order_time_bj__gte=day7).aggregate(Sum('qty'))
            day7_sold = sum_day7['qty__sum']

            # 15天销量
            day15 = datetime.now().date() - timedelta(days=15)
            sum_day15 = MLOrder.objects.filter(shop=s,
                                               sku=st.sku,
                                               item_id=st.item_id,
                                               order_time_bj__gte=day15).aggregate(Sum('qty'))
            day15_sold = sum_day15['qty__sum']

            # 30天销量
            day30 = datetime.now().date() - timedelta(days=30)
            sum_day30 = MLOrder.objects.filter(shop=s,
                                               sku=st.sku,
                                               item_id=st.item_id,
                                               order_time_bj__gte=day30).aggregate(Sum('qty'))
            day30_sold = sum_day30['qty__sum']

            # 累计销量
            sum_total = MLOrder.objects.filter(shop=s,
                                               sku=st.sku,
                                               item_id=st.item_id, ).aggregate(Sum('qty'))
            total_sold = sum_total['qty__sum']

            # 累计利润
            sum_profit = MLOrder.objects.filter(shop=s,
                                                sku=st.sku,
                                                item_id=st.item_id, ).aggregate(Sum('profit'))
            total_profit = sum_profit['profit__sum']

            # 平均毛利润
            avg_profit = MLOrder.objects.filter(shop=s,
                                                sku=st.sku,
                                                item_id=st.item_id, ).aggregate(Avg('profit'))
            avg_profit = avg_profit['profit__avg']

            # 平均毛利率
            a_profit_rate = MLOrder.objects.filter(shop=s,
                                                   sku=st.sku,
                                                   item_id=st.item_id, ).aggregate(Avg('profit_rate'))
            avg_profit_rate = a_profit_rate['profit_rate__avg']

            from django.db.models import Q
            # 退款率
            refund_count = MLOrder.objects.filter(shop=s,
                                                  sku=st.sku,
                                                  item_id=st.item_id, ).filter(
                Q(order_status='RETURN') | Q(order_status='CASE')).count()
            total_count = MLOrder.objects.filter(shop=s,
                                                 sku=st.sku,
                                                 item_id=st.item_id, ).count()
            if total_count:
                refund_rate = refund_count / total_count
            else:
                refund_rate = 0

            st.day15_sold = day15_sold if day15_sold else 0
            st.day7_sold = day7_sold if day7_sold else 0
            st.day30_sold = day30_sold if day30_sold else 0
            st.total_sold = total_sold if total_sold else 0
            st.total_profit = total_profit if sum_profit else 0
            st.avg_profit = avg_profit if avg_profit else 0
            st.avg_profit_rate = avg_profit_rate if avg_profit_rate else 0
            st.refund_rate = refund_rate
            st.save()

    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 11
    task_log.note = 'FBM销量计算'
    task_log.save()

    return 'OK'


# 计算店铺30天每天累积总销量
@shared_task()
def calc_shop_sale():
    q = Q()
    q.connector = 'OR'
    q.children.append(('order_status', 'FINISHED'))
    q.children.append(('order_status', 'RETURN'))
    q.children.append(('order_status', 'CASE'))

    shops = Shop.objects.filter(warehouse_type='FBM', is_active=True)
    for s in shops:
        add_list = []
        for i in range(30):
            date = datetime.now().date() - timedelta(days=i)
            order_set = MLOrder.objects.filter(order_time__date=date, shop=s).filter(q)
            qty = 0
            amount = 0.0
            profit = 0.0

            for item in order_set:
                qty += item.qty
                amount += item.price
                profit += item.profit

            sr = ShopReport.objects.filter(calc_date=date, shop=s).first()
            if sr:
                sr.qty = qty
                sr.amount = amount
                sr.profit = profit
                sr.save()
            else:
                add_list.append(ShopReport(
                    qty=qty,
                    amount=amount,
                    profit=profit,
                    shop=s,
                    calc_date=date
                ))
        if len(add_list):
            ShopReport.objects.bulk_create(add_list)
    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 13
    task_log.note = 'fbm店铺销量计算'
    task_log.save()

    return 'OK'


# 获取店铺额度
@shared_task()
def get_shop_quota(shop_id):
    shop = Shop.objects.filter(id=shop_id).first()

    # FBM库存统计
    queryset = ShopStock.objects.filter(is_active=True, qty__gt=0, shop__id=shop_id).exclude(p_status='OFFLINE')
    total_amount = 0
    for i in queryset:
        total_amount += (i.unit_cost + i.first_ship_cost) * i.qty

    # 中转仓库存统计
    ts = TransStock.objects.filter(listing_shop=shop.name, is_out=False)
    trans_amount = 0
    for i in ts:
        trans_amount += (i.unit_cost + i.first_ship_cost) * i.qty

    # 在途运单统计,含备货中
    ships = Ship.objects.filter(shop=shop.name).filter(
        Q(s_status='SHIPPED') | Q(s_status='BOOKED') | Q(s_status='PREPARING'))
    onway_amount = 0
    for i in ships:
        onway_amount += i.shipping_fee
        onway_amount += i.extra_fee
        onway_amount += i.products_cost

    # 在途中转运单统计,含备货中
    ship_detail = ShipDetail.objects.filter(Q(ship__s_status='SHIPPED') | Q(ship__s_status='BOOKED') | Q(ship__s_status='PREPARING')).filter(ship__target='TRANSIT')
    for i in ship_detail:
        is_shop_product = MLProduct.objects.filter(shop=shop.name, sku=i.sku).first()
        # 如果是该店铺下的产品
        if is_shop_product:
            onway_amount += (i.unit_cost + i.avg_ship_fee) * i.qty

    used_quota = total_amount + trans_amount + onway_amount
    return used_quota


# 上传美客多订单
@shared_task()
def upload_mercado_order(shop_id, notify_id):
    import warnings
    import re
    import openpyxl

    warnings.filterwarnings('ignore')

    data = MEDIA_ROOT + '/upload_file/order_excel_' + shop_id + '.xlsx'
    wb = openpyxl.load_workbook(data)
    sheet = wb.active

    month_dict = {'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04', 'mayo': '05', 'junio': '06',
                  'julio': '07', 'agosto': '08', 'septiembre': '09', 'octubre': '10', 'noviembre': '11',
                  'diciembre': '12'}

    shop = Shop.objects.filter(id=shop_id).first()
    er = ExRate.objects.filter(currency=shop.currency).first()
    ex_rate = er.value

    # 模板格式检查
    format_checked = True
    if sheet['A3'].value != '# de venta':
        format_checked = False
    if sheet['B3'].value != 'Fecha de venta':
        format_checked = False
    if sheet['C3'].value != 'Estado':
        format_checked = False
    if sheet['I3'].value != 'Cargo por venta e impuestos':
        format_checked = False
    if sheet['J3'].value != 'Costos de envío':
        format_checked = False
    if sheet['L3'].value != 'Total (MXN)':
        format_checked = False
    if sheet['M3'].value != 'Venta por publicidad':
        format_checked = False
    if sheet['N3'].value != 'SKU':
        format_checked = False
    if sheet['O3'].value != '# de publicación':
        format_checked = False
    if sheet['R3'].value != 'Precio unitario de venta de la publicación (MXN)':
        format_checked = False
    if sheet['Y3'].value != 'Comprador':
        format_checked = False
    if sheet['AA3'].value != 'Domicilio':
        format_checked = False
    if sheet['AB3'].value != 'Municipio/Alcaldía':
        format_checked = False
    if sheet['AC3'].value != 'Estado':
        format_checked = False
    if sheet['AD3'].value != 'Código postal':
        format_checked = False
    if sheet['AE3'].value != 'País':
        format_checked = False
    if not format_checked:
        # 修改上传通知
        file_upload = FileUploadNotify.objects.filter(id=notify_id).first()
        file_upload.upload_status = 'ERROR'
        file_upload.desc = '模板格式有误，请检查!'
        file_upload.save()
        return 'ERROR'

    add_list = []
    for cell_row in list(sheet)[3:]:
        qty = cell_row[5].value
        if not qty:
            continue
        sku = cell_row[13].value
        item_id = cell_row[14].value[3:]

        # 如果不在fmb库存中，或者所在店铺不对应，则跳出
        shop_stock = ShopStock.objects.filter(sku=sku, item_id=item_id, shop=shop).first()
        if not shop_stock:
            continue
        first_ship_cost = shop_stock.first_ship_cost
        if not first_ship_cost:
            first_ship_cost = 0

        order_number = cell_row[0].value

        t = cell_row[1].value
        de_locate = [m.start() for m in re.finditer('de', t)]
        day = t[:de_locate[0] - 1]
        if int(day) < 10:
            day = '0' + day
        month = t[de_locate[0] + 3:de_locate[1] - 1]
        year = t[de_locate[1] + 3:de_locate[1] + 7]
        hour = t[de_locate[1] + 8:de_locate[1] + 10]
        min = t[de_locate[1] + 11:de_locate[1] + 13]
        order_time = '%s-%s-%s %s:%s:00' % (year, month_dict[month], day, hour, min)

        bj = datetime.strptime(order_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=14)
        order_time_bj = bj.strftime('%Y-%m-%d %H:%M:%S')

        price = cell_row[17].value if cell_row[17].value else 0
        fees = cell_row[8].value if cell_row[8].value else 0
        postage = cell_row[9].value if cell_row[9].value else 0
        receive_fund = cell_row[11].value if cell_row[11].value else 0
        is_ad = True if cell_row[12].value == 'Sí' else False

        buyer_name = cell_row[24].value
        buyer_address = cell_row[26].value
        buyer_city = cell_row[27].value
        buyer_state = cell_row[28].value
        buyer_postcode = cell_row[29].value
        buyer_country = cell_row[30].value

        profit = (float(
            receive_fund) * 0.99) * ex_rate - shop_stock.unit_cost * qty - shop_stock.first_ship_cost * qty
        profit_rate = profit / (price * ex_rate)
        if profit_rate < 0:
            profit_rate = 0

        order_status = 'FINISHED'
        if cell_row[2].value == 'Cancelada por el comprador':
            order_status = 'CANCEL'
        if cell_row[2].value == 'Paquete cancelado por Mercado Libre':
            order_status = 'CANCEL'
        if cell_row[2].value == 'Devolución en camino':
            order_status = 'RETURN'
        if cell_row[2].value == 'Reclamo cerrado con reembolso al comprador':
            order_status = 'CASE'
        if cell_row[2].value[:8] == 'Devuelto':
            order_status = 'RETURN'

        # 检查同一店铺订单编号是否存在
        ml_order = MLOrder.objects.filter(order_number=order_number, shop=shop).first()
        if not ml_order:
            add_list.append(MLOrder(
                shop=shop,
                platform='MERCADO',
                order_number=order_number,
                order_status=order_status,
                order_time=order_time,
                order_time_bj=order_time_bj,
                qty=qty,
                currency=shop.currency,
                ex_rate=ex_rate,
                price=price,
                fees=fees,
                postage=postage,
                receive_fund=receive_fund,
                is_ad=is_ad,
                sku=sku,
                p_name=shop_stock.p_name,
                item_id=item_id,
                image=shop_stock.image,
                unit_cost=shop_stock.unit_cost * qty,
                first_ship_cost=first_ship_cost * qty,
                profit=profit,
                profit_rate=profit_rate,
                buyer_name=buyer_name,
                buyer_address=buyer_address,
                buyer_city=buyer_city,
                buyer_state=buyer_state,
                buyer_postcode=buyer_postcode,
                buyer_country=buyer_country,
            ))
            shop_stock.qty -= qty
            shop_stock.save()

            # 创建库存日志
            stock_log = StockLog()
            stock_log.shop_stock = shop_stock
            stock_log.current_stock = shop_stock.qty
            stock_log.qty = qty
            stock_log.in_out = 'OUT'
            stock_log.action = 'SALE'
            stock_log.desc = '销售订单号: ' + order_number
            stock_log.user_id = 0
            stock_log.save()
            stock_log.create_time = order_time  # order_time
            stock_log.save()
        else:
            if ml_order.order_status != order_status:
                ml_order.order_status = order_status
                ml_order.receive_fund = receive_fund
                ml_order.profit = profit
                ml_order.save()

                # 如果订单是取消状态，库存增加回来
                if order_status == 'CANCEL':
                    shop_stock.qty += qty
                    shop_stock.save()

                    # 创建库存日志
                    stock_log = StockLog()
                    stock_log.shop_stock = shop_stock
                    stock_log.current_stock = shop_stock.qty
                    stock_log.qty = qty
                    stock_log.in_out = 'IN'
                    stock_log.action = 'CANCEL'
                    stock_log.desc = '取消订单入库, 订单号: ' + order_number
                    stock_log.user_id = 0
                    stock_log.save()
    if len(add_list):
        MLOrder.objects.bulk_create(add_list)

    # 修改上传通知
    file_upload = FileUploadNotify.objects.filter(id=notify_id).first()
    file_upload.upload_status = 'SUCCESS'
    file_upload.desc = '上传成功!'
    file_upload.save()

    return 'SUCESS'


# 上传NOON订单
@shared_task()
def upload_noon_order(shop_id, notify_id):
    import warnings
    import openpyxl
    warnings.filterwarnings('ignore')

    data = MEDIA_ROOT + '/upload_file/order_excel_' + shop_id + '.xlsx'
    wb = openpyxl.load_workbook(data)
    sheet = wb.active

    shop = Shop.objects.filter(id=shop_id).first()
    er = ExRate.objects.filter(currency=shop.currency).first()
    ex_rate = er.value

    # 如果是invoice表
    if sheet['A1'].value == 'Invoice Nr':
        # 模板格式检查
        format_checked = True
        if sheet['A1'].value != 'Invoice Nr':
            format_checked = False
        if sheet['C1'].value != 'Invoice Date':
            format_checked = False
        if sheet['G1'].value != 'Source Document Type':
            format_checked = False
        if sheet['K1'].value != 'Vat Amount':
            format_checked = False
        if sheet['L1'].value != 'Price incl tax':
            format_checked = False
        if sheet['N1'].value != 'Item Nr':
            format_checked = False
        if sheet['O1'].value != 'SKU':
            format_checked = False
        if sheet['P1'].value != 'Partner SKU':
            format_checked = False
        if sheet['S1'].value != 'Customer ID':
            format_checked = False
        if sheet['T1'].value != 'Customer Name':
            format_checked = False
        if sheet['U1'].value != 'Customer City':
            format_checked = False
        if sheet['V1'].value != 'Customer Country':
            format_checked = False
        if not format_checked:
            # 修改上传通知
            file_upload = FileUploadNotify.objects.filter(id=notify_id).first()
            file_upload.upload_status = 'ERROR'
            file_upload.desc = '模板格式有误，请检查!'
            file_upload.save()
            return 'ERROR'

        add_list = []
        for cell_row in list(sheet)[1:]:
            row_type = cell_row[6].value
            # 检查行类型
            if row_type != 'Customer order':
                continue
            if not row_type:
                break

            sku = cell_row[15].value
            item_id = cell_row[14].value[:-2]

            # 如果不在fmb库存中，或者所在店铺不对应，则跳出
            shop_stock = ShopStock.objects.filter(sku=sku, item_id=item_id, shop=shop).first()
            if not shop_stock:
                continue
            first_ship_cost = shop_stock.first_ship_cost
            if not first_ship_cost:
                first_ship_cost = 0

            order_number = cell_row[13].value
            order_time = cell_row[2].value
            # 该字段可能有datetime和str 2种类型, 需要进行判断
            if type(cell_row[2].value) == 'str':
                order_time = cell_row[2].value + ' 00:00:00'

            buyer_name = cell_row[19].value
            buyer_id = cell_row[18].value
            buyer_city = cell_row[20].value
            buyer_country = cell_row[21].value
            VAT = -abs(cell_row[10].value) if cell_row[10].value else 0
            invoice_price = cell_row[11].value
            order_status = 'UNCHECK'

            # 检查同一店铺订单编号是否存在
            ml_order = MLOrder.objects.filter(order_number=order_number, shop=shop).first()
            if not ml_order:
                add_list.append(MLOrder(
                    shop=shop,
                    platform='NOON',
                    order_number=order_number,
                    order_status=order_status,
                    order_time=order_time,
                    qty=1,
                    currency=shop.currency,
                    ex_rate=ex_rate,
                    VAT=VAT,
                    invoice_price=invoice_price,
                    sku=sku,
                    p_name=shop_stock.p_name,
                    item_id=item_id,
                    image=shop_stock.image,
                    unit_cost=shop_stock.unit_cost * 1,
                    first_ship_cost=first_ship_cost * 1,
                    buyer_name=buyer_name,
                    buyer_id=buyer_id,
                    buyer_city=buyer_city,
                    buyer_country=buyer_country,
                ))
                shop_stock.qty -= 1
                shop_stock.save()

                # 创建库存日志
                stock_log = StockLog()
                stock_log.shop_stock = shop_stock
                stock_log.current_stock = shop_stock.qty
                stock_log.qty = 1
                stock_log.in_out = 'OUT'
                stock_log.action = 'SALE'
                stock_log.desc = '销售订单号: ' + order_number
                stock_log.user_id = 0
                stock_log.save()
                stock_log.create_time = order_time  # order_time
                stock_log.save()
        if len(add_list):
            MLOrder.objects.bulk_create(add_list)

    elif sheet['A1'].value == 'item_nr':
        # 模板格式检查
        format_checked = True
        if sheet['A1'].value != 'item_nr':
            format_checked = False
        if sheet['B1'].value != 'partner_sku':
            format_checked = False
        if sheet['C1'].value != 'sku_config':
            format_checked = False
        if sheet['L1'].value != 'country_code':
            format_checked = False
        if sheet['M1'].value != 'item_status':
            format_checked = False
        if sheet['Q1'].value != 'ordered_date':
            format_checked = False
        if sheet['W1'].value != 'currency_code':
            format_checked = False
        if sheet['AC1'].value != 'offer_price':
            format_checked = False
        if sheet['AG1'].value != 'fee_commission':
            format_checked = False
        if sheet['AU1'].value != 'fee_outbound_fbn_v2':
            format_checked = False
        if sheet['AW1'].value != 'payment_due':
            format_checked = False
        if not format_checked:
            return 'ERROR'
        for cell_row in list(sheet)[1:]:
            order_number = cell_row[0].value
            if not order_number:
                break

            # 检查同一店铺订单编号是否存在
            ml_order = MLOrder.objects.filter(order_number=order_number, shop=shop).first()
            if ml_order:
                order_status = cell_row[12].value
                price = cell_row[28].value if cell_row[28].value else 0
                promo_coupon = cell_row[29].value if cell_row[29].value else 0
                fees = cell_row[32].value if cell_row[32].value else 0
                postage = cell_row[46].value if cell_row[46].value else 0
                payment_due = cell_row[48].value if cell_row[48].value else 0
                receive_fund = round(payment_due + ml_order.VAT, 2)
                shipped_date = ''
                delivered_date = ''
                if cell_row[17].value:
                    shipped_date = cell_row[17].value
                    # 该字段可能有datetime和str 2种类型, 需要进行判断
                    if type(cell_row[17].value) == 'str':
                        shipped_date = cell_row[17].value + ' 00:00:00'
                if cell_row[18].value:
                    delivered_date = cell_row[18].value
                    if type(cell_row[17].value) == 'str':
                        delivered_date = cell_row[18].value + ' 00:00:00'

                # 如果不在fmb库存中，或者所在店铺不对应，则跳出
                shop_stock = ShopStock.objects.filter(sku=ml_order.sku, item_id=ml_order.item_id, shop=shop).first()
                if not shop_stock:
                    continue
                first_ship_cost = shop_stock.first_ship_cost
                if not first_ship_cost:
                    first_ship_cost = 0

                if order_status == 'delivered':
                    # 订单送达
                    if ml_order.order_status != 'FINISHED':
                        ml_order.order_status = 'FINISHED'
                        ml_order.price = price
                        ml_order.promo_coupon = promo_coupon
                        ml_order.postage = postage
                        ml_order.fees = fees
                        ml_order.receive_fund = receive_fund
                        if shipped_date:
                            ml_order.shipped_date = shipped_date
                        if delivered_date:
                            ml_order.delivered_date = delivered_date

                        profit = (float(
                            receive_fund) * 0.99) * ex_rate - shop_stock.unit_cost * ml_order.qty - first_ship_cost * ml_order.qty
                        profit_rate = profit / (price * ex_rate)
                        if profit_rate < 0:
                            profit_rate = 0
                        ml_order.profit = profit
                        ml_order.profit_rate = profit_rate
                        ml_order.save()
                elif order_status == 'returned':
                    # 订单退货
                    if ml_order.order_status != 'RETURN':
                        ml_order.order_status = 'RETURN'
                        ml_order.VAT = 0
                        ml_order.price = price
                        ml_order.promo_coupon = promo_coupon
                        ml_order.postage = postage
                        ml_order.fees = fees
                        ml_order.receive_fund = payment_due
                        if shipped_date:
                            ml_order.shipped_date = shipped_date
                        if delivered_date:
                            ml_order.delivered_date = delivered_date

                        profit = (float(
                            payment_due) * 0.99) * ex_rate - shop_stock.unit_cost * ml_order.qty - first_ship_cost * ml_order.qty
                        profit_rate = profit / (price * ex_rate)
                        if profit_rate < 0:
                            profit_rate = 0
                        ml_order.profit = profit
                        ml_order.profit_rate = profit_rate
                        ml_order.save()

                else:
                    continue
            else:
                continue
    else:
        # 修改上传通知
        file_upload = FileUploadNotify.objects.filter(id=notify_id).first()
        file_upload.upload_status = 'ERROR'
        file_upload.desc = '模板格式有误，请检查!'
        file_upload.save()
        return 'ERROR'
    # 修改上传通知
    file_upload = FileUploadNotify.objects.filter(id=notify_id).first()
    file_upload.upload_status = 'SUCCESS'
    file_upload.desc = '上传成功!'
    file_upload.save()
    return 'SUCESS'


# 盛德交运运单
@shared_task()
def sd_place_order(ship_id, data):
    ship = Ship.objects.filter(id=ship_id).first()
    if not ship:
        return {'status': 'error', 'msg': '运单不存在！'}
    if ship.carrier != '盛德物流':
        return {'status': 'error', 'msg': '仅支持盛德物流交运！'}
    if not ship.envio_number:
        return {'status': 'error', 'msg': 'envio号不能为空！'}

    # 交运数据
    payload = {
        'txtconsigneephoto': 'undefined',
        'operNo': '',
        'hkremarks': '',
        'country_code': '墨西哥',
        'd_code': data['d_code'],  # fbm仓库代码
        'fbano': '',
        'address1': data['address1'], # fbm仓库地址
        'zip_code': data['zip_code'],  # fbm仓库邮编
        'channelcode': '',
        'delivertype': '卡派',
        'warehousename': '深圳石岩仓(必须预约)',
        'channeltype2': '墨西哥极速达',
        'jfunit': 'kg',
        'postcode': 'mx',
        'reserveid': data['reserveid'],  # 预约id
        'apptdate': data['apptdate'],  # 预约日期
        'ckyyservice': 1,
        'rsum': 1,
        'invoicelink': '',
        'cargoagency': '',
        'EntrustType': data['EntrustType'],  # 空运
        'tihuotype': '自送货',
        'nid': '03E85014-136E-4E5B-B2F9-751E21FF5D88',  # 公司id,固定
        'khchannel_id': '2498F847-EA54-44EE-9EFF-797BF44AAEF6',  # 不知道，固定
        'warehouseid': data['warehouseid'],  # 仓库id
        'DeliveryTime': data['DeliveryTime'],  # 预约送仓时间
        'LoadingDriver': '',
        'channelway': '',
        'kimsvolume': '',
        'ConsignorContacts': '钟生',
        'ConsignorPhone': '13823289200',
        'ConsignorAddress': '深圳市 福田区 赛格科技园 4栋西  703E',
        'extendoperno': '',
        'khremarks': '',
        'isbx': '否',
        'insure_currency': '',
        'xmai': '',
        'isOtherImporter': 0,
        'importername': '',
        'destination': '',
        'eori': '',
        'address': '',
        'importerid': '',
        'isfba': 'FBM',
        'sellerid': data['sellerid'],  # Seller ID
        'envio': data['envio'],  # fbm入仓号
        'intowarehouseweeks': '',
        'shop': '',
        'cwremark': '',
        'fbl': '',
        'buildtime': '',
        'shippingdate': '',
        'companyname': '',
        'consignee': '',
        'telephone': '',
        'province': '',
        'city': '',
        'yyno': '',
        'po': '',
        'consigneephoto': '',
        'ftype': '箱唛',  # 上传文件类型
        'product': data['product'],  # 品名
        'ProductNature': data['ProductNature'],  # 产品性质，可能多个
        'vat_clear_customs': '无',
        'GoodsNum': ship.total_box,  # 预计箱数
        'yjweight': ship.weight,  # 预计重量
        'yjvolume': round(ship.cbm, 4),  # 预计体积
        'CustomsDeclaration': '无单证',
        'fruit': 1,
        'quantity': ship.total_qty,  # 产品总数量
        'rcid': 'EBCF9B79-2504-49D7-AD07-BE325670DE22',  # 待查看
        'bxjine': 0.00,
        'email': '',
        'valtype': 1,
        'somrequest': '',
        'vat': '',
        'vat_company': '',
        'vat_address': '',
        'vat_contact': '',
        'vat_companyphone': '',
        'eroi': '',
        'eoricompany': '',
        'eoriaddr': '',
        'iskims': '否',
    }
    # 上传附件
    files = {}
    f_id = time.strftime('%Y%m%d%H%M%S')  # 箱唛附件编号

    f_name = ''  #  pdf文件名
    sa_set = ShipAttachment.objects.filter(ship=ship, a_type='BOX_LABEL')
    for i in sa_set:
        extension = i.name.split(".")[-1]
        if extension == 'pdf':
            f_name = i.name
    path = '{batch}_{id}/{name}'.format(batch=ship.batch, id=ship.id, name=f_name)
    book_file = MEDIA_ROOT + '/ml_ships/' + path
    files['txtupload' + f_id] = open(book_file, 'rb')  # 上传箱唛附件

    # 箱唛附件描述信息
    payload['filegrid'] = json.dumps(
        [{"id": f_id, "filename": f_name, "filetype": "箱唛", "size": "2.805KB", "fileurl": ""}],
        ensure_ascii=False)

    p_list = []  # 运单产品列表
    boxes = ShipBox.objects.filter(ship=ship)
    box_num = 0
    num = 0
    for b in boxes:
        sd_set = ShipDetail.objects.filter(ship=ship, box_number=b.box_number)
        box_tag = 1
        for i in sd_set:
            product_pic = MEDIA_ROOT + '/ml_product/' + i.sku + '_100x100.jpg'
            # 上传产品图片
            files['txtimg' + str(num + 1)] = open(product_pic, 'rb')

            p_list.append({
                'ContainerNo': i.ship.batch + '/' + str(box_num + 1),  # 货箱编号
                'ContaineNum': box_tag,  # 件数
                'ContainerWeight': '0.00',
                'ContainerLength': '0.00',
                'ContainerWidth': '0.00',
                'ContainerHeight': '0.00',
                'GoodsSKU': i.brand,  # 品牌
                'EnglishProduct': i.en_name,  # 英文品名
                'ChineseProduct': i.cn_name,  # 中文品名
                'DeclaredValue': i.declared_value,  # 单个产品申报价值(usd)
                'DeclaredNum': i.qty,  # 单箱申报数量
                'Material': i.cn_material,  # 材质
                'Purpose': i.use,  # 用途
                'CustomsCode': i.custom_code,  # 海关编码
                'SalesWebsite': 'https://articulo.mercadolibre.com.mx/MLM-' + i.item_id,  # 销售网址
                'SellingPice': '0.00',
                "PicturesLink": "1",
                "ProductWeight": "0.00",
                "ProductSize": "",
                "ASIN": "无",
                "FNSKU": "无",
                "model": "",
                "netweight": "0.00",
                "roughweight": "0.00",
                "english_material": i.cn_material,  # 英文材质
                "id": num + 1,
                "isdd": "",
                "isdc": "",
                "GoodsSKUtype": "",
                "custom1": "",
                "custom2": "",
                "custom3": "",
                "custom4": "",
                "custom5": ""
            })
            box_tag = 0
            num += 1
        box_num += 1
    payload['tb_GoodsInfo2'] = json.dumps(p_list, ensure_ascii=False)  # 产品列表

    c_path = os.path.join(BASE_DIR, "site_config.json")
    with open(c_path, "r", encoding="utf-8") as f:
        data = json.load(f)  # 加载配置数据
    header = {'Cookie': data['sd_cookies']}
    url = 'http://client.sanstar.net.cn/console/customer_order/newadd?somrequest='

    resp = requests.post(url, files=files, data=payload, headers=header)

    if 'success' in resp.json():
        if resp.json()['success']:
            # 交运成功
            ship.s_number = resp.json()['sono']
            ship.carrier_order_status = 'WAIT'
            ship.carrier_rec_check = 'UNCHECK'
            ship.carrier_order_time = datetime.now()
            ship.save()

            # 创建操作日志
            log = MLOperateLog()
            log.op_module = 'SHIP'
            log.op_type = 'EDIT'
            log.target_type = 'SHIP'
            log.target_id = ship.id
            log.desc = '盛德交运成功，获取运单号-{track_num}'.format(track_num=ship.s_number)
            log.save()
            return {'status': 'success', 'msg': resp.json()['msg']}
        else:
            return {'status': 'error', 'msg': resp.json()['msg']}

    return 'SUCESS'


# 查询盛德运单受理状态
@shared_task()
def query_sd_order_status():
    payload = {
        'model': '下单日期',
        'stime': datetime.now().date() - timedelta(days=14),
        'etime': datetime.now().date(),
        'nid': '03E85014-136E-4E5B-B2F9-751E21FF5D88',
    }
    c_path = os.path.join(BASE_DIR, "site_config.json")
    with open(c_path, "r", encoding="utf-8") as f:
        data = json.load(f)  # 加载配置数据
    header = {'Cookie': data['sd_cookies']}
    url = 'http://client.sanstar.net.cn/Common/IDATA_MK?type=list&proc=cliect_select_BigWaybill'

    resp = requests.post(url, data=payload, headers=header)
    data = []
    if resp.json():
        if 'rows' in resp.json():
            data = resp.json()['rows']

    if len(data):
        ship_set = Ship.objects.filter(s_status='PREPARING', carrier_order_status='WAIT')
        for i in ship_set:
            for d in data:
                if i.s_number == d['sono']:
                    i.carrier_order_status = 'ACCEPTED'
                    i.save()

                    # 创建操作日志
                    log = MLOperateLog()
                    log.op_module = 'SHIP'
                    log.op_type = 'EDIT'
                    log.target_type = 'SHIP'
                    log.target_id = i.id
                    log.desc = '盛德运单已受理'
                    log.save()

    return 'SUCESS'