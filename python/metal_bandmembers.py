import re
import requests
import bs4
import json
from bs4 import BeautifulSoup
from csv import DictReader
from fs.osfs import OSFS
from util import useragents

# //(([0-9]+)[^0-9]+([0-9]+))|
member_finder = re.compile(
    '(?:(?:current)|(?:former)|(?:official)|(?:other)|(?:classic_line-up)|(?:final)|(?:touring)|(?:session)).*',
    re.IGNORECASE)

member_finder2 = re.compile(
    '((current)|(former)|(members)|(musicians)|(Personnel)|(Line[-_]up)).*',
    re.IGNORECASE)

from_to_re = re.compile('(\D*(?P<from>[0-9]+)\D(?P<to>[0-9a-zA-Z]+))')

quick_pft = re.compile(
    '(?P<plays>[a-zA-Z]+\s[a-zA-Z]+)(\s[^0-9]*(?P<from>[0-9]{4})\s?(?:–|-)\s?(?:[a-zA-Z]+\s)?(?P<to>(?:present)|(?:['
    '0-9]{4}))[^0-9]*)?')
just_date = re.compile('[^0-9]*(?P<active>[0-9]+)[^0-9]*')
nuke_extra_played = re.compile('(?:[\s]+)|(?:and)')
no_ew = re.compile('\s+')
only_decimal = re.compile('[^0-9]+')

tr_name = re.compile('^(?:[^a-zA-Z]?[a-zA-Z]+[^a-zA-Z]?(?:[^a-zA-Z]*))+$')
tr_from_to = re.compile('(?:(?:(?:[^0-9]+)?[0-9]+(?:[^0-9]+)?)|(?:[0-9]+[^0-9]+[0-9]+(?:[^0-9]+)?)+)')
tr_plays = re.compile('(?:[a-z]+(?:\s[a-z]+[^a-z]+)?)+')
tr_bad_date = re.compile('[0-9][^0-9][0-9]\s[a-z]+\s(?P<active>[0-9]{4})', re.IGNORECASE)
tr_extract_from_to = re.compile('(?P<from>[0-9]{4})\s?(?:–|-)\s?(?:[a-zA-Z]+\s)?(?P<to>(?:present)|(?:[0-9]{4}))')

just_table_ft = re.compile(
    '[^0-9]*(?P<from>[0-9]{4})\s?(?:–|-)\s?(?:[a-zA-Z]+\s)?(?P<to>(?:present)|(?:[0-9]{4}))[^0-9]*', re.MULTILINE)
# just_table_whoplays = re.compile('(?P<who>[a-zA-Z]+(?:\s[a-zA-Z]+)?)\s?(?:–|-)\s?(?P<plays>.+)')
just_table_whoplays = re.compile('(?P<who>\s?[^a-zA-Z]?[a-zA-Z]+[^a-zA-Z]?)+\s?(?:–|-)\s?(?P<plays>.+)')

only_name = re.compile('(?:[a-z]\.?\s?[^a-z]?)+', re.IGNORECASE)
rest = re.compile('(([a-z][^a-z]+[a-z])|[a-z])+\s(.+)', re.IGNORECASE)
why = re.compile('–|-')
really = re.compile('([0-9]+(?:–|-|–)[0-9]+)|([0-9]+(?::–|-|–)[a-z]+)|([0-9]+)', re.IGNORECASE)

basic_npa = re.compile('(?P<name>.+)(?!\s(?:–|-|—|:)\s)[^a-zA-Z]+(?P<plays>[^(]+)\((?P<ft>.+)\)', re.IGNORECASE)
basic_npa2 = re.compile('(?P<name>.+)(?=(?:\s|\S)(?:–|-|—|:)\s|\S)[^a-zA-Z]+(?P<plays>[^(]+)\((?P<ft>.+)\)',
                        re.IGNORECASE)
basic_npa3 = re.compile(
    '(?P<name>[\wåäöÅÄÖ.\",\s]+)(?!(?:\s|\S)(–|-|—|:)(?:\s|\S))[^a-zA-Z]+(?P<plays>[^(]+)\((?P<ft>.+)\)')

