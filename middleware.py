from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponse


class VisitLimitMiddleWare(MiddlewareMixin):
    def process_request(self, request):

        # 系统关闭维护
        if settings.SITE_CLOSE:
            return HttpResponse(content="系统关闭", status=503)

        # 客户端要求最低版本
        required_app_ver = 139
        app_ver = request.META.get("HTTP_APP_VER")

        if app_ver:
            if int(app_ver) < required_app_ver:
                return HttpResponse(content="app版本过低", status=555)