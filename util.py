# Utilities for cryptopals.

from collections import namedtuple


def groups(seq, length):
    '''
    Yield groups of specified length from a sequence. The final yield will provide whatever data is left in the
    sequence, without padding.Useful in a for statement:
        for pair in groups('abcdefg', 2):
            do_the_thing(pair)
    :param seq: A slicable object like string or list.
    :param length: The length of each group (ie. 2 for pairs)
    :return:
    '''
    for i in range(0, len(seq), length):
        # print(i)
        yield seq[i:i + length]


def hexbytes_to_bytestr(bytes_data):
    l = list(map(lambda x: chr(int(x, 16)).encode(), groups(bytes_data, 2)))
    s = b''.join(l)
    return s


def test_groups():
    data = 'abcde'
    for pair in groups(data, 2):
        print(pair)

    pair_list = [pairs for pairs in groups(data, 2)]
    assert pair_list == ['ab', 'cd', 'e']


def plaintext_score(bytestr):
    '''
    Quick and dirty scoring method that uses the most common english letters.
    :param bytestr: Bytes to check
    :return: Int score.
    '''

    # print(bytestr)
    # print('len', len(bytestr))

    score = 0

    # weights
    COMMON_WEIGHT = 3
    PUNCTUATION_WEIGHT = 1
    ISPRINTABLE_WEIGHT = 10
    UNICODEDECODEERROR_WEIGHT = -15

    for byte in bytestr:
        if bytes([byte]).upper() in b'ETAOIN SHRDLU':
            score += COMMON_WEIGHT

        if bytes([byte]).upper() in b',.?;:\'"/:!':
            score += PUNCTUATION_WEIGHT
    try:
        if bytestr.decode().isprintable():
            score += ISPRINTABLE_WEIGHT
    except UnicodeDecodeError:
        score -= UNICODEDECODEERROR_WEIGHT

    # print('score', score)
    return score


class ScoredPlaintext(namedtuple('ScoredPlaintext', 'bytestr')):
    def __new__(cls, bytestr):
        self = super(ScoredPlaintext, cls).__new__(cls, bytestr)
        self._score = plaintext_score(bytestr)
        return self

    @property
    def score(self):
        return self._score

    def __str__(self):
        return "ScoredPlaintext: " + str(self.bytestr) + "\tScore: " + str(self.score)


def test_ScoredPlaintext():
    sp = ScoredPlaintext(b'abcdef')
    print(sp)
    print(sp.score)

    sp2 = ScoredPlaintext(b'\x1b77316?x\x15\x1b\x7f+x413=x9x(7-6<x7>x:9;76')
    print(sp2)
    print(sp2.score)