basic_npak = re.compile('(?P<name>[åäöÅÄÖ\w()\".#\'/\s]+)\s(?:–|-|—|:)\s(?P<rest>.+)', re.IGNORECASE)

col_npa = re.compile('(?P<name>[a-zA-Z.]+\s(?:[a-zA-Z]+|[0-9]))+:\s(?P<plays>[a-zA-Z,\s]+)\((?P<ft>.+)\)')

basic_pa = re.compile('(?P<plays>[a-zA-Z,\s]+)\((?P<ft>.+)\)')
no_cite = re.compile('\[[0-9]+\]')
no_para = re.compile('[()\s]')

colon_begin = re.compile('^[\wåäöÅÄÖ.\"\-,\s()]+:.+')

something = re.compile(
    '(?P<name>[åäöÅÄÖ.a-zA-Z]+\s(?:[a-zA-Z]+|[0-9]))+\s(?:–|-|—|:)\s(?P<plays>[^0-9]+)\(?(?P<ft>.+)\)?')

really2 = re.compile('(?P<name>[åäöÅÄÖ\w()\".#\'/\s]+)\s(?:–|-|—|:)\s(?P<rest>.+)')

just_plays = re.compile('(?:\(.+\))|(?:\[.+\])')
just_ft = re.compile('((?P<from>[0-9]+)(?:–|-|—|:)(?P<to>[0-9a-z]+))|(?P<year>[0-9]+)')

acopper = re.compile('(?P<name>[^(]+)\((?P<plays>[^)]+)\)')

def write_page(band, pname, request):
    with open('band_pages/%s/%s.html' % (band, pname), 'w+') as page_out:
        page_out.write(request.text)


def dl_pages():
    base = 'band_pages'
    bandpages = OSFS(base)
    c = 0
    with requests.session() as session:
        with open('bandpages_original.csv', 'r') as bndin:
            for row in DictReader(bndin):
                band = row['band']
                wlink = row['wlink']
                malink = row['malink']
                if not bandpages.isdir(band):
                    bandpages.makedir(band)
                session.headers.update({'User-Agent': useragents[c]})
                request = session.get(wlink)
                write_page(band, 'wiki', request)
                if malink != 'none':
                    request = session.get(malink)
                    write_page(band, 'ma', request)
                c += 1
                if c == 3:
                    c = 0

    bandpages.close()


def extract_dl_bmember_pages():
    base = 'band_pages'
    bandpages = OSFS(base)
    c = 0
    with requests.session() as session:
        for page in bandpages.walkfiles():
            path = '%s/%s' % (base, page)
            band = page[page.find('/') + 1:page.rfind('/')]
            page_type = page[page.rfind('/') + 1:page.find('.')]
            if page_type == 'wiki':
                with open(path, 'r') as win:
                    wsoup = BeautifulSoup(win.read(), 'lxml')
                    band_mem_page = wsoup.find_all('a', href=True, title=re.compile('list\sof\s.+\sband\smembers',
                                                                                    re.IGNORECASE))
                    if len(band_mem_page) != 0:
                        session.headers.update({'User-Agent': useragents[c]})
                        request = session.get('https://en.wikipedia.org%s' % band_mem_page[0]['href'])
                        with open('bandmember_pages/%s.html' % band, 'w+') as page_out:
                            page_out.write(request.text)
                        c += 1
                        if c == 3:
                            c = 0


def wiki_dl(wsoup):
    for dl in wsoup.find_all('dl'):
        print(dl, dl.find_next_siblings('ul'))


def wiki_ids(wsoup):
    got = False
    members = {}
    cmembers = wsoup.find('span', id='Current_members')
    if cmembers is not None:
        got = True
        print(cmembers)
        child = cmembers.find_parent().find_next_sibling()
        print(child)
        # print('got current members')
    fmembers = wsoup.find('span', id='Former_members')
    if fmembers is not None:
        got = True
        print(fmembers)
        child = fmembers.find_parent().find_next_sibling()
        print(child)
        # print('got former members')
    lmembers = wsoup.find('span', id='Live_members')
    if lmembers is not None:
        got = True
        print(lmembers)
        child = lmembers.find_parent().find_next_sibling()
        print(child)
        # print('got live members')
    return got, members


