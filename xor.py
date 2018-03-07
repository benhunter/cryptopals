# standard library imports
import statistics
from collections import namedtuple
from itertools import zip_longest

# library imports
import pytest

import base_64
# local code imports
import util

# Set True to print debug messages.
DEBUG = False

def fixed_xor(one, two):
    '''
    Returns XOR combination of two equal length bytestrings.
    :param one: Bytes
    :param two: Bytes
    :return: Bytes
    '''

    result = b''

    # print(len(one))
    # test equal len
    if len(one) != len(two):
        raise ValueError('Parameter lengths are not equal.', len(one), len(two), one, two)
    # xor byte by byte

    for i in range(len(one)):
        # print(one, one[i], type(one[i]))
        xor_result = one[i] ^ two[i]
        result += bytes([xor_result])
        # result += format(one[i] ^ two[i], 'x')
        # print(result, type(result))

    # print('fixed_xor:', type(result), result)
    return result


def single_byte_xor(multiple_byte, single_byte):
    extended = single_byte * len(multiple_byte)
    # print('single_byte_xor len:', len(multiple_byte), 'extended:', len(extended), type(extended), extended)
    return fixed_xor(multiple_byte, extended)


def decode_single_byte_xor(cipherbytes):
    decode_all_single_byte_xor(cipherbytes)[0]


def decode_all_single_byte_xor(cipherbytes):
    # print('Decoding cipherbytes:', len(cipherbytes), type(cipherbytes), cipherbytes)

    # generate and score all possible single-byte xor results
    scores = []
    for x in range(256):
        # print('decode for loop:', hex(x))
        result = single_byte_xor(cipherbytes, bytes([x]))
        # print('decode for loop: x:', x, 'result:', type(result), result)

        # scores.append(util.ScoredPlaintext(result, scoring_func=util.plaintext_score_complex))
        scores.append(util.ScoredPlaintext(result, scoring_func=util.plaintext_score))
        # Or use a different scoring function:
        #   Such as: util.ScoredPlaintext(result, scoring_func=util.plaintext_score_complex)

    # return the most probable result
    scores.sort(key=lambda x: x.score, reverse=True)

    return scores


