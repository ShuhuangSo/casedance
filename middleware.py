from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponse


class VisitLimitMiddleWare(MiddlewareMixin):
    def process_request(self, request):

        # 系统关闭维护
        if settings.SITE_CLOSE:
            return HttpResponse(content="系统关闭", status=503)