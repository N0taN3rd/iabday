import requests
from csv import DictReader
from fs.osfs import OSFS
import json
from timemap_me import Timemap
from util import useragents, tm_link


def save_tm(band, request):
    with open('timemaps/link/%s.tm' % band, 'w+') as metalTm:
        metalTm.write(request.text)


def get_metal_timemaps():
    c = 0
    with requests.session() as session:
        with open('bands.csv', 'r') as metalIn:
            for metal in DictReader(metalIn):
                session.headers.update({'User-Agent': useragents[c]})
                request = session.get(tm_link % metal['site'])
                save_tm(metal['band'], request)
                c += 1
                if c == 3:
                    c = 0
                print(metal['band'])


if __name__ == '__main__':
    c = 0
    bands = {}
    with open('bands.csv', 'r') as metalIn:
        for metal in DictReader(metalIn):
            bands[metal['band']] = {'site': metal['site']}
    mtml = OSFS('timemaps/link/')
    for metal_tml in mtml.walkfiles():
        p1 = metal_tml.find('/')
        p2 = metal_tml.find('.')
        b = metal_tml[p1 + 1:p2]
        with open('timemaps/link%s' % metal_tml, 'r') as mtmlin:
            metal_tm = Timemap(mtmlin.readlines())
            print(metal_tm)
            bands[b] = metal_tm
            print('----------------------------------------')
    mtml.close()
    for band, tm in bands.items():
        print(band,tm)
        with open('timemaps/json/%s.json'%band,'w+') as btm:
            json.dump(tm, btm, default=lambda x: x.to_json(), indent=2)
    # with open('band_to_tm.json','w+') as btm:
    #     json.dump(bands,btm,default=lambda x:x.to_json(),indent=2)