def expand_str(text, length):
    return (text * (length // len(text) + 1))[:length]


def repeating_key_xor(text, key):
    return fixed_xor(text, expand_str(key, len(text)))


def hamming_dist(str_one, str_two):
    '''
    Count the number of bits that differ between two bytestrings.
    :param str_one:
    :param str_two:
    :return:
    '''
    assert len(str_one) == len(str_two)

    sum = 0
    for i in range(len(str_one)):
        xored = str_one[i] ^ str_two[i]
        diff = 0
        while xored > 0:
            if xored % 2 == 1:
                diff += 1
            xored = xored // 2
        sum += diff
        if DEBUG: print(str_one, str_two, str_one[i], str_two[i], diff, sum)

    return sum


def find_xor_key_length(cipher, KEYSIZE_MIN, KEYSIZE_MAX, NUM_BLOCKS):
    '''


    :param cipher:
    :param KEYSIZE_MIN:
    :param KEYSIZE_MAX:
    :return: Length of xor key size with lowest average hamming distance.
    '''

    assert KEYSIZE_MIN < KEYSIZE_MAX

    # find edit/hamming distance
    # hammdist(block1, block2) / KEYSIZE
    #  or  statistics.mean(all_hammdist(block1, 2, 3, 4) / KEYSIZE
    # minimum hammdist of all tested KEYSIZES is most likely key length

    distances = []
    KeyLengthTuple = namedtuple('KeyLengthTuple', 'key_len hamming_dist')
    for keylen in range(KEYSIZE_MIN, KEYSIZE_MAX + 1):
        blocks = []
        # TODO rewrite as list comprehension
        for i in range(NUM_BLOCKS):
            blocks.append(cipher[i * keylen:(i + 1) * keylen])  # 0:keysize, keysize:keysize+keysize,
        # print(blocks)

        block_hamm_dists = []
        for i in range(len(blocks) - 1):
            # print('hamming:', blocks[i], blocks[i + 1])
            block_hamm_dists.append(hamming_dist(blocks[i], blocks[i + 1]))

        dist = statistics.mean(block_hamm_dists) / keylen
        distances.append(KeyLengthTuple(keylen, dist))

    def key(keylengthtuple):
        return (keylengthtuple.hamming_dist)

    distances = sorted(distances, key=key)
    # pprint(distances)

    # print(min(distances, key=key))
    return min(distances, key=key).key_len



########
#  TESTS
def test_fixed_xor():
    hexstr = b'1c0111001f010100061a024b53535009181c'
    one = hexstr
    two = b'686974207468652062756c6c277320657965'

    onebytestr = util.hexbytes_to_bytestr(one)
    # print(onebytestr)
    # print(str(onebytestr))
    # print(len(onebytestr))
    xor_result = fixed_xor(onebytestr, util.hexbytes_to_bytestr(two))
    # print('xor_result', xor_result, type(xor_result))
    answer = b'746865206b696420646f6e277420706c6179'
    # print('answer', answer)
    assert xor_result == util.hexbytes_to_bytestr(answer)


def test_singlebyte_xor():
    cipher_hex_bytes = b'1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736'
    cipher_bytestr = util.hexbytes_to_bytestr(cipher_hex_bytes)
    # print('Test - cipher_bytestr:', cipher_bytestr)

    decode = decode_all_single_byte_xor(cipher_bytestr)[0]
    # print(decode)
    assert decode.bytestr == b"Cooking MC's like a pound of bacon"


def test_expand_str():
    assert expand_str('1', 10) == '1111111111'
    assert expand_str(b'1', 10) == b'1111111111'
    assert expand_str(b'12', 10) == b'1212121212'
    assert expand_str(b'12', 11) == b'12121212121'


def test_hamming_dist():
    assert hamming_dist(b'', b'') == 0
    assert hamming_dist(b'test', b'test') == 0
    assert hamming_dist(b'a', b'b') == 2
    assert hamming_dist(b'this is a test', b'wokka wokka!!!') == 37
    with pytest.raises(TypeError):
        assert hamming_dist('this is a test', 'wokka wokka!!!') == 37


# TODO
def test_find_xor_key_length():
    print('find_xor_key_length', find_xor_key_length())


###########
# SOLUTIONS
def test_solve_set1_chall4():
    all_plain = []
    top_plain = []
    with open('4.txt') as f:
        for line in f.readlines():
            if DEBUG: print(line)
            converted = util.hexbytes_to_bytestr(line.strip().encode())
            all_plain += decode_all_single_byte_xor(converted)
            top_plain.append(decode_all_single_byte_xor(converted)[0])

        all_plain.sort(key=lambda x: x.score, reverse=True)
        top_plain.sort(key=lambda x: x.score, reverse=True)

        print("Place : Result (all decoded scores)")
        for i in range(10):
            print(str(i) + ':', all_plain[i])

        print("Place : Result (top decoded scores)")
        for i in range(10):
            print(str(i) + ':', top_plain[i])

    assert all_plain[0].bytestr == b'Now that the party is jumping\n'
    assert top_plain[0].bytestr == b'Now that the party is jumping\n'


def test_solve_chall5():
    answer = repeating_key_xor(b'Burning \'em, if you ain\'t quick and nimble\nI go crazy when I hear a cymbal', b'ICE')
    # print(answer)
    # print(util.bytestr_to_hexbytes(answer))
    assert util.bytestr_to_hexbytes(
        answer) == b'0b3637272a2b2e63622c2e69692a23693a2a3c6324202d623d63343c2a26226324272765272a282b2f20430a652e2c652a3124333a653e2b2027630c692b20283165286326302e27282f'


def test_solve_chall6():
    '''
    1) Let KEYSIZE be the guessed length of the key; try values from 2 to (say) 40.

    2) Write a function to compute the edit distance/Hamming distance between two strings. The Hamming distance is just
    the number of differing bits. The distance between:
        this is a test
        and
        wokka wokka!!!
        is 37. Make sure your code agrees before you proceed.

    3) For each KEYSIZE, take the first KEYSIZE worth of bytes, and the second KEYSIZE worth of bytes, and find the edit
    distance between them. Normalize this result by dividing by KEYSIZE.

    4) The KEYSIZE with the smallest normalized edit distance is probably the key. You could proceed perhaps with the smallest 2-3 KEYSIZE values. Or take 4 KEYSIZE blocks instead of 2 and average the distances.

    5) Now that you probably know the KEYSIZE: break the ciphertext into blocks of KEYSIZE length.

    6) Now transpose the blocks: make a block that is the first byte of every block, and a block that is the second byte of every block, and so on.

    7) Solve each block as if it was single-character XOR. You already have code to do this.

    8) For each block, the single-byte XOR key that produces the best looking histogram is the repeating-key XOR key byte for that block. Put them together and you have the key.
    '''

    KEYSIZE_RANGE_MIN = 2  # Inclusive range of possible key sizes to search
    KEYSIZE_RANGE_MAX = 40
    NUMBER_OF_BLOCKS = 4  # TODO 2, 4 also suggested. 6 jumps to 20.

    with open('6.txt') as f:
        cipher = [x.rstrip('\n').encode() for x in f.readlines()]
        # print(cipher)
        # print()

        # TODO is this really one big string????
        cipher = b''.join(cipher)
        # Un-Base64 AFTER joining, not before
        cipher = base_64.base64_to_bytes(cipher)
        # print(cipher, len(cipher))

        # for cipher in cipher:

        likely_xor_key_length = find_xor_key_length(cipher, KEYSIZE_RANGE_MIN, KEYSIZE_RANGE_MAX, NUMBER_OF_BLOCKS)
        print('likely_xor_key_length', likely_xor_key_length)

        transposed = [bytearray(b'') for i in range(likely_xor_key_length)]
        for block in util.groups(cipher, likely_xor_key_length):
            if len(block) < likely_xor_key_length:
                continue
            for position in range(likely_xor_key_length):
                transposed[position].append(block[position])
        # pprint(transposed)
        # print(transposed)
        # print(len(transposed))

        xor_decoded = []
        for transposed_block in transposed:
            # print('decoding block:', transposed_block)
            xor_decoded.append(decode_all_single_byte_xor(transposed_block)[0].bytestr)
            print('decoding result:', xor_decoded)

        # pprint(xor_decoded)

        # de-transpose
        # pprint(list(zip_longest(*xor_decoded)))

        result = bytearray()
        for bytes in zip_longest(*xor_decoded):
            print(bytes, type(bytes))
            for b in bytes:
                result.append(b)
        print(result, len(result))
