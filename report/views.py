from datetime import datetime, timedelta

from casedance.settings import BASE_URL
from product.models import ProductExtraInfo, Product
from report.models import SalesReport, StockReport, CustomerReport, ProductReport
from report.serializers import SalesReportSerializer, StockReportSerializer, CustomerReportSerializer, \
    ProductReportSerializer
from rest_framework import viewsets, mixins, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from sale.models import OrderDetail, Customer
from store.models import Store, Stock, StockLog
from report import tasks


class SalesReportViewSet(mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    list:
        销量统计
    """
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportSerializer  # 序列化

    filter_backends = (DjangoFilterBackend,)  # 过滤
    filterset_fields = {
        'sale_date': ['gte', 'lte', 'exact', 'gt', 'lt'],
    }

    @action(methods=['get'], detail=False, url_path='test')
    def test(self, request):
        import random
        qt1 = SalesReport.objects.filter(series='华尔兹001')
        for i in qt1:
            i.qty = random.randint(50, 70)
            i.amount = random.randint(500, 1000)
            i.save()
        qt2 = SalesReport.objects.filter(series='华尔兹002')
        for i in qt2:
            i.qty = random.randint(80, 110)
            i.amount = random.randint(1000, 1500)
            i.save()
        return Response({'msg': '更新成功'}, status=status.HTTP_200_OK)

    # 统计今天销售量
    @action(methods=['get'], detail=False, url_path='calc_today_sales')
    def calc_today_sales(self, request):
        today = datetime.now().date()
        order_set = OrderDetail.objects.filter(order__create_time__date=today,
                                               order__order_status='FINISHED')
        total_qty = 0
        total_amount = 0
        for i in order_set:
            total_qty += i.qty
            total_amount += i.qty * i.sold_price
        series_set = ProductExtraInfo.objects.filter(type='SERIES')
        series_sale_list = []
        for s in series_set:
            qt = order_set.filter(product__series=s.name)
            qty = 0
            amount = 0.0
            for i in qt:
                qty += i.qty
                amount += i.qty * i.sold_price
            series_sale_list.append({
                'name': s.name,
                'qty': qty,
                'amount': amount
            })

        return Response({'total_qty': total_qty,
                         'total_amount': total_amount,
                         'series_sale_list': series_sale_list
                         }, status=status.HTTP_200_OK)

    # 统计过去60天销售量
    @action(methods=['get'], detail=False, url_path='calc_sales')
    def calc_sales(self, request):
        tasks.calc_total_sale()

        return Response({'msg': '更新成功'}, status=status.HTTP_200_OK)


class StockReportViewSet(mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    list:
        库存统计
    """
    queryset = StockReport.objects.all()
    serializer_class = StockReportSerializer  # 序列化

    filter_backends = (DjangoFilterBackend,)  # 过滤
    filterset_fields = {
        'stock_date': ['gte', 'lte', 'exact'],
    }

    # 统计过去60天库存
    @action(methods=['get'], detail=False, url_path='calc_60d_stock')
    def calc_60d_stock(self, request):
        series_set = ProductExtraInfo.objects.filter(type='SERIES')
        today = datetime.now().date()
        # 当前库存
        for s in series_set:
            qt = Stock.objects.filter(product__series=s.name)
            total_qty = 0
            total_amount = 0.0
            for i in qt:
                total_qty += i.qty
                total_amount += i.qty * i.product.unit_cost
            stock_report = StockReport.objects.filter(stock_date=today, series=s.name).first()
            if stock_report:
                stock_report.amount = total_amount
                stock_report.qty = total_qty
                stock_report.save()
            else:
                sr = StockReport()
                sr.amount = total_amount
                sr.qty = total_qty
                sr.series = s.name
                sr.stock_date = today
                sr.save()

            # 过去60天库存
            for i in range(60):
                date = datetime.now().date() - timedelta(days=i + 1)  # from yesterday

                sl = StockLog.objects.filter(create_time__date=date, product__series=s.name)
                q = Q()
                q.connector = 'OR'
                q.children.append(('op_type', 'M_IN'))
                q.children.append(('op_type', 'B_IN'))
                in_stock = sl.filter(q)
                in_qty = 0
                in_amount = 0.0
                for item in in_stock:
                    in_qty += item.qty
                    in_amount += item.qty * item.product.unit_cost

                q2 = Q()
                q2.connector = 'OR'
                q2.children.append(('op_type', 'M_OUT'))
                q2.children.append(('op_type', 'S_OUT'))
                out_stock = sl.filter(q2)
                out_qty = 0
                out_amount = 0.0
                for item in out_stock:
                    out_qty += item.qty
                    out_amount += item.qty * item.product.unit_cost

                stock_report2 = StockReport.objects.filter(stock_date=date, series=s.name).first()
                # next day stock
                stock_report_next = StockReport.objects.filter(stock_date=date + timedelta(days=1),
                                                               series=s.name).first()
                if stock_report2:
                    stock_report2.amount = stock_report_next.amount + out_amount - in_amount
                    stock_report2.qty = stock_report_next.qty + out_qty - in_qty
                    stock_report2.save()
                else:
                    sr = StockReport()
                    sr.amount = stock_report_next.amount + out_amount - in_amount
                    sr.qty = stock_report_next.qty + out_qty - in_qty
                    sr.series = s.name
                    sr.stock_date = date
                    sr.save()

        return Response({'msg': '更新成功'}, status=status.HTTP_200_OK)

    # 统计当前库存
    @action(methods=['get'], detail=False, url_path='calc_current_stock')
    def calc_current_stock(self, request):
        series_set = ProductExtraInfo.objects.filter(type='SERIES')
        series_data = []
        for s in series_set:
            qt = Stock.objects.filter(product__series=s.name)
            total_qty = 0
            total_amount = 0.0
            for i in qt:
                total_qty += i.qty
                total_amount += i.qty * i.product.unit_cost
            series_data.append({
                'name': s.name,
                'qty': total_qty,
                'amount': total_amount
            })

        store_set = Store.objects.all()
        store_data = []
        all_qty = 0
        all_amount = 0.0
        for s in store_set:
            qt2 = Stock.objects.filter(store=s)
            total_qty2 = 0
            total_amount2 = 0.0
            for i in qt2:
                total_qty2 += i.qty
                total_amount2 += i.qty * i.product.unit_cost
            store_data.append({
                'name': s.store_name,
                'qty': total_qty2,
                'amount': total_amount2
            })
            all_qty += total_qty2
            all_amount += total_amount2

        return Response({'series_data': series_data,
                         'store_data': store_data,
                         'total_qty': all_qty,
                         'total_amount': all_amount}, status=status.HTTP_200_OK)


class CustomerReportViewSet(mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """
    list:
        客户销量统计报告
    """
    queryset = CustomerReport.objects.all()
    serializer_class = CustomerReportSerializer  # 序列化

    filter_backends = (DjangoFilterBackend,)  # 过滤
    filterset_fields = {
        'calc_date': ['gte', 'lte', 'exact'],
    }

    # 统计客户60天销量
    @action(methods=['get'], detail=False, url_path='calc_customer_report')
    def calc_customer_report(self, request):
        tasks.calc_customer_report()
        return Response({'msg': '更新成功'}, status=status.HTTP_200_OK)

    # 统计客户累计销量
    @action(methods=['post'], detail=False, url_path='calc_total')
    def calc_total(self, request):
        start_date = request.data['start_date']
        end_date = request.data['end_date']

        customers = Customer.objects.filter(is_active=True)
        sale_list = []
        for cs in customers:
            cr = CustomerReport.objects.filter(calc_date__gte=start_date, customer=cs).filter(calc_date__lte=end_date)
            total_qty = 0
            total_amount = 0.0
            for i in cr:
                total_qty += i.qty
                total_amount += i.amount
            sale_list.append({
                'name': cs.company_name,
                'total_qty': total_qty,
                'total_amount': total_amount
            })
        from operator import itemgetter
        sale_list.sort(key=itemgetter('total_qty'), reverse=True)

        return Response({'data': sale_list[:10]}, status=status.HTTP_200_OK)


class ProductReportViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    list:
        统计产品每天销量
    """
    queryset = ProductReport.objects.all()
    serializer_class = ProductReportSerializer  # 序列化

    filter_backends = (DjangoFilterBackend,)  # 过滤
    filterset_fields = {
        'calc_date': ['gte', 'lte', 'exact'],
    }

    # 统计60天产品每天销量
    @action(methods=['get'], detail=False, url_path='calc_product_sale')
    def calc_product_sale(self, request):
        tasks.calc_product_sale()
        return Response({'msg': '更新成功'}, status=status.HTTP_200_OK)

    # 统计产品累计销量
    @action(methods=['post'], detail=False, url_path='calc_total')
    def calc_total(self, request):
        start_date = request.data['start_date']
        end_date = request.data['end_date']

        q = Q()
        q.connector = 'OR'
        q.children.append(('status', 'ON_SALE'))
        q.children.append(('status', 'CLEAN'))
        q.children.append(('status', 'PRIVATE'))
        products = Product.objects.filter(q)

        sale_list = []
        for p in products:
            pr = ProductReport.objects.filter(calc_date__gte=start_date, product=p).filter(calc_date__lte=end_date)
            total_qty = 0
            total_amount = 0.0
            for i in pr:
                total_qty += i.qty
                total_amount += i.amount
            sale_list.append({
                'id': p.id,
                'image': BASE_URL + p.image.url if p.image.url else '',
                'sku': p.sku,
                'name': p.p_name,
                'total_qty': total_qty,
                'total_amount': total_amount
            })
        from operator import itemgetter
        sale_list.sort(key=itemgetter('total_qty'), reverse=True)

        return Response({'data': sale_list[:20]}, status=status.HTTP_200_OK)