# -*- coding:utf-8 -*-
from werkzeug.routing import BaseConverter
from flask import session,jsonify,g
from functools import wraps
from  response_code import RET

class RegexConverter(BaseConverter):

    def __init__(self,url_map,*args):

        super(RegexConverter,self).__init__(url_map)

        self.regex = args[0]


def login_require(func):

    @wraps(func)
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id')

        if user_id:
            g.user_id = user_id
            return func(*args,**kwargs)
        else:
            resp = {
                'errno': RET.SESSIONERR,
                'errmsg': '用户未登录'
            }
            return jsonify(resp)

    return wrapper