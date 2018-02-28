# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_dict,Config
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
import redis
import logging
from logging.handlers import RotatingFileHandler
from utils.re_tool import RegexConverter


# 设置日志等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)



db = SQLAlchemy()
redis_store = None

def create_app(config_key):
    # 创建app对象
    app = Flask(__name__)
    # 加载配置项
    app.config.from_object(config_dict[config_key])
    # 添加自定义转换器
    app.url_map.converters['re'] = RegexConverter
    # 开启csrf保护
    CSRFProtect(app)
    # 将cookie中的ses sion信息同步到redis中,需要进行配置
    Session(app)
    # 将app参数传给db
    db.init_app(app)
    global redis_store
    # 创建redis数据库操作对象
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

    from ihome.api_1_0 import api
    from ihome.static_html import static_request
    # 注册蓝图
    app.register_blueprint(api,url_prefix='/api/v1_0')
    app.register_blueprint(static_request)

    return app,db