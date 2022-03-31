from django.apps import AppConfig


class SaleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sale'

    # 以下为启动代码
    def ready(self):
        import sale.signals