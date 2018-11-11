

import json
import logging
import math
import os
import re
import sys
import time
from pprint import pprint
from urllib.parse import quote, urljoin

import asks
import trio
from pyquery import PyQuery as jq
from stem import Signal
from stem.connection import connect
from termcolor import colored

from FakeUAdb import UAS

asks.init('trio')  # 初始化trio
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
spiderSession = asks.Session(connections=LIMIT)
spiderSession.headers = FAKEHEADER
spiderSession.timeout_manager


logging.basicConfig(
    format="[%(asctime)s] >>> %(levelname)s  %(name)s: %(message)s", level=logging.INFO)  # 初始化日志输出格式，级别
loger = logging.getLogger('FakeUA')  # 初始化一个日志对象
try:
    controller = connect()
    controller.authenticate()
except Exception as e:
    loger.error(colored('请检测您的Tor端口','red'))
    exit()


async def getTypesL1():
    """
        取得一级分类
    """
    url = "https://developers.whatismybrowser.com/useragents/explore/"
    resp = await spiderSession.get(url)
    # listing-by-field-name > li:nth-child(1) > h2 > a
    # listing-by-field-name > li:nth-child(2) > h2 > a
    async with trio.open_nursery() as nursery:
        for item in jq(resp.text)("#listing-by-field-name > li > h2 > a").items():
            types = item.text().strip().replace(' ', '_').lower()
            POOLS[types] = {}
            nursery.start_soon(
                getTypesL2, POOLS[types], types, urljoin(url, item.attr('href')))

async def getTypesL2(target, types, href):
    """
        取得二级分类
    """
    loger.info(colored(f'fetching {href}', 'yellow'))
    resp = await spiderSession.get(href)
    async with trio.open_nursery() as nursery:
        for item in jq(resp.text)("body > div.content-base > section > div > table > tbody > tr").items():
            name = item(
                'td:nth-child(1)>a').text().strip().replace(' ', '_').lower()
            target[name] = {}
            url = urljoin(href, item('td:nth-child(1)>a').attr('href'))
            nums = int(item('td:nth-child(2)').text().strip())
            target[name]['url'] = url
            target[name]['nums'] = nums
            target[name]['UA_list'] = []
            for page in range(1, math.ceil(nums/PERPAGE)+1):
                TASKS.add('__'.join([
                    types,
                    name,
                    f"{url}{page}"
                ]))

async def getUAs():
    global MAXNUMS
    """
        爬行任务调度
    """
    limit = trio.CapacityLimiter(LIMIT)
    while TASKS:
        MAXNUMS = len(list(TASKS))
        loger.info(colored(f'当前任务量:{MAXNUMS}', 'red'))
        await trio.sleep(1)
        async with trio.open_nursery() as nursery:
            for item in list(TASKS):
                nursery.start_soon(getUAsitem, item, limit)

async def getUAsitem(detals, limit):
    global DATANUMS
    global MAXNUMS

    """
        获取单个任务
    """
    types, name, url = detals.split('__')
    target = POOLS[types][name]['UA_list']
    async with limit:
        try:
            loger.info(colored(f'fetching -> {url}', 'yellow'))
            resp = await spiderSession.get(url, timeout=5, retries=3)
            LocalDatas = []
            for item in jq(resp.text)(
                    "body > div.content-base > section > div > table > tbody > tr").items():
                datas = {
                    # 'uid':'',
                    'useragent': item('td.useragent').text(),
                    # 'href': item('td.useragent>a').attr('href'),
                    'software': item('td:nth-child(2)').attr('title'),
                    'engine': item('td:nth-child(3)').text(),
                    'types': item('td:nth-child(4)').text(),
                    'popularity': item('td:nth-child(5)').text()
                }
                loger.info(
                    '[' +
                    colored(DATANUMS,'green')+
                    '/'+
                    colored(MAXNUMS,'yellow')+
                    '/'+
                    colored(str(len(target)), 'blue') +
                    ']' +
                    colored('->', 'blue').join([
                        colored(types, 'red'),
                        colored(name, 'red'),
                        colored(datas["useragent"], 'green')
                    ]))
                target.append(datas)
                LocalDatas.append(datas)
            SaveToDB(LocalDatas,UAS)
            TASKS.remove(detals)
            DATANUMS +=1
            MAXNUMS -=1
        except KeyboardInterrupt:
            raise
        except Exception as e:
            loger.error(colored(e, 'red'))
            NewID()

def NewID():
    controller.signal(Signal.NEWNYM)
    loger.error(colored('切换线路', 'red'))

def SaveJson(datas, filename):
    """
        Json数据存储
    """
    if not datas:
        return
    loger.info(colored(f'文件存储至 {filename}', 'yellow'))
    with open(filename, 'w') as f:
        f.write(json.dumps(datas, indent=4, ensure_ascii=False))

def MakeChunk(datas,length=100):
    for item in range(0, math.ceil(len(datas)/length)):
        yield datas[item*length:(item+1)*length]

def SaveToDB(datas,model):
    # data_source = []
    data_source = datas
    # for tk, td in datas.items():
    #     for nk,nd in td.items():
    #         data_source.extend(nd['UA_list'])
    if data_source:
        loger.info(colored(f'数据存储至DB中 [{len(data_source)}]', 'yellow'))
        for chunk in list(MakeChunk(data_source)):
            model.insert_many(data_source).execute()

def main():
    """
        主逻辑
    """
    while True:
        try:
            trio.run(getTypesL1)
            break
        except Exception:
            NewID()
    trio.run(getUAs)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        loger.error(colored(e, 'red'))
    finally:
        SaveJson(POOLS, 'POOLS.json')
        # SaveToDB(POOLS, UAS)
