# -*- coding: UTF-8 -*-

from CCPRestSDK import REST
import ConfigParser
import logging
# 主帐号
accountSid = '8aaf07086178588a01618c60bf500519'

# 主帐号Token
accountToken = '6ebf559d1e89466083261fd16c60dfb8'

# 应用Id
appId = '8aaf07086178588a01618c60bfb00520'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


class CCP(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CCP, cls).__new__(cls,*args, **kwargs)
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)

        return cls._instance

    def sendTemplateSMS(self,to, datas, tempId):

        try:
            result = self.rest.sendTemplateSMS(to, datas, tempId)
        except Exception as e:
            logging.error(e)
            raise e

        return result.get('statusCode')



# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id

def sendTemplateSMS(to, datas, tempId):
    # 初始化REST SDK
    rest = REST(serverIP, serverPort, softVersion)
    rest.setAccount(accountSid, accountToken)
    rest.setAppId(appId)

    result = rest.sendTemplateSMS(to, datas, tempId)
    for k, v in result.iteritems():

        if k == 'templateSMS':
            for k, s in v.iteritems():
                print '%s:%s' % (k, s)
        else:
            print '%s:%s' % (k, v)


            # sendTemplateSMS(手机号码,内容数据,模板Id)


if __name__ == '__main__':
    sendTemplateSMS('17863856808', ['987876', 5], 1)
