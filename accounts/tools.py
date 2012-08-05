import uuid

def format_minutes_to_hhmm(minutes):
    """
    Formats minutes passed in a day ('dygn') into HH:MM format
    where H is hour and M is minute.
    """
    output_str = ""
    if minutes >= 0:

        hours = minutes / 60
        minutes_remaining = minutes - (hours * 60)

        output_str = str(hours).zfill(2) + ":" + str(minutes_remaining).zfill(2)

    return output_str


def format_minutes_to_pretty_format(minutes):

    """
    Formats minutes into a pretty format:
    Ex:
        1 timme 15 minuter.
        10 timmar 45 minuter.
    """

    output_str = ""
    if minutes >= 0:
        hours = minutes / 60
        minutes_remaining = minutes - (hours * 60)

        if hours >= 1:
            output_str += str(hours) + " "
            if hours == 1:
                output_str += "timme"
            else:
                output_str += "timmar"
            output_str += " "

        if minutes_remaining >= 1:
            output_str += str(minutes_remaining) + " "
            if minutes_remaining == 1:
                output_str += "min"
            else:
                output_str += "min"

    return output_str.strip()


def list_with_time_interval(start=0, stop=60* 24, interval=30,
                            format_function=format_minutes_to_hhmm):
    """
    Generate a list of tuples with minutes occuring between start and
    stop with correct interval and a string generated from
    format_function.
    """
    # basic error checks
    if interval <= 0 or start > stop:
        return []

    times = []
    minutes = start
    while minutes <= stop:

        output = format_function(minutes)
        times.append((minutes, output))

        minutes += interval
    return times

def get_unique_filename(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2iT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2iG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.1fMB' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.iKB' % kilobytes
    else:
        size = '%.iB' % bytes
    return size

"""
Generate short URL
A bit-shuffling approach is used to avoid generating consecutive, predictable URLs.
However, the algorithm is deterministic and will guarantee that no collisions
will occur.

http://code.activestate.com/recipes/576918-python-short-url-generator/
"""

DEFAULT_ALPHABET = 'ABCDEFGHIJKLMNOPQRXTZ123456789'
DEFAULT_BLOCK_SIZE = 35
MIN_LENGTH = 8

class UrlEncoder(object):
    def __init__(self, alphabet=DEFAULT_ALPHABET, block_size=DEFAULT_BLOCK_SIZE):
        self.alphabet = alphabet
        self.block_size = block_size
        self.mask = (1 << block_size) - 1
        self.mapping = range(block_size)
        self.mapping.reverse()
    def encode_url(self, n, min_length=MIN_LENGTH):
        return self.enbase(self.encode(n), min_length)
    def decode_url(self, n):
        return self.decode(self.debase(n))
    def encode(self, n):
        return (n & ~self.mask) | self._encode(n & self.mask)
    def _encode(self, n):
        result = 0
        for i, b in enumerate(self.mapping):
            if n & (1 << i):
                result |= (1 << b)
        return result
    def decode(self, n):
        return (n & ~self.mask) | self._decode(n & self.mask)
    def _decode(self, n):
        result = 0
        for i, b in enumerate(self.mapping):
            if n & (1 << b):
                result |= (1 << i)
        return result
    def enbase(self, x, min_length=MIN_LENGTH):
        result = self._enbase(x)
        padding = self.alphabet[0] * (min_length - len(result))
        return '%s%s' % (padding, result)
    def _enbase(self, x):
        n = len(self.alphabet)
        if x < n:
            return self.alphabet[x]
        return self._enbase(x / n) + self.alphabet[x % n]
    def debase(self, x):
        n = len(self.alphabet)
        result = 0
        for i, c in enumerate(reversed(x)):
            result += self.alphabet.index(c) * (n ** i)
        return result

def encode_url(n, min_length=MIN_LENGTH):
    return UrlEncoder().encode_url(n, min_length)
