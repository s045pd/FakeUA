import hashlib

from peewee import *

db = SqliteDatabase('useragents.db') # 初始化数据库


class UAS(Model):
    uid = AutoField(primary_key=True, null=True) # 自增ID
    useragent = TextField(unique=True) # useragent
    software = CharField(null=True) # 软件类型
    engine = CharField(null=True) # 引擎
    types = CharField(null=True) # 硬件类型
    popularity = CharField(null=True) # 通用性

    class Meta:
        database = db # 指定数据库

db.connect() # 连接数据库
db.create_tables([UAS]) # 初始化创建不存在的库


def UserAgent(searchwords, methods='and'):
    """
        {
            "key":[
                "words1",
                "words2"
            ]
        }
    """
    count = 0
    resagent = ''
    if methods not in ['and', 'or']:
        return ''
    methods = '&' if not methods == 'or' else '|'
    whereQuery = f' {methods} '.join([
        f'(UAS.{key} << {str(item)})' for key, item in searchwords.items()
    ])
    try:
        count = UAS.select().where(eval(whereQuery)).order_by(fn.Random()).count()
        resagent = UAS.select().where(eval(whereQuery)).order_by(
            fn.Random()).limit(1)[0].useragent
    except Exception as e:
        pass
    return count, resagent


def UserAgentGroups(colname, limit=10):
    if colname in ['software', 'engine', 'types', 'popularity']: # 判定查询字段是否合法
        target = eval(f'UAS.{colname}') # 取得目标字段类
        return {eval(f'item.{colname}'): item.nums for item in UAS.select(target, fn.COUNT(target).alias('nums')).group_by(target).order_by(fn.COUNT(target).desc()).limit(limit)}


if __name__ == '__main__':
    from pprint import pprint
    print(UserAgent({
        "software": [
            'Android Browser 4.0'
        ]
    }))
    # pprint(UserAgentGroups('engine', 5))
