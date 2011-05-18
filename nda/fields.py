# -*- coding: utf-8 -*-

from random import randint, randrange, choice, random
from StringIO import StringIO
from datetime import datetime, date, time
from hashlib import md5

class NdaField(object):
    DOMAINS = ['example.com', 'test.ok', 'some.org',
               'ololo.net', 'somebody.neme', 'whatabout.me',
               'yandex.ru', 'localhost', 'pisem.net']

    def __init__(self, source_file=None):
        if source_file:
            with open(source_file) as f:
                self.source = StringIO(f.read())

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
    def __init__(self, source_file='ndator/texts/lorem.txt',
                 min_length=None, max_length=None):
        super(CharNda, self).__init__(source_file)
        self.min = min_length
        self.max = max_length

    def obfuscate(self, value):
        text = self.source.read()
        if self.min and self.max:
            res = text[:randint(self.min, self.max)]
        elif self.max:
            res = text[:randint(self.max / 2 + 1, self.max)]
        elif self.min:
            res = text[:randint(self.min, len(text))]
        else:
            res = text[:randint(0, len(text))]

        return res


class FirstNameNda(NdaField):
    def __init__(self, source_file='ndator/texts/names.txt', sep=' '):
        super(FirstNameNda, self).__init__(source_file)
        self.sep = sep
        # part: 0 - firstname, 1 - lastname, 2 - middlename
        self.part = 0

    def obfuscate(self, value):
        """ source file shuld be in
        <firstname><separator><lastname><separator>[middlename]
        """
        text_lines = self.source.read().splitlines()

        return text_lines[
            randint(0, len(text_lines)-1)].split(self.sep)[self.part].strip()


class LastNameNda(FirstNameNda):
    def __init__(self, source_file='ndator/texts/names.txt', sep=' '):
        super(LastNameNda, self).__init__(source_file, sep)
        # part: 0 - firstname, 1 - lastname, 2 - middlename
        self.part = 1


class MiddleNameNda(FirstNameNda):
    def __init__(self, source_file='ndator/texts/names.txt', sep=' '):
        super(MiddleNameNda, self).__init__(source_file, sep)
        # part: 0 - firstname, 1 - lastname, 2 - middlename
        self.part = 2


class LoginNda(FirstNameNda):
    def __init__(self, source_file='ndator/texts/login.txt', sep=' '):
        super(LoginNda, self).__init__(source_file, sep)

    def obfuscate(self, value):
        text_lines = self.source.read().splitlines()
        return text_lines[randint(0, len(text_lines)-1)].strip()


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
        first = super(LoginNda, self).obfuscate(value.split('@')[0])
        return first + u'@' + last


class IPAdressNda(NdaField):
    def obfuscate(self, value):
        return u'.'.join([unicode(randint(1, 255)) for i in range(4)])


class NullBooleanNda(NdaField):
    def obfuscate(self, value):
        return choice([True, False, None])


class URLNda(NdaField):
    def obfuscate(self, value):
        h = md5(str(datetime.now()) + value).hexdigest()[:16]
        return u'http://%s/%s' %(choice(self.DOMAINS), h)


class HashNda(NdaField):
    def obfuscate(self, value):
        return md5(str(value)).hexdigest()
