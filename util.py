# Utilities for cryptopals.

# standard library imports
from collections import namedtuple

# external library imports

# Set True to print logs
DEBUG = False

# letter_frequency = b'ETAOIN SHRDLU'
'''
http://norvig.com/mayzner.html
TODO Need to include space. 
letter %
'''
letter_freq = {
    b'E': 0.1249,
    b'T': 0.0928,
    b'A': 0.0804,
    b'O': 0.0764,
    b'I': 0.0757,
    b'N': 0.0723,
    b'S': 0.0651,
    b'R': 0.0628,
    b'H': 0.0505,
    b'L': 0.0407,
    b'D': 0.0382,
    b'C': 0.0334,
    b'U': 0.0273,
    b'M': 0.0251,
    b'F': 0.0240,
    b'P': 0.0214,
    b'G': 0.0187,
    b'W': 0.0168,
    b'Y': 0.0166,
    b'B': 0.0148,
    b'V': 0.0105,
    b'K': 0.0054,
    b'X': 0.0023,
    b'J': 0.0016,
    b'Q': 0.0012,
    b'Z': 0.0009
}

letter_table = {
    b'E': 15,
    b'T': 14,
    b'A': 13,
    b'O': 12,
    b'I': 11,
    b'N': 10,
    b' ': 9,
    b'S': 8,
    b'H': 7,
    b'R': 6,
    b'D': 5,
    b'L': 4,
    b'U': 3
}

# A set of english dictionary words for plaintext_score_dict(). Keeps list in memory instead of loading from file
# multiple times during exectution.
word_set = None  # None means the dictionary file hasn't been loaded yet.
DICTIONARY_FILE = 'MainEnglishDictionary_ProbWL.txt'


