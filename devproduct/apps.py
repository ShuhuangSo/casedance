from django.apps import AppConfig


class DevproductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'devproduct'

    # 以下为启动代码
    def ready(self):
        import devproduct.signals
