from django.apps import AppConfig


class BonusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bonus'

    # 以下为启动代码
    def ready(self):
        import bonus.signals
