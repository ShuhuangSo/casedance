from django.apps import AppConfig


class MercadoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mercado'

    # 以下为启动代码
    def ready(self):
        import mercado.signals