def extract_wiki(page_path, band):
    with open(page_path, 'r') as win:
        wsoup = BeautifulSoup(win.read(), 'lxml')
        band_mem_page = wsoup.find_all('a', title=re.compile('list\sof\s[a-zA-Z_/\s]+\sband\smembers', re.IGNORECASE))
        if len(band_mem_page) != 0:
            print(band, band_mem_page)
            # # wiki_dl(wsoup)
            # got, members = wiki_ids(wsoup)
            # if got:
            #     print('we found memebers by id',band)
            #     print('----------------------------------------')


def next_sibling_filter(elem):
    return elem.name != 'div' and elem.name != 'h3'


def extract_table(table, bands, band):
    last_member = ''
    for tr in table.find_all('tr'):
        found_name = False
        found_from_to = False
        found_plays = False
        for td in tr.find_all('td'):
            list_holder = td.find('div', class_='hlist')
            if list_holder is not None:
                maybe_from_to = [li for li in list_holder.find_all('li', text=tr_from_to)]
                if len(maybe_from_to) > 0:
                    found_from_to = True
                    ayrs = []
                    for ft in maybe_from_to:
                        ftm = tr_extract_from_to.match(ft.text)
                        if ftm:
                            ayrs.append({'from': ftm.group('from'), 'to': ftm.group('to')})
                    bands[band][last_member]['active'] = ayrs
                maybe_plays = [li for li in list_holder.find_all('li', text=re.compile('[a-zA-Z]+'))]
                if len(maybe_plays) > 0:
                    found_plays = True
                    plays = []
                    for play in maybe_plays:
                        plays.append(play.text)
                    bands[band][last_member]['plays'] = plays
            else:
                if len(td.text) > 0:
                    if not found_name:
                        name = tr_name.match(td.text)
                        if name:
                            found_name = True
                            last_member = td.text
                            bands[band][last_member] = {}
                    if not found_from_to:
                        from_to = tr_from_to.match(td.text)
                        if from_to:
                            ayrs = []
                            if ',' in td.text:
                                active = no_ew.sub('', td.text)
                                yrs = active.split(',')
                                for y in yrs:
                                    ftm = from_to_re.match(y)
                                    if ftm:
                                        to = ftm.group('to')
                                        if 'present' not in to:
                                            to = only_decimal.sub('', to)
                                        ayrs.append({'from': ftm.group('from'), 'to': to})
                                    else:
                                        ayrs.append({'from': y, 'to': y})
                                bands[band][last_member]['active'] = ayrs
                            else:
                                active = td.text
                                m = tr_extract_from_to.match(active)
                                if m:
                                    bands[band][last_member]['active'] = [
                                        {'from': m.group('from'), 'to': m.group('to')}]
                                else:
                                    bad_date = tr_bad_date.match(active)
                                    if bad_date:
                                        bands[band][last_member]['active'] = [
                                            {'from': bad_date.group('active'),
                                             'to': bad_date.group('active')}]
                                    else:
                                        bands[band][last_member]['active'] = [{'from': active, 'to': active}]
                            found_from_to = True
                    if not found_plays:
                        plays = tr_plays.match(td.text)
                        if plays:
                            if ',' in td.text:
                                wass = td.text.split(',')
                                plays = []
                                for played in wass:
                                    played = nuke_extra_played.sub('', played)
                                    plays.append(played)
                                bands[band][last_member]['plays'] = plays
                            else:
                                bands[band][last_member]['plays'] = [td.text]
                            found_plays = True
                else:
                    continue


