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
    letter_frequency = b'ETAOIN SHRDLU'

    # count frequency in bytestr
    # score based on similarity to common frequency
    score = 0
    bytestr_upper = bytestr.upper()
    for i, letter in enumerate(letter_frequency):
        score += bytestr_upper.count(letter) * (15 - i)

    if bytestr.count(b' ') < 5:
        # print('NOT ENOUGH SPACES')
        return 0

    return score


def plaintext_score_complex(bytestr):

    # print(bytestr)
    # print('len', len(bytestr))

    score = 0

    # weights
    COMMON_WEIGHT = 10  # 3
    PUNCTUATION_WEIGHT = 0  # 1
    WEIRD_CHAR_PENALTY = -10
    ISPRINTABLE_WEIGHT = 10  # 10
    UNICODEDECODEERROR_WEIGHT = 0  # -15
    NO_SPACES_PENALTY = -2000
    CONSECUTIVE_SPACES_PENALTY = -1000
    COMMON_WORD_BONUS = 0

    letter_frequency = b'ETAOIN SHRDLU'
    common_words = [b'FLAG', b'THE', b'AND', b'OR', b'FOR', b'YOU', b"'RE"]

    # print(bytestr)
    for byte in bytestr:

        for i, char in enumerate(letter_frequency):
            # print(byte, i, char)
            if bytes([byte]).upper() == bytes([char]):
                score += (len(letter_frequency) - i) * COMMON_WEIGHT

        # if bytes([byte]) in b',.?;:\'"/:!':
        #     score += PUNCTUATION_WEIGHT

        if bytes([byte]) in br'\/#$%|<>=&':
            score += WEIRD_CHAR_PENALTY

    try:
        if bytestr.decode().isprintable():
            score += ISPRINTABLE_WEIGHT

        if b' ' not in bytestr:
            score += NO_SPACES_PENALTY

        if b'  ' in bytestr:
            score += CONSECUTIVE_SPACES_PENALTY

        for word in common_words:
            if word.upper() in bytestr.upper():
                score += COMMON_WORD_BONUS
                # print("COMMON_WORD_BONUS", word)

    except UnicodeDecodeError:
        score -= UNICODEDECODEERROR_WEIGHT

    # print('score', score)
    return score


class ScoredPlaintext(namedtuple('ScoredPlaintext', 'bytestr')):
    def __new__(cls, bytestr):
        self = super(ScoredPlaintext, cls).__new__(cls, bytestr)
        self._score = \
            (bytestr)
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
