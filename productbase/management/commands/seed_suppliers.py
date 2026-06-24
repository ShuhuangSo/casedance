import random
from django.core.management.base import BaseCommand
from productbase.models import Supplier, ProductSeries


SUPPLIER_NAMES = [
    "深圳华强北电子", "义乌小商品城", "广州白云皮具", "东莞虎门服装",
    "杭州四季青女装", "北京中关村数码", "上海七浦路服饰", "成都荷花池百货",
    "武汉汉正街批发", "南京夫子庙商贸", "重庆朝天门市场", "西安康复路批发",
    "郑州银基商贸城", "沈阳五爱市场", "济南泺口服装城", "福州台江农贸市场",
    "昆明螺蛳湾商贸", "长沙高桥大市场", "南昌洪城大市场", "合肥城隍庙市场",
    "石家庄南三条批发", "太原服装城", "贵阳市西路商业街", "南宁和平商场",
    "兰州东部市场", "呼和浩特国贸商城", "银川商城", "西宁义乌商贸城",
    "拉萨八廓商城", "乌鲁木齐边疆商贸城",
]

SERIES_NAMES = [
    ("苹果系列", 15.0), ("华为系列", 12.0), ("三星系列", 11.0),
    ("小米系列", 8.0), ("OPPO系列", 9.5), ("vivo系列", 10.0),
    ("平板保护套", 5.0), ("手机壳通用款", 3.5), ("耳机配件", 2.0),
    ("数据线系列", 1.5), ("充电器系列", 4.0), ("钢化膜系列", 1.0),
]


class Command(BaseCommand):
    help = "生成 30 条供应商测试数据，含部分收藏和随机系列"

    def handle(self, *args, **options):
        created_suppliers = 0
        created_series = 0

        for i, name in enumerate(SUPPLIER_NAMES):
            is_favorite = i < 8  # 前 8 个为收藏
            contact_person = f"联系人{random.choice('赵钱孙李周吴郑王')}{i+1:02d}"
            phone = f"138{random.randint(10000000, 99999999)}"
            wechat = f"wx_{name[:4]}_{i+1}"

            supplier, sup_created = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    "is_favorite": is_favorite,
                    "purchase_channel": random.choice(["1688", "淘宝", "拼多多", "线下批发", "亚马逊"]),
                    "link_url": f"https://shop{i+1}.example.com",
                    "contact_person": contact_person,
                    "phone": phone,
                    "wechat": wechat,
                    "qq": f"{random.randint(100000000, 999999999)}",
                    "address": f"{random.choice(['广东省', '浙江省', '北京市', '上海市', '四川省'])}测试地址{i+1}号",
                }
            )
            if sup_created:
                created_suppliers += 1

            # 随机分配 1~4 个系列
            num_series = random.randint(1, 4)
            for series_name, price in random.sample(
                SERIES_NAMES, min(num_series, len(SERIES_NAMES))
            ):
                _, ser_created = ProductSeries.objects.get_or_create(
                    supplier=supplier,
                    name=series_name,
                    defaults={"price": price + random.uniform(-2, 3)},
                )
                if ser_created:
                    created_series += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"完成：新增供应商 {created_suppliers} 条，新增产品系列 {created_series} 条"
            )
        )