def extract_dl(dls, bands, band):
    last_member = ''
    for dl in dls:
        for c in dl.contents:
            if isinstance(c, bs4.element.Tag):
                if c.name == 'dt':
                    last_member = c.text
                    bands[band][last_member] = {}
                else:
                    if 'Active:' in c.text:
                        active = c.text[c.text.find(': ') + 2:]
                        # print(active)
                        if ',' in active:
                            yrs = active.split(',')
                            ayrs = []
                            for y in yrs:
                                ftm = from_to_re.match(y.strip(' '))
                                if ftm:
                                    ayrs.append({'from': ftm.group('from'),
                                                 'to': ftm.group('to')})
                                else:
                                    ayrs.append({'from': y,
                                                 'to': y})
                            bands[band][last_member]['active'] = ayrs
                        else:
                            ftm = from_to_re.match(active.rstrip())
                            if ftm:
                                gd = ftm.groupdict()
                                bands[band][last_member]['active'] = [{'from': gd['from'], 'to': gd['to']}]
                            else:
                                active = just_date.match(active).group('active')
                                bands[band][last_member]['active'] = [{'from': active,
                                                                       'to': active}]
                    elif 'Instruments:' in c.text:
                        was = c.text[c.text.find(':') + 2:]
                        if ',' in was:
                            wass = was.split(',')
                            plays = []
                            for played in wass:
                                plays.append(played.lstrip().rstrip())
                            bands[band][last_member]['plays'] = plays
                        else:
                            bands[band][last_member]['plays'] = [was]


def extract_caption_table(tables, bands, band):
    for tbl in tables:
        maybe_caption = tbl.find('caption')
        if maybe_caption:
            for tr in tbl.find_all('tr'):
                th = tr.find('th')
                maybe_ft = just_table_ft.match(th.text)
                if maybe_ft:
                    active = {
                        'from': maybe_ft.group('from'), 'to': maybe_ft.group('to')
                    }
                else:
                    ma = only_decimal.sub('', th.text)
                    active = {
                        'from': ma, 'to': ma
                    }
                for member in th.find_next().find_all('li'):
                    mmp = just_table_whoplays.match(member.text)
                    if mmp:
                        who = mmp.group('who').lstrip().rstrip()
                        if bands[band].get(who, None) is None:
                            bands[band][who] = {}
                        if bands[band][who].get('active', None) is None:
                            bands[band][who]['active'] = []
                        bands[band][who]['active'].append(active)
                        if bands[band][who].get('plays', None) is None:
                            bands[band][who]['plays'] = []
                        bands[band][who]['plays'].append(mmp.group('plays'))


def gen_lis(mdts):
    for dt in mdts:
        parent = dt.find_parent()
        for li in parent.find_next('ul').find_all('li'):
            yield li


def build_ft(fts, bands, band, member):
    active = []
    if ',' in fts:
        for ft in fts.split(','):
            mft = from_to_re.match(ft)
            if mft:
                active.append({'from': mft.group('from'), 'to': mft.group('to')})
            else:
                active.append({'from': ft, 'to': ft})
    else:
        mft = from_to_re.match(fts)
        if mft:
            active.append({'from': mft.group('from'), 'to': mft.group('to')})
        else:
            active.append({'from': fts, 'to': fts})
    bands[band][member]['active'] = active


def build_plays(plays, bands, band, member):
    pls = set()
    if ',' in plays:
        for instrument in plays.split(','):
            pls.add(instrument)
    else:
        pls.add(plays)
    bands[band][member]['plays'] = list(pls)


def extract_colon(text, bands, band):
    [name, rest] = text.split(':')
    bands[band][name] = {}
    mpa = basic_pa.match(rest)
    if mpa:
        plays = mpa.group('plays').lstrip().rstrip()
        build_plays(plays, bands, band, name)
        build_ft(no_para.sub('', mpa.group('ft')), bands, band, name)
    else:
        print(text)
        raise Exception(': failed')


def do_npft(match, bands, band):
    name = match.group('name')
    bands[band][name] = {}
    plays = match.group('plays')
    from_to = match.group('ft')
    build_plays(plays, bands, band, name)
    build_ft(from_to, bands, band, name)


def find_members_dt(wsoup, bands, band):
    mdts = wsoup.find_all('dt', text=member_finder2)  # type: list(bs4.element.Tag)
    if len(mdts) > 0:
        for li in gen_lis(mdts):
            if colon_begin.match(li.text):
                extract_colon(li.text, bands, band)
            else:
                what = something.match(li.text)
                if what:
                    do_npft(what, bands, band)
                else:
                    mbnpa = basic_npa.match(li.text)
                    if mbnpa:
                        do_npft(mbnpa, bands, band)



