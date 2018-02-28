# -*- coding:utf-8 -*-
import redis

class Config(object):
    # 数据库基本配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/ihome2'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # import os,base64
    # 生成随机秘钥
    # base64.b64encode(os.urandom(32))

    # 设置秘钥
    SECRET_KEY = 'hHTbkPtfOaV7uwT5S0ktkz18jXtUxMa9VY1PMEGs9PA='

    # 配置redis的数据
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 配置session存储到redis中
    PERMANENT_SESSION_LIFETIME = 86400  # 单位是秒, 设置session过期的时间
    SESSION_TYPE = 'redis'  # 指定存储session的位置为redis
    SESSION_USE_SIGNER = True  # 对数据进行签名加密, 提高安全性
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置redis的ip和端口


class DevelopConfig(Config):
    """开发模式"""
    DEBUG = True

class OfficialConfig(Config):
    """正式模式"""

    # SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/ihome'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    pass

# 你应该能看懂这个字典
config_dict = {
    'develop':DevelopConfig,
    'official':OfficialConfig,
}