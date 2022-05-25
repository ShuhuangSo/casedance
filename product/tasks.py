from __future__ import absolute_import
from celery import shared_task
import requests
from datetime import datetime
import time
import random
from bs4 import BeautifulSoup

from product.models import DeviceBrand, DeviceModel
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
headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.gsmarena.com',
    'Referer': 'https://fdn.gsmarena.com/'
}
base_url = "https://www.gsmarena.com/"


# 爬取品牌列表
@shared_task
def get_brands():
    resp = requests.get(base_url, headers=headers)
    resp.encoding = "utf-8"

    # 品牌
    page = BeautifulSoup(resp.text, 'html.parser')
    table = page.find('div', class_='brandmenu-v2 light l-box clearfix')
    brands = table.find_all('li')
    all_list = []
    for b in brands:
        b_link = b.find('a')['href']  # 品牌link
        b_name = b.text  # 品牌name

        # 检查品牌是否存在，存在不添加
        is_exist = DeviceBrand.objects.filter(brand_name=b_name).count()
        if is_exist:
            continue
        all_list.append(DeviceBrand(
            brand_name=b_name,
            link=base_url + b_link
        ))
    DeviceBrand.objects.bulk_create(all_list)
    return 'OK'


# 爬取手机型号信息(首次抓取使用)
@shared_task
def get_device_models():
    brand = DeviceBrand.objects.filter(brand_name='Wiko').first()
    list_url = brand.link  # 品牌产品列表第一页链接

    # 第一页产品列表
    list_resp = requests.get(list_url, headers=headers)
    list_resp.encoding = "utf-8"
    list_page = BeautifulSoup(list_resp.text, 'html.parser')

    # 创建所有列表页面链接
    product_pages = list_page.find('div', class_='nav-pages')
    link_list = [list_url]  # 第一页链接加入列表
    if product_pages:
        page_links = product_pages.find_all('a')
        # 第二页开始的所有页面链接
        for i in page_links:
            link = i['href']
            link_list.append(base_url + link)

    for li in link_list:
        get_list_models(brand.brand_name, li)
        time.sleep(1)

    return 'OK'


# 获取最近更新的手机型号
@shared_task
def check_new_models():
    brands = DeviceBrand.objects.all()
    for b in brands:
        get_list_models(b.brand_name, b.link)
        time.sleep(1)

    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 3
    task_log.note = '同步手机型号'
    task_log.save()
    return '手机型号已同步'


# 获取手机型号参数
@shared_task
def update_spec():
    dms = DeviceModel.objects.filter(model='Galaxy M12').order_by('-create_time').first()
    # dms = DeviceModel.objects.filter(announced=None).order_by('-create_time')[:1]
    # for d in dms:
    #     get_models_info(d.id)
        # time.sleep(1)
    get_models_info(dms.id)
    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 4
    task_log.note = '同步手机参数'
    task_log.save()
    return '手机参数已同步'


# 爬取型号详细信息
@shared_task
def get_models_info(id):
    dm = DeviceModel.objects.get(id=id)
    # 获取型号信息详情
    s = requests.session()
    s.headers = headers
    resp = s.get(dm.link)
    # resp = requests.get(dm.link, headers=headers)
    resp.encoding = "utf-8"

    page = BeautifulSoup(resp.text, 'html.parser')
    specs_list = page.find('div', id='specs-list')
    launch = specs_list.find_all('table')[1]
    # 发布日期
    announced = launch.find('td', attrs={'data-spec': 'year'}).text
    # 状态
    status = launch.find('td', attrs={'data-spec': 'status'}).text
    body = specs_list.find_all('table')[2]
    # 尺寸
    dimensions = body.find('td', attrs={'data-spec': 'dimensions'}).text
    # 重量
    weight = body.find('td', attrs={'data-spec': 'weight'}).text

    dm.announced = announced
    dm.status = status
    dm.dimensions = dimensions
    dm.weight = weight
    dm.create_time = datetime.now()
    dm.save()

    return 'OK'


# 获取所有型号
def get_list_models(brand_name, url):
    list_resp = requests.get(url, headers=headers)
    list_page = BeautifulSoup(list_resp.text, 'html.parser')
    list_table = list_page.find('div', class_='section-body')
    products = list_table.find_all('li')
    add_list = []
    for p in products:
        title = p.text  # 型号名称
        img = p.find('img')['src']  # 型号图片链接
        link = base_url + p.find('a')['href']  # 型号信息详情链接

        # 型号不存在才创建
        is_exist = DeviceModel.objects.filter(model=title).count()
        if not is_exist:
            add_list.append(DeviceModel(
                brand=brand_name,
                model=title,
                image=img,
                link=link,
            ))
    if len(add_list):
        DeviceModel.objects.bulk_create(add_list)