def ensure_member_dict(bands, band, name):
    if bands[band].get(name, None) is None:
        bands[band][name] = {}
    if bands[band][name].get('active', None) is None:
        bands[band][name]['active'] = []
    if bands[band][name].get('plays', None) is None:
        bands[band][name]['plays'] = []


def find_members_span(wsoup, bands, band):
    members = wsoup.find_all('span', id=member_finder2)  # type: list(bs4.element.Tag)
    if len(members) > 0:
        for member in members:
            parent = member.find_parent()
            for li in parent.find_next('ul'):
                if isinstance(li, bs4.element.NavigableString):
                    continue
                text = li.text
                nothings = really2.match(text)
                if nothings:
                    name = nothings.group('name')
                    rest = nothings.group('rest')
                    no_ft = just_plays.sub('', rest)
                    from_tos = list(just_ft.finditer(rest))
                    ensure_member_dict(bands, band, name)
                    if len(from_tos) > 0:
                        yrs = []
                        for ft in from_tos:
                            mdict = ft.groupdict()
                            singley = mdict.get('year', None)
                            if not singley:
                                yrs.append({'from': mdict.get('from'), 'to': mdict.get('to')})
                            else:
                                yrs.append({'from': singley, 'to': singley})
                        bands[band][name]['active'] = yrs
                    build_plays(no_ft, bands, band, name)
                else:
                    it = re.match('(?P<name>[åäöÅÄÖa-zA-Z\s]+)\s(?:–|-|—|−)\s(?P<plays>[^(]+)\((?P<ft>.+)\)', text)
                    if it is not None:
                        name = it.group('name')
                        plays = it.group('plays')
                        ft = it.group('ft')
                        ensure_member_dict(bands, band, name)
                        build_plays(plays, bands, band, name)
                        build_ft(ft, bands, band, name)


def populate_skip(skip, skip2=False):
    with open('skip.txt', 'r') as rin:
        for b in rin:
            skip.add(b.rstrip())
    if skip2:
        with open('skip2.txt', 'r') as rin:
            for b in rin:
                skip.add(b.rstrip())


def alice_cooper(wsoup,bands,band):
    print('alice coop')
    for td in wsoup.find_all('td'):
        ft = td.find('span',class_='mw-headline')
        if ft is not None:
            for li in td.find_next('ul').find_all('li'):
                pft = acopper.match(li.text)
                name = pft.group('name').lstrip().rstrip()
                plays = pft.group('plays').lstrip().rstrip()
                ensure_member_dict(bands, band, name)
                if '–' in ft.text:
                    [f,t] = ft.text.split('–')
                    bands[band][name]['active'].append({'from':f,'to':t})
                else:
                    [f, t] = ft.text.split(' ')
                    bands[band][name]['active'].append({'from': t, 'to': t})
                if ',' in plays:
                    for p in plays.split(','):
                        bands[band][name]['plays'].append(p)
                else:
                    bands[band][name]['plays'].append(plays)


