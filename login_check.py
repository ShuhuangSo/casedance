from mercado.models import MLOperateLog


# 自定义jwt token返回格式
def jwt_response_payload_handler(token, user=None, request=None):
    # 获取用户的访问的ip地址
    ip = request.META.get("REMOTE_ADDR")

    # 创建登录日志
    log = MLOperateLog()
    log.op_module = 'SYSTEM'
    log.op_type = 'CREATE'
    log.desc = '登录系统, 登录设备IP: {ip}'.format(ip=ip)
    log.user = user
    log.save()
    return {'code': 100,
            'token': token,
            'user': user.username,
            }