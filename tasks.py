from celery import Celery
from conf import Config
app = Celery('darknet', broker=f'redis://{Config.redis_host}:{Config.redis_port}//')


@app.task()
def SaveToDB(datas, model):
    if datas:
        loger.info(colored(f'数据存储至DB中 [{len(datas)}]', 'yellow'))
        for chunk in list(MakeChunk(datas)):
            model.insert_many(datas).execute()
