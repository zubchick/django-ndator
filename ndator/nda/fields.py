# -*- coding: utf-8 -*-

from __future__ import with_statement
import os
from random import randint, randrange, choice, random
from datetime import datetime, date, time

from hashlib import md5


BASE_PATH = os.path.split(os.path.abspath(__file__))[0]
BASE_PATH = os.path.join(BASE_PATH, '../')


class NdaField(object):
    DOMAINS = ['example.com', 'test.ok', 'ololo.gg', 'somebody.name', 'localhost.by']

    def __init__(self, source_file=None):
        if source_file:
            with open(source_file) as f:
                self.source = f.read().splitlines()

    def obfuscate(self, value):
        return value


class IntegerNda(NdaField):
    def __init__(self, min_value=None, max_value=None):
        self.min = min_value
        self.max = max_value

    def obfuscate(self, value):
        if not (self.min and self.max):
            len_ = len(str(value)) - 1
            res = (randint(10 ** len_, 10 ** (len_ + 1) - 1) *
                   (choice([-1, 1]) if value < 0 else 1))
        else:
            res = randint(self.min, self.max)

        return res


class FloatFieldNda(IntegerNda):
    def __init__(self, min_value=None, max_value=None):
        self.min = int(min_value)
        self.max = int(max_value) - 1

    def obfuscate(self, value):
        intg = super(FloatFieldNda, self).obfuscate(value)
        return intg + random()


class BooleanNda(NdaField):
    def obfuscate(self, value):
        return bool(randint(0, 1))


class CharNda(NdaField):
    def __init__(self, source_file=BASE_PATH+'texts/lorem.txt',
                 min_length=None, max_length=None, words=None):
        super(CharNda, self).__init__(source_file)
        self.min = min_length
        self.max = max_length
        self.words = words

    def obfuscate(self, value):
        text = '\n'.join(self.source)

        if self.words:
            res = []
            text = text.split()
            for _ in xrange(self.words):
                res.append(text[randint(0, len(text) - 1)])
            return ' '.join(res)

        if self.min and self.max:
            res = text[:randint(self.min, self.max)]
        elif self.max:
            res = text[:randint(1, self.max / 2)]
        elif self.min:
            res = text[:randint(self.min, len(text))]
        else:
            self.words = 2
            res = CharNda.obfuscate(self, value)
        return res


class SlugNda(CharNda):
    def obfuscate(self, value):
        self.max = self.max or 50
        self.words = self.words or 2
        text = '\n'.join(self.source).split()
        sep = choice(['', '-', '_'])
        res = []
        for _ in xrange(self.words):
            res.append(text[randint(0, len(text) - 1)])
        return sep.join(res)[:self.max]


class FirstNameNda(NdaField):
    def __init__(self, source_file=BASE_PATH+'texts/names.txt', sep=' '):
        super(FirstNameNda, self).__init__(source_file)
        self.sep = sep
        # part: 0 - firstname, 1 - lastname, 2 - middlename
        self.part = 0

    def obfuscate(self, value):
        """ source file shuld be in
        <firstname><separator><lastname><separator>[middlename]
        """
        text_lines = self.source
        return text_lines[
            randint(0, len(text_lines)-1)].split(self.sep)[self.part].strip()


class LastNameNda(FirstNameNda):
    def __init__(self, source_file=BASE_PATH+'texts/names.txt', sep=' '):
        super(LastNameNda, self).__init__(source_file, sep)
        # part: 0 - firstname, 1 - lastname, 2 - middlename
        self.part = 1


class MiddleNameNda(FirstNameNda):
    def __init__(self, source_file=BASE_PATH+'texts/names.txt', sep=' '):
        super(MiddleNameNda, self).__init__(source_file, sep)
        # part: 0 - firstname, 1 - lastname, 2 - middlename
        self.part = 2


class LoginNda(FirstNameNda):
    def __init__(self, source_file=BASE_PATH+'texts/login.txt',
                 unique=False, how_many=10000):
        super(LoginNda, self).__init__(source_file)
        self.unique = unique
        self.how_many = how_many

    def obfuscate(self, value):
        text_lines = self.source
        if self.unique:
            postf = str(int(md5(str(value)).hexdigest(), 16) % self.how_many)
        else:
            postf = ''
        return text_lines[randint(0, len(text_lines)-1)].strip() + postf


class DateNda(NdaField):
    def obfuscate(self, value):
        start_date = date.today().replace(year=1901).toordinal()
        end_date = date.today().toordinal()
        return date.fromordinal(randint(start_date, end_date))


class DateTimeNda(DateNda):
    def obfuscate(self, value):
        rnd = super(DateTimeNda, self).obfuscate(value)
        return datetime(year=rnd.year, month=rnd.month, day=rnd.day,
                        hour=randrange(12), minute=randrange(60),
                        second=randrange(60))


class TimeNda(NdaField):
    def obfuscate(self, value):
        return time(hour=randrange(12), minute=randrange(60),
                    second=randrange(60))


class EmailNda(LoginNda):
    def obfuscate(self, value):
        last = choice(self.DOMAINS)
        first = super(LoginNda, self).obfuscate(value)
        return first + u'@' + last


class IPAdressNda(NdaField):
    def obfuscate(self, value):
        return u'.'.join([unicode(randint(1, 255)) for i in range(4)])


class NullBooleanNda(NdaField):
    def obfuscate(self, value):
        return choice([True, False, None])


class URLNda(NdaField):
    def obfuscate(self, value):
        value = value or ''
        h = md5(str(datetime.now()) + value).hexdigest()[:16]
        return u'http://%s/%s' %(choice(self.DOMAINS), h)


class HashNda(NdaField):
    def obfuscate(self, value):
        return md5(str(value)).hexdigest()
