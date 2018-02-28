# -*- coding:utf-8 -*-
from . import api
from ihome.utils.captcha.captcha import captcha # 导入图片验证码duixiang
from ihome import redis_store
from flask import jsonify, make_response, request
import logging
from ihome.utils.response_code import RET
from ihome.utils.common import REDIS_IMG_VERIFY_CODE_MISS_TIME,\
    REDIS_CHIT_VERIFY_CODE_MISS_TIME,CHIT_VERIFY_CODE_MISS_TIME
from ihome.models import User
from ihome.libs.yuntongxun.SendTemplateSMS import CCP # 导入云通讯类
import random


@api.route('/verify_codes/<code_id>')
def get_verify_code(code_id):
    # 拆包获取验证码的名字,验证码以及图片,
    name, verify_code, img_file = captcha.generate_captcha()
    try:
        # 　讲验证码暂时存储到redis中，存储时间为300s
        redis_store.setex('verify_code_' + code_id, REDIS_IMG_VERIFY_CODE_MISS_TIME, verify_code)
    except Exception as e:
        # 如果保存存储日志
        logging.error(e)
        # 返回json数据给前端页面
        resp = {
            'errno': RET.DBERR,
            'errmsg': '添加redis失败'
        }
        return jsonify(resp)

    # 获取响应对象
    response = make_response(img_file)
    # 将响应格式改为图片
    response.headers['Content-Type'] = 'image/jpg'

    return response


@api.route('/sms_codes/<re(r"1[3456789]\d{9}"):phone>')
def get_sms_code(phone):
    # 通过get请求传入的参数获取用户输入的验证码,以及自动生成的验证码id
    verify_code = request.args.get('verify_code')
    verify_code_id = request.args.get('verify_code_id')
    print verify_code
    print verify_code_id
    # 校验数据完整性
    if not all([verify_code, verify_code_id]):
        resp = {
            'errno': RET.NODATA,
            'errmsg': '数据不完整'
        }
        return jsonify(resp)

    try:
        # 查询该验证码id 是否有对应的验证码
        res = redis_store.get('verify_code_' + verify_code_id)
    except Exception as e:
        # 如果报错写入日志
        logging.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': '数据库查询错误'
        }
        return jsonify(resp)
    # 如果返回值为空则表示验证码没有查到
    if res is None:
        resp = {
            'errno': RET.NODATA,
            'errmsg': '验证码已过期'
        }
        return jsonify(resp)

    try:
        # 从redis中删除对应的键值(查询出的结果已经保存在了res中所以可以删除后在比较是否输入正确)
        redis_store.delete('verify_code_' + verify_code_id)
    except Exception as e:
        logging.error(e)

    # 将验证码和用户输入的验证码都转换为小写然后进行比较
    if res.lower() != verify_code.lower():
        resp = {
            'errno': RET.DATAERR,
            'errmsg': '验证码错误'
        }
        return jsonify(resp)

    try:
        # 根据手机号查询对应用户是否已注册
        user = User.query.filter_by(mobile=phone).first()

    except Exception as e:
        logging.error(e)
    else:
        # 如果用户已注册返回错误信息
        if user:
            resp = {
                'errno': RET.DATAEXIST,
                'errmsg': '手机号已注册'
            }
            return jsonify(resp)
    # 生成6为随机验证码
    sms_code = '%06d' % random.randint(0, 999999)

    try:
        # 将验证码存储到redis中
        redis_store.setex('sms_code_' + phone, REDIS_CHIT_VERIFY_CODE_MISS_TIME, sms_code)
    except Exception as e:
        # 返回错误信息
        logging.error(e)
        resp = {
            'errno': RET.DATAERR,
            'errmsg': 'redis添加失败'
        }
        return jsonify(resp)

    # 创建云通讯ccp对象
    ccp = CCP()
    # 向对应号码发送指定验证码又想起为5分钟
    status_code = ccp.sendTemplateSMS(phone, [sms_code, CHIT_VERIFY_CODE_MISS_TIME], 1)
    # 如果返回码为000000则表示短信发送成功
    if status_code == '000000':
        resp = {
            'errno': RET.OK,
            'errmsg': '短信发送成功'
        }
        return jsonify(resp)
    else:
        # 否则失败
        resp = {
            'errno': RET.THIRDERR,
            'errmsg': '短信发送失败'
        }
        return jsonify(resp)
