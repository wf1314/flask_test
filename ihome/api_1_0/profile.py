# -*- coding:utf-8 -*-
import logging
from ihome.models import User
from ihome.api_1_0 import api
from ihome.utils.re_tool import login_require
from flask import request,jsonify,g,session
from ihome.utils.response_code import RET
from ihome.utils.img_storage import storage # 导入七牛云存储函数
from ihome import db
from ihome.utils.common import QINIU_URL


@api.route('/users/avatar', methods=['POST'])
@login_require
def set_user_avatar():
    """上传头像"""
    # 获取表单提交的头像数据
    avatar = request.files.get('avatar')
    # 如果没有则表示用户未选择图片直接点击了上传
    if not avatar:
        resp = {
            'errno': RET.IOERR,
            'errmsg': '未上传头像'
        }
        return jsonify(resp)

    try:
        # 获取图片的内容
        image_data = avatar.read()
        # 获取图片的名称
        image_name = storage(image_data)
    except Exception as e:
        logging.error(e)
        resp = {
            'errno': RET.IOERR,
            'errmsg': '头像上传失败'
        }
        return jsonify(resp)
    try:
        # 通过g变量获取用户id
        user_id = g.user_id
        # user = User.query.filter_by(id=user_id).first()
        # user.avatar_url = image_name
        # db.session.add(user)
        # 将用户表中的头像数据更改为新的图片名称
        User.query.filter_by(id=user_id).update({'avatar_url':image_name})

        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        resp = {
            'errno': RET.DBERR,
            'errmsg': '数据库查询错误'
        }
        return jsonify(resp)
    # 拼接图片的链接
    avatar_url = QINIU_URL + image_name

    return jsonify(errno=RET.OK,errmsg='头像上传成功',data={'avatar_url':avatar_url})

@api.route("/users/name", methods=["PUT"])
@login_require
def change_user_name():
    """修改用户名"""
    # 通过g变量获取用户id
    user_id = g.user_id
    # 获取json数据
    req_data = request.get_json()
    # 如果没有数据表示数据不完整
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 获取用户提交的用户名
    name = req_data.get("name")
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg="名字不能为空")

    try:
        # 更新用户名为新用户名
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="设置用户错误")
    # 更改session中保存的用户名
    session["user_name"] = name
    return jsonify(errno=RET.OK, errmsg="OK", data={"name": name})


@api.route("/users", methods=["GET"])
@login_require
def get_user_profile():
    """获取个人信息"""
    user_id = g.user_id
    # 查询数据库获取个人信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")
    # 如果用户不存在
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")
    # 返回数据库数据
    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())

@api.route("/users/auth", methods=["POST"])
@login_require
def set_user_auth():
    """保存实名认证信息"""
    user_id = g.user_id

    # 获取参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 获取用户提交的真是姓名和身份证号
    real_name = req_data.get("real_name")
    id_card = req_data.get("id_card")

    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        # 更新数据库内容
        User.query.filter_by(id=user_id, real_name=None, id_card=None)\
            .update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户实名信息失败")

    return jsonify(errno=RET.OK, errmsg="OK")


@api.route("/users/auth", methods=["GET"])
@login_require
def get_user_auth():
    """获取用户 的实名认证信息"""
    user_id = g.user_id

    # 在数据库中查询信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户实名信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.auth_to_dict())