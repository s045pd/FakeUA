from urllib.parse import urljoin, urlparse

import moment
import numpy
from pyquery import PyQuery as jq

from common import addtotal, addupdate
from log import success, info


def ParserSelect(text, url, types, city):
    jqdata = jq(text)
    payload = {}

    try:

        if types == 'xxx':
            for item in jqdata('.xxx').items():

                hid = item.text()
                payload[hid] = {
                    "hid": hid,
                }
                addtotal()
                success(f"{hid}")

        elif types == 'xxx_details':
            payload = {

            }
            addupdate()

    except Exception as e:
        raise

    return payload