def groups(seq, length):
    '''
    Yield groups of specified length from a sequence. The final yield will provide whatever data is left in the
    sequence, without padding. Useful in a for statement:
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


def bytestr_to_hexbytes(bytestr):
    # return b''.join([(b'%x' % b) for b in bytestr])  # Doesn't pad to two chars for hex values less than 10.
    return b''.join(['{0:02x}'.format(b).encode() for b in bytestr])


def plaintext_score(bytestr):
    '''
    Quick and dirty scoring method that uses the most common english letters.
    :param bytestr: Bytes to check
    :return: Int score.
    '''


    # count frequency in bytestr
    # score based on similarity to common frequency
    score = 0
    bytestr_upper = bytestr.upper()

    for i, letter in enumerate(letter_table.keys()):
        score += bytestr_upper.count(letter) * letter_table[letter]

    # if bytestr.count(b' ') < 5:
    #     # print('NOT ENOUGH SPACES')
    #     # return 0
    #     pass

    return score


def plaintext_score_complex(bytestr):

    # print(bytestr)
    # print('len', len(bytestr))

    score = 0

    # weights
    COMMON_WEIGHT = 10  # 3
    PUNCTUATION_WEIGHT = 0  # 1
    WEIRD_CHAR_PENALTY = 0
    ISPRINTABLE_WEIGHT = 10  # 10
    UNICODEDECODEERROR_WEIGHT = 0  # -15
    NO_SPACES_PENALTY = -2000
    CONSECUTIVE_SPACES_PENALTY = -1000
    COMMON_WORD_BONUS = 0

    common_words = [b'FLAG', b'THE', b'AND', b'OR', b'FOR', b'YOU', b"'RE"]

    bytestr_upper = bytestr.upper()

    for i, letter in enumerate(letter_table.keys()):
        score += bytestr_upper.count(letter) * letter_table[letter]

    # print(bytestr)
    for byte in bytestr:
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


def plaintext_score_dict(bytestr):
    '''
    Score based on appreance of words from an English Dictionary.
    Dictionary here:
    https://github.com/berzerk0/Probable-Wordlists/tree/master/Dictionary-Style#mainenglishdictionary_probwltxt

    Must call load_dict() before calling this function.

    :param bytestr:
    :return:
    '''
    if DEBUG: print(bytestr)
    if DEBUG: print('len', len(bytestr))

    # List loaded from file of dictionary words
    global word_set

    # Load the dictionary into memory if it hasn't already been done.
    if not word_set:
        load_dict(DICTIONARY_FILE)

    score = 0

    # weights
    WORD_BONUS = 1
    UNICODEDECODEERROR_WEIGHT = 0


    try:
        for word in bytestr.split(b' '):
            if DEBUG: print(word)
            if word.lower().decode() in word_set:
                score += WORD_BONUS
                if DEBUG: print("WORD_BONUS", word)

    except UnicodeDecodeError:
        score -= UNICODEDECODEERROR_WEIGHT

    # print('score', score)
    return score


def plaintext_score_historgram(bytestr):
    '''
    Stack percentages of each character. Closest to normal histogram wins.
    :param bytestr:
    :return:
    '''
    # TODO
    return 0


def plaintext_score_diff_from_norm(bytestr):
    '''
    Count the percentage points from normal for each alphabet character.
    TODO Golf score? Or invert to make a %?
    :param bytes:
    :return:
    '''

    this_letter_freq = letter_freq

    score = 0

    for char in letter_freq.keys():
        # print(char, type(char))
        # print(bytestr.upper().count(char))
        # print(bytestr.upper().count(char) / len(bytestr))
        # this_letter_freq[char] = bytestr.upper().count(char) / len(bytestr)

        score += abs(letter_freq[char] - (bytestr.upper().count(char) / len(bytestr)))

    # pprint(this_letter_freq)
    # sorted_freq = OrderedDict(sorted(this_letter_freq.items(), key=lambda x: x[1], reverse=True))
    # pprint(sorted_freq)

    punctuation_boost = 0
    punctuation_set = b'\'.,;?!'
    for punc in punctuation_set:
        if bytestr.count(punc) > 0:
            punctuation_boost += 1

    # try:
    #     if not bytestr.decode().isprintable():
    #         return 0
    # except UnicodeDecodeError:
    #     return 0

    if score == 0:
        return 0

    return 100 / score + punctuation_boost


def load_dict(file):
    global word_set
    word_set = set()

    with open(file) as f:
        for line in f.readlines():
            word_set.add(line.strip())

        # if DEBUG: print(dictionary)
        if DEBUG: print(type(word_set))
        if DEBUG: print(len(word_set))
        # if DEBUG: print(dictionary[100])
        return

    raise IOError("Failed to load dictionary from file: " + file)


class ScoredPlaintext(namedtuple('ScoredPlaintext', 'bytestr')):
    def __new__(cls, bytestr, scoring_func=plaintext_score_diff_from_norm, key=None):
        self = super(ScoredPlaintext, cls).__new__(cls, bytestr)
        self._score = scoring_func(bytestr)
        self._key = key
        return self

    @property
    def score(self):
        return self._score

    def key(self):
        return self._key

    def __str__(self):
        if self._key:
            return "ScoredPlaintext: Key: " + str(self._key) + "\tScore: " + str(self.score) + "\tBytestring: " + str(
                self.bytestr)
        return "ScoredPlaintext: Score: " + str(self.score) + "\tBytestring: " + str(self.bytestr)


########
#  TESTS
def test_groups():
    data = 'abcde'
    for pair in groups(data, 2):
        print(pair)

    pair_list = [pairs for pairs in groups(data, 2)]
    assert pair_list == ['ab', 'cd', 'e']

    data = b'abcde'
    for pair in groups(data, 2):
        print(pair)

    pair_list = [pairs for pairs in groups(data, 2)]
    assert pair_list == [b'ab', b'cd', b'e']


def test_ScoredPlaintext():
    sp = ScoredPlaintext(b'abcdef')
    print(sp)
    print(sp.score)

    sp2 = ScoredPlaintext(b'\x1b77316?x\x15\x1b\x7f+x413=x9x(7-6<x7>x:9;76', scoring_func=plaintext_score)
    print(sp2)
    print(sp2.score)
    print(plaintext_score_dict("This is a test sentence!".encode()))
    print(plaintext_score_dict(
        b'\x0b\n\x0bZ\x0fZ\t_\x0bY\x0b\x02\t\r\x0b\x03\t_\t]\n\x0e\t\x0e\x0e\r\t_\n_\x0b\x0c\x0bZ\x0cZ\x0b\x03\n\x0e\t]\x0eY\x0f\x0f\x08\x03Z\x0f\n\x0e\x0bY\n\x08\t^\t\x0b1'))


def test_ScoredPlaintext_diff_from_norm():
    print(ScoredPlaintext(b'test test test', scoring_func=plaintext_score_diff_from_norm))
    print(ScoredPlaintext(b'This is only a test.', scoring_func=plaintext_score_diff_from_norm))
    print(ScoredPlaintext(
        b'In addition to the usual mapping methods, ordered dictionaries also support reverse iteration using reversed().',
        scoring_func=plaintext_score_diff_from_norm))


def test_load_dict():
    load_dict(DICTIONARY_FILE)
    # print(word_set)
    assert plaintext_score_dict(b'this is only a test') == 5
    assert 'test' in word_set


def test_bytestr_to_hexbytes():
    print(bytestr_to_hexbytes(b'AAAA'))
    assert bytestr_to_hexbytes(b'AAAA') == b'41414141'

    print(bytestr_to_hexbytes(b'\x01'))
    assert bytestr_to_hexbytes(b'\x01') == b'01'
