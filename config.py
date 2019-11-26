class Config(object):
    
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100
    SERVER_PORT = 80

    name = 'spider'
    maxConnections = 20

    fakeHeader = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }

    status = {'success': 0, 'failed': 0, 'total': 0, 'updated': 0}
    defaultstatus = {'success': 0, 'failed': 0, 'total': 0, 'updated': 0}

    mysql_or_sqlite = 1
    mysql_host = '127.0.0.1'
    mysql_port = 32769
    mysql_usr = 'root'
    mysql_pass = 'root'

    redis_host = '127.0.0.1'
    redis_port = 32768

    mongoURI = 'mongodb://root:4030aoii1033@localhost:32770/lianjia?authSource=admin'

    db = 'work'

    exportfunc = ['json', 'excel']

    FAKEHEADER = {
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "referer": "http://www.mafengwo.cn/",
        "accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01"
    }  # 默认伪造headers

    POOLS = {}  # 数据池
    TASKS = set()  # 任务池
    DATANUMS = 0
    MAXNUMS = 0
    LIMIT = 10  # 并发限制
    PERPAGE = 50


conf = Config
