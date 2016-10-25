import re
import dateutil.parser

tokenizer = re.compile('(<[^>]+>|[a-zA-Z]+="[^"]*"|[;,])\\s*')


class TimeMap:
    def __init__(self, tm_lines):
        self.original = None
        self.timebundle = None
        self.timegate = None
        self.timemap = None
        self.first_memento = None
        self.last_memento = None
        self.mementos = {}
        self.__tokens = TimeMapTokenizer(tm_lines)
        link = self.get_next_link()
        while link is not None:
            print(link)
            if link[0] == 'memento':
                self.mementos[link[1]] = link[2]
            elif link[0] == 'original':
                self.original = link[2] if link is not None else None
            elif link[0] == 'timebundle':
                self.timebundle = link[2] if link is not None else None
            elif link[0] == 'timegate':
                self.timegate = link[2] if link is not None else None
            elif link[0] == 'timemap':
                self.timemap = link[2] if link is not None else None
            elif link[0] == 'first memento':
                self.mementos[link[1]] = link[2]
                self.first_memento = link[1] if link is not None else None
            elif link[0] == 'last memento':
                self.mementos[link[1]] = link[2]
                self.last_memento = link[1] if link is not None else None
            link = self.get_next_link()

    def get_next_link(self):
        uri = None
        datetime = None
        rel = None
        resource_type = None
        for token in self.__tokens:
            if token[0] == '<':
                uri = token[1:-1]
            elif token[:9] == 'datetime=':
                datetime = token[10:-1]
            elif token[:4] == 'rel=':
                rel = token[5:-1]
            elif token[:5] == 'type=':
                resource_type = token[6:-1]
            elif token == ';':
                None
            elif token == ',':
                return (rel, dateutil.parser.parse(datetime)
                if datetime is not None else None,
                        uri, resource_type)

        if uri is None:
            return None
        else:
            return (rel, dateutil.parser.parse(datetime)
            if datetime is not None else None,
                    uri, resource_type)

    def __getitem__(self, key):
        return self.mementos[key]

    def __str__(self):
        return 'original=%s timegate=%s '


class TimeMapTokenizer:
    def __init__(self, tm_lines):
        self._tokens = []
        self.lines = tm_lines
        self.size = len(self.lines)
        self.cur = 0

    def __next__(self):
        if len(self._tokens) == 0:
            if self.cur == self.size:
                raise StopIteration
            line = self.lines[self.cur]
            self.cur += 1
            if self.cur == self.size:
                raise StopIteration
            self._tokens = tokenizer.findall(line)
        return self._tokens.pop(0)

    def __iter__(self):
        return self