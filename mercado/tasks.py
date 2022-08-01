from __future__ import absolute_import
from celery import shared_task
import requests
import random
import time
import json
import urllib
import hashlib
from datetime import datetime, timedelta
from django.utils import dateparse
from bs4 import BeautifulSoup

from mercado.models import ApiSetting, Listing, Seller, ListingTrack, Categories, TransApiSetting

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
                listing_track.rating_average = listing.rating_average
                listing_track.health = listing.health
                listing_track.save()
            time.sleep(1)
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
    time.sleep(1)
    if resp.status_code == 200:
        resp.encoding = "utf-8"
        result = json.loads(resp.text)
        return result['trans_result'][0]['dst']
    else:
        return ''


# 更新卖家详细信息
def update_seller(site_id, seller_id):
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