# -*- coding:utf-8 -*-
from flask import Blueprint  # 导入蓝图扩展

api = Blueprint('api',__name__)  # 创建蓝图

import index,handle_verify,passport,profile,house,order

@api.after_request
def after_request(response):
    """设置默认的响应报文格式为application/json"""
    # 如果响应报文response的Content-Type是以text开头，则将其改为默认的json类型
    if response.headers.get("Content-Type").startswith("text"):
        response.headers["Content-Type"] = "application/json"
    return response