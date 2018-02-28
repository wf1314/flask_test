# -*- coding:utf-8 -*-
from ihome.api_1_0 import api
from flask import request, session
import re
from ihome.utils.response_code import RET
from flask import jsonify
import logging
from ihome.utils.re_tool import login_require
from ihome import redis_store, db
from ihome.models import User


@api.route('/users', methods=['POST'])
def register():
    # 获取用户提交数据,手机号,短信验证码,密码
    response_json = request.get_json()
    mobile = response_json.get('mobile')
    sms_code = response_json.get('sms_code')
    password = response_json.get('password')
    # 校验数据完整性
    if not all([mobile, sms_code, password]):
        resp = {
            'errno': RET.DATAERR,
            'errmsg': '数据不完整'
        }
        return jsonify(resp)
    # 验证手机号
    if not re.match(r'1[3456789]\d{9}', mobile):
        resp = {
            'errno': RET.DATAEXIST,
            'errmsg': '手机号已注册'
        }
        return jsonify(resp)

    try:
        # 从redis中读取存储的短信验证码数据
        db_sms_code = redis_store.get('sms_code_' + mobile)

    except Exception as e:
        logging.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': '数据库查询错误'
        }
        return jsonify(resp)
    # 如果验证码为空
    if sms_code is None:
        resp = {
            'errno': RET.DBERR,
            'errmsg': '数据库查询错误'
        }
        return jsonify(resp)
    # 如果用户输入的验证码不等于存储的验证码
    if int(sms_code) != int(db_sms_code):
        resp = {
            'errno': RET.DATAERR,
            'errmsg': '验证码输入错误'
        }
        return jsonify(resp)
    try:
        # 将redis中存储的短信验证码删除
        redis_store.delete('sms_code_' + mobile)
    except Exception as e:
        logging.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': '网络错误'
        }
        return jsonify(resp)

    try:
        # 根据手机号获取用户对象
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:

        logging.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': '数据库查询错误'
        }
        return jsonify(resp)
    # 如果用户存在
    if user:
        resp = {
            'errno': RET.DATAEXIST,
            'errmsg': '用户已存在'
        }
        return jsonify(resp)
    # 向数据库中添加数据
    user = User(name=mobile, mobile=mobile)
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    # 如果报错先进行回滚
    except Exception as e:

        logging.error(e)
        db.session.rollback()
        logging.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': '注册失败'
        }
        return jsonify(resp)

    try:
        # 注册成功后直接跳转到登录成功的页面
        # 向Session中添加数据用于保存用户登录状态
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['mobile'] = mobile

    except Exception as e:
        logging.error(e)
        resp = {
            'errno': RET.LOGINERR,
            'errmsg': '注册失败'
        }
        return jsonify(resp)

    return jsonify(errno=RET.OK, errmsg='注册成功')


@api.route('/sessions', methods=['POST'])
def login():
    # 获取json数据  参数 mobile password
    request_json = request.get_json()
    mobile = request_json.get('mobile')
    password = request_json.get('password')
    # 校验数据完整性
    if not all([mobile, password]):
        resp = {
            'errno': RET.DATAERR,
            'errmsg': '数据不完整'
        }
        return jsonify(resp)
    # 验证手机号
    if not re.match(r'1[3456789]\d{9}', mobile):
        resp = {
            'errno': RET.DATAEXIST,
            'errmsg': '账号有误'
        }
        return jsonify(resp)
    # 获取当前访问的用户的ip地址
    user_ip = request.remote_addr
    try:
        # 从redis中读取用户登录错误的次数
        err_count = redis_store.get('access_' + user_ip)
    except Exception as e:
        logging.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': '数据库查询错误'
        }
        return jsonify(resp)
    # 如果错误次数大于5次
    if err_count and int(err_count) >= 5:
        resp = {
            'errno': RET.REQERR,
            'errmsg': '累计输入错误次数已达最大值'
        }
        return jsonify(resp)

    try:
        # 从数据库中获取当前用户对象
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        logging.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': '数据库查询错误'
        }
        return jsonify(resp)
    # 如果用户不存在或者用户密码输入错误
    if not user or not user.check_password(password):
        # 利用incr记录错误此时 从0开始每次+1
        redis_store.incr('access_' + user_ip)
        # 设置数据的有效期
        redis_store.expire('access_' + user_ip, 3600 * 24)

        resp = {
            'errno': RET.PWDERR,
            'errmsg': '用户名或密码错误'
        }
        return jsonify(resp)

    try:
        # 如果用户存在切密码正确,删除redis中存储的错误次数
        redis_store.delete('access_' + user_ip)
    except Exception as e:
        logging.error(e)

        resp = {
            'errno': RET.DBERR,
            'errmsg': 'redis删除错误'
        }
        return jsonify(resp)

    try:
        # 注册后默认为自动登录后的状态
        # 设置信息保存至Session表示用户已登录
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['mobile'] = mobile

    except Exception as e:
        logging.error(e)
        resp = {
            'errno': RET.LOGINERR,
            'errmsg': '登录失败'
        }
        return jsonify(resp)

    return jsonify(errno=RET.OK, errmsg='登录成功')


@api.route('/sessions', methods=['GET'])
def login_state():
    # 获取用户名
    user_name = session.get('user_name')

    if user_name:
        # 如果用户名存在返回数据,否则显示注册 登录选项
        return jsonify(errno=RET.OK, errmsg='true', data={'name': user_name})

    else:

        return jsonify(errno=RET.SESSIONERR, errmsg='False')


@api.route('/sessions', methods=['DELETE'])
@login_require
def logout():
    # 获取csrf_token信息先进行保存
    csrf_token = session['csrf_token']
    # 清空Session内容
    session.clear()
    # 将csrf_token信息重新设置
    session['csrf_token'] = csrf_token

    return jsonify(errno=RET.OK, errmsg='退出登录成功')
