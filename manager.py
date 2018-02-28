# -*- coding:utf-8 -*-
from flask_script import Manager # 用于添加终端命令
from flask_migrate import Migrate,MigrateCommand # 用于数据库迁移
from ihome import create_app


app,db = create_app('develop') # 通过拆包获取函数返回值
manager = Manager(app) # 创建manager对象
Migrate(app,db)
manager.add_command('db',MigrateCommand) # 添加迁移命令


if __name__ == '__main__':
    manager.run()