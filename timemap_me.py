import re
import arrow

memento_re = re.compile('<([^>]+)>;\srel="([a-z]+\s)?memento";\sdatetime="([^"]+)",')
original_re = re.compile('<([^>]+)>;\srel="original",')
self_re = re.compile('<([^>]+)>;\srel="self"; type="([^"]+)";\sfrom="([^"]+)";\suntil="([^"]+)",')
timegate_re = re.compile('<([^>]+)>;\srel="timegate",')


class Timemap(object):
    def __init__(self, tmlines):
        self.original = None
        self.timegate = None
        self.timemap = None
        self.first_memento = None
        self.last_memento = None
        self.mementos = []
        self.found_self = False
        self.found_timegate = False
        self.found_original = False
        self.build(tmlines)

    def build(self, tmlines):
        for line in tmlines:
            line = line.rstrip()

            if not self.found_original:
                maybe_original = original_re.match(line)
                if maybe_original is not None:
                    groups = maybe_original.groups()
                    self.found_original = True
                    self.original = groups[0]

            if not self.found_self:
                maybe_self = self_re.match(line)
                if maybe_self is not None:
                    groups = maybe_self.groups()
                    self.first_memento = groups[2]
                    self.last_memento = groups[3]
                    self.timemap = groups[0]
                    self.found_self = True

            if not self.found_timegate:
                maybe_timegate = timegate_re.match(line)
                if maybe_timegate is not None:
                    groups = maybe_timegate.groups()
                    self.timegate = groups[0]
                    self.found_timegate = True

            maybe_memento = memento_re.match(line)
            if maybe_memento is not None:
                groups = maybe_memento.groups()
                # 2016 07 25 06 37 43
                print()
                self.mementos.append({
                    "uri": groups[0],
                    "datetime": re.findall('([0-9]{14})',groups[0])[0]
                })

    def to_json(self):
        jdict = {'original': self.original, 'self': self.timemap, 'timegate': self.timegate,
                 'first': self.first_memento, 'last': self.last_memento, 'mementos': self.mementos}
        return jdict

    def __str__(self):
        return 'timemap=%s timegate=%s original=%s first_memento=%s last_memento=%s num_mementos=%d' % (
            self.timemap, self.timegate, self.original, self.first_memento, self.last_memento, len(self.mementos))

    def __repr__(self):
        return self.__str__()