def extract_members_bmemberpages():
    base = 'bandmember_pages'
    bandpages = OSFS(base)
    bandl = []
    bands = {}
    for page in bandpages.walkfiles():
        path = '%s/%s' % (base, page)
        band = page[page.find('/') + 1:page.rfind('.')]
        bandl.append(band)
        # if band != 'AC_DC':
        #     continue
        with open(path, 'r') as win:
            wsoup = BeautifulSoup(win.read(), 'lxml')
            allm = wsoup.find_all('span', id=member_finder)
            bands[band] = {}
            if len(allm) == 0:
                tables = wsoup.find_all('table')
                extract_caption_table(tables, bands, band)
            else:
                for span in allm:
                    # print(span)
                    parent = span.find_parent()  # type: bs4.element.Tag
                    # print(type(parent))
                    sibling = parent.find_next_sibling(next_sibling_filter)  # type: bs4.element.Tag
                    # print('next sibling is a ', sibling.name)
                    if sibling.name == 'table':
                        extract_table(sibling, bands, band)
                    elif sibling.name == 'dl':
                        siblings = [dl for dl in parent.find_next_siblings('dl')]  # type: list(bs4.element.Tag)
                        extract_dl(siblings, bands, band)
                    else:
                        if band == 'Twisted_Sister' or band == 'Opeth':
                            for ul in [ul for ul in parent.find_next_siblings('ul')]:
                                for li in ul.find_all('li'):
                                    dash = li.text.find('-')
                                    name = li.text[:dash]
                                    if dash == -1:
                                        dash = li.text.find('-')
                                        name = li.text[:dash]
                                    if dash == -1:
                                        dash = li.text.find('–')
                                        name = li.text[:dash]
                                    if bands[band].get(name, None) is None:
                                        bands[band][name] = {}
                                    if bands[band][name].get('active', None) is None:
                                        bands[band][name]['active'] = []
                                    if bands[band][name].get('plays', None) is None:
                                        bands[band][name]['plays'] = []
                                    plays_in = li.text[dash + 2:]
                                    plays = plays_in[:plays_in.find('(')]
                                    ain = plays_in[plays_in.find('(') + 1:plays_in.rfind(')')]
                                    for found in really.finditer(ain):
                                        it = found.group(0)
                                        ft = from_to_re.match(it)
                                        if ft:
                                            bands[band][name]['active'].append({
                                                'from': ft.group('from'), 'to': ft.group('to')
                                            })
                                        else:
                                            bands[band][name]['active'].append({
                                                'from': it, 'to': it
                                            })
                                    if ',' in plays:
                                        for play in plays.split(','):
                                            bands[band][name]['plays'].append(play)
                                    else:
                                        bands[band][name]['plays'].append(plays.rstrip())
            if bands[band] == {}:
                tables = wsoup.find_all('table')
                extract_caption_table(tables, bands, band)

    for k, v in bands.items():
        if v == {}:
            print(k)
    print(len(list(bands.keys())))
    # with open('skip.txt', 'w+') as out:
    #     for b in bandl:
    #         out.write('%s\n' % b)
    #
    # with open('band_timeline_b.json', 'w+') as out:
    #     nbands = {}
    #     for band, bdict in bands.items():
    #         nbands[band] = []
    #         print(band)
    #         for member, infor in bdict.items():
    #             print(infor)
    #             nbands[band].append(
    #                 {'member': member, 'plays': infor.get('plays', []), 'active': infor.get('active', [])})
    #     json.dump(nbands, out, indent=2)

def rest_wiki():
    skip = set()
    populate_skip(skip, skip2=False)
    base = 'band_pages'
    bandpages = OSFS(base)
    bands = {}
    no_do = {  'Sunn_O)))','Alice_Cooper',
             'Hellbastard'}
    for page in bandpages.walkfiles():
        path = '%s/%s' % (base, page)
        band = page[page.find('/') + 1:page.rfind('/')]
        page_type = page[page.rfind('/') + 1:page.find('.')]
        if page_type == 'wiki' and band not in skip:
            bands[band] = {}
            with open(path, 'r') as win:
                wsoup = BeautifulSoup(win.read(), 'lxml')
                if band in no_do:
                    if band == 'Alice_Cooper':
                        alice_cooper(wsoup, bands, band)
                else:
                    find_members_dt(wsoup, bands, band)
                    find_members_span(wsoup, bands, band)

    # for k,v in bands.items():
    #     if v == {}:
    #         print(k)
    # print(len(list(bands.keys())))
    with open('band_timeline_a2.json', 'w+') as out:
        nbands = {}
        for band, bdict in bands.items():
            nbands[band] = []
            print(band)
            for member, infor in bdict.items():
                print(infor)
                nbands[band].append(
                    {'member': member, 'plays': infor.get('plays', []), 'active': infor.get('active', [])})
        json.dump(nbands, out, indent=2)


def combine():
    with open('band_timeline_a2.json', 'r') as bdin:
        b1 = json.load(bdin)
    with open('band_timeline_b.json', 'r') as bdin:
        b2 =  json.load(bdin)

    for k,v in b2.items():
        if b1.get(k, None) is not None:
            print('badddd',k)
        b1[k] = v

    print(len(b1.keys()))
    with open('band_timeline.json', 'w+') as bdin:
        json.dump(b1, bdin, indent=2)


if __name__ == '__main__':
    combine()
    # extract_members_bmemberpages()
    # rest_wiki()
