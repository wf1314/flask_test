# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_data, etag, urlsafe_base64_encode
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'nwVUtwqaZ8ag9TbzMUclisq15JB4D4L_wOKhMxG4'
secret_key = 'RHDUG-Um3jVE1YuoPAYKgBGJFc7-mTeuWdv1PvGQ'


def storage(file_data):
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'ihome'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)
    # 要上传文件的本地路径
    ret, info = put_data(token, None, file_data)
    print(info)
    print ret

    if info.status_code == 200:
        # 表示上传成功， 返回文件名
        # 我们上传成功之后, 需要在别的页面显示图像, 因此需要返回图像名
        return ret.get("key")
    else:
        # 表示上传失败
        raise Exception("上传失败")
        # http://ozcxm6oo6.bkt.clouddn.com/FnTUusE1lgSJoCccE2PtYIt0f7i3

if __name__ == '__main__':
    # 打开图片数据
    # rb: 以二进制读
    with open("./adv01.jpg", "rb") as f:
        # 读取图片数据二进制数据
        file_data = f.read()
        # print file_data
        # 上传图片书记到七牛云
        result = storage(file_data)
        # result 就存储的是图片名. 将来就可以再程序中调用显示
        print result
