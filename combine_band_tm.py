import json
import arrow
from dateutil.tz import tz
import re
from fs.osfs import OSFS

date4 = re.compile('(?:[0-9]{4})|(?:present)')
still_month = re.compile('[a-zA-Z]+ (?P<from>[0-9]+) – [a-zA-Z]+ (?P<to>[0-9]+)')


def do_combine():
    with open('band_timeline.json', 'r') as bndin:
        bands = json.load(bndin)
        print(bands)

    mtml = OSFS('timemaps/json')
    for metal_tml in mtml.walkfiles():
        p1 = metal_tml.find('/')
        p2 = metal_tml.find('.')
        b = metal_tml[p1 + 1:p2]
        with open('timemaps/json%s' % metal_tml, 'r') as bndin:
            band_tm = json.load(bndin)
            with open('band_to_tm/%s.json' % b, 'w+') as btm:
                json.dump({"info": bands[b], "tm": band_tm}, btm, indent=2)
            print(band_tm)
    mtml.close()


def extract_binfo_date(active):
    if active['to'] == 'present':
        to = arrow.utcnow()
    else:
        to = arrow.get('%s%s' % (active['to'], '1231'))
    if active['from'] == 'present':
        f = arrow.utcnow()
    else:
        f = arrow.get('%s%s' % (active['from'], '0101'), 'YYYYMMDD')
    return f, to


def sanitiz():
    base = 'band_to_tm'
    metal_btm = OSFS(base)
    for metal in metal_btm.walkfiles():
        p1 = metal.find('/')
        p2 = metal.find('.')
        b = metal[p1 + 1:p2]
        print(b)
        with open('%s%s' % ('band_to_tm', metal), 'r') as min:
            metal = json.load(min)
            info = metal['info']
            mem_point = []
            for i in info:
                for f,t in map(extract_binfo_date,i['active']):
                    mem_point.append({
                        "f": f.format(),
                        "t": t.format(),
                        "plays": i['plays'],
                        "member": i['member']
                    })
            mtm = metal['tm']
            metal_plot = {
                "member_points": mem_point,
                "mementos": mtm['mementos'],
                "first": mtm['first'],
                "last": mtm['last'],
                "timemap": mtm['self'],
                "timegate": mtm['timegate'],
                "original": mtm['original'],
            }
            with open('plot/%s.json' % b, 'w') as mout:
                json.dump(metal_plot,mout,indent=2)
            print('----------------------------------------')
    metal_btm.close()


if __name__ == '__main__':
    # do_combine()
    sanitiz()
    # with open('/home/john/PycharmProjects/ia-bday/band_to_tm/Anata.json', 'r') as min:
    #     metal = json.load(min)
    #     mementos = metal['tm']['mementos']
    #     info = metal['info']
    #     n_mementos = [] # type: list(dict[str,arrow.Arrow])
    #     for m in mementos:
    #         n_mementos.append({
    #             "uri": m['uri'],
    #             'datetime': arrow.get(m['datetime'], 'YYYYMMDDHHmmss')
    #         })
    #     not_in_range = []
    #     for i in info:
    #         for active in i['active']:
    #             f,to = extract_binfo_date(active)
    #             for nm in n_mementos:
    #                 dt = nm['datetime']
    #                 if f <= dt <= to:
    #                     print(dt,'in range',f,to)
    #                 else:
    #                     not_in_range.append(dt)
    #                     print(dt,'is not in range of band')
