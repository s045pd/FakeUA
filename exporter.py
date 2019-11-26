import json

import pandas

from common import checkPath
from log import success
from common import checkTimes


def CreateXLSX(datas, columns, filename='res.xlsx'):
    with checkTimes():
        xlsx = pandas.DataFrame(datas)
        xlsx.rename(columns=columns, inplace=True)
        writer = pandas.ExcelWriter(
            filename, options={'strings_to_urls': False})
        xlsx.to_excel(writer, "data")
        writer.save()
        success('Created {filename}')


def CreateJson(datas, filename='res.json'):
    with checkTimes():
        with open(filename, 'w') as f:
            f.write(json.dumps(datas, ensure_ascii=False, indent=4))
            success(f'Saved {filename}')
