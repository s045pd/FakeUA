from peewee import fn
from sanic import Sanic
from sanic.log import logger
from sanic.response import json,redirect
from termcolor import colored
from contextlib import contextmanager
import time

@contextmanager
def checkTimes():
    startTime = time.time()
    yield
    logger.info(
        colored(f'cost times: [{str(round(round(time.time()-startTime,5)*1000,3)) }]ms', 'green'))

from config import conf
from FakeUAdb import UAS

app = Sanic()

@app.route('/')
def handel_request(request):
    return redirect('/fakeua')

@app.route('/fakeua')
async def query_string(request):
    with checkTimes():
        args = request.args
        query = UAS.select()

        keywords = args.get('keywords', [''])[0][:16].lower()
        if keywords:
            query = query.where(UAS.useragent.in_(keywords))

        engine = args.get('engine', [''])[0]
        engine = engine.lower() if len(engine) < 10 and ''.join(
            engine.split()).isalpha() else ''
        if engine:
            query = query.where(UAS.engine.in_(engine))

        types = args.get('types', [''])[0]
        types = types.lower() if len(types) < 10 else ''
        if types:
            query = query.where(UAS.types.in_(types))

        software = args.get('software', [''])[0]
        software = software.lower() if len(software) < 24 else ''
        if software:
            query = query.where(UAS.software.in_(software))

        limit = args.get('limit', [conf.DEFAULT_LIMIT])[0]
        limit = int(limit) if limit.isdigit() else conf.DEFAULT_LIMIT
        limit = limit if limit < conf.MAX_LIMIT + 1  else conf.DEFAULT_LIMIT

        counts = query.count()
        # result = query.order_by(fn.Random()).limit(limit)

        # return json({'total': counts, 'results': result})
        return json({})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=conf.SERVER_PORT)
