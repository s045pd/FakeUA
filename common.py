import copy
import os
import time
from contextlib import contextmanager

import moment

from conf import config
from log import info


@contextmanager
def checkTimes(level=3):
    timeStart = time.time()
    yield
    info(f'cost times: {round(time.time()-timeStart,level)}s')


def checkCount(func):
    def checker(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            config.status['success'] += 1
            return res
        except Exception:
            config.status['failed'] += 1
            raise
    return checker(func)


def addsucess():
    config.status['success'] += 1


def addfailed():
    config.status['failed'] += 1


def addtotal():
    config.status['total'] += 1


def addupdate():
    config.status['updated'] += 1


def checkPath(path):
    return os.path.exists(path)


def initPath(path):
    if not checkPath(path):
        os.makedirs(path)


def timeSections(starttimes=None, endtimes=None, sectiondays=30, sectionshours=1, formats=None):
    if not starttimes:
        starttimes = moment.now().replace(minutes=0, seconds=0).add(days=-sectiondays)
    else:
        starttimes = moment.date(starttimes)
    if not endtimes:
        endtimes = moment.now().replace(minutes=0, seconds=0)
    else:
        endtimes = moment.date(endtimes)

    while starttimes < endtimes:
        nexttimes = copy.deepcopy(starttimes).add(hours=sectionshours)
        if formats:
            yield starttimes.format(formats), nexttimes.format(formats)
        else:
            yield starttimes, nexttimes
        starttimes = nexttimes


if __name__ == "__main__":
    print(list(timeSections(formats='YYYY-MM-DD hh:mm:ss')))
