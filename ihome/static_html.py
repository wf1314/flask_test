# -*- coding:utf-8 -*-
from flask import Blueprint,current_app,make_response
from flask_wtf.csrf import generate_csrf
# 创建蓝图对象
static_request = Blueprint('static_request',__name__)

@static_request.route('/<re(".*"):html>', methods=['GET', 'POST'])
def index(html):
    # 如果为空返回首页
    if not html:

        html = 'html/index.html'
    # favicon.ico为网页小图标
    elif html != 'favicon.ico':

        html = 'html/' + html
    # 生成csrf
    csrf_token = generate_csrf()
    # 显示静态文件
    response = current_app.send_static_file(html)
    #设置ｃｓｒｆ
    response.set_cookie('csrf_token',csrf_token)

    return response