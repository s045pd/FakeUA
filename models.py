import datetime
import hashlib
import json

import pymysql
from peewee import *

from conf import config
from peewee import __exception_wrapper__

db = None

class RetryOperationalError(object):

    def execute_sql(self, sql, params=None, commit=True):
        try:
            cursor = super(RetryOperationalError, self).execute_sql(
                sql, params, commit)
        except OperationalError:
            if not self.is_closed():
                self.close()
            with __exception_wrapper__:
                cursor = self.cursor()
                cursor.execute(sql, params or ())
                if commit and not self.in_transaction():
                    self.commit()
        return cursor


class RetryMySQLDatabase(RetryOperationalError, MySQLDatabase):
    pass

if config.mysql_or_sqlite:
    Links = {
        'host': config.mysql_host,
        'port': config.mysql_port,
        'user': config.mysql_usr,
        'password': config.mysql_pass,

    }
    try:
        con = pymysql.connect(**Links)
        with con.cursor() as cursor:
            cursor.execute(
                f'create database {config.db} character set UTF8mb4 collate utf8mb4_bin')
        con.close()
    except pymysql.err.ProgrammingError as e:
        if '1007' in str(e):
            pass
    except Exception as e:
        raise e
    Links['database'] = config.db
    db = RetryMySQLDatabase(**Links, charset='utf8mb4')
else:
    db = SqliteDatabase(config.db)

class UAS(Model):
    uid = AutoField(primary_key=True, null=True)  # 自增ID
    useragent = TextField(unique=True)  # useragent
    software = CharField(null=True)  # 软件类型
    engine = CharField(null=True)  # 引擎
    types = CharField(null=True)  # 硬件类型
    popularity = CharField(null=True)  # 通用性

    class Meta:
        database = db  # 指定数据库


db.connect()  # 连接数据库
db.create_tables([UAS])  # 初始化创建不存在的库
