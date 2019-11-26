

from log import info,warning,error,success
import trio
import asks

asks.init('trio')

class spider(object):

    def __init__(self, *args, **kwargs):
        
        self.datas = {}


    async def getTypesL1(self):
        """
            取得一级分类
        """
        url = "https://developers.whatismybrowser.com/useragents/explore/"
        resp = await spiderSession.get(url)
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



    def run(self):
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        loger.error(colored(e, 'red'))
    finally:
        SaveJson(POOLS, 'POOLS.json')

