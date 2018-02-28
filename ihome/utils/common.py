# -*- coding:utf-8 -*-

REDIS_IMG_VERIFY_CODE_MISS_TIME = 300  # redis中存储图片验证码有效期

REDIS_CHIT_VERIFY_CODE_MISS_TIME = 300  # redis中存储短信验证码有效期

CHIT_VERIFY_CODE_MISS_TIME = 5 # 用户获得的验证码的过有效期

QINIU_URL = 'http://p4i89t4of.bkt.clouddn.com/'  # 七牛云存储的url

AREA_INFO_REDIS_EXPIRES = 3600  # 城区信息的redis缓存时间， 单位：秒

HOME_PAGE_MAX_HOUSES = 5  # 首页展示最多的房屋数量

HOME_PAGE_DATA_REDIS_EXPIRES = 7200  # 首页房屋数据的Redis缓存时间，单位：秒

HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 30  # 房屋详情页展示的评论最大数

HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 7200  # 房屋详情页面数据Redis缓存时间，单位：秒

HOUSE_LIST_PAGE_CAPACITY = 2  # 房屋列表页面每页的数量

HOUSE_LIST_PAGE_REDIS_EXPIRES = 3600  # 房屋列表页面数据Redis缓存时间
