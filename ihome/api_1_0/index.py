# -*- coding:utf-8 -*-
from . import api
from ihome import db
from ihome.models import *

# 定义蓝图路由
@api.route('/index', methods=['GET', 'POST'])
def index():
    return 'hello'

