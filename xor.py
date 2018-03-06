# local code imports
# library imports
import pytest

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

        scores.append(util.ScoredPlaintext(result, scoring_func=util.plaintext_score_complex))
        # Or use a different scoring function:
        #   Such as: util.ScoredPlaintext(result, scoring_func=util.plaintext_score_complex)

    # return the most probable result
    scores.sort(key=lambda x: x.score, reverse=True)

    return scores


def expand_str(text, length):
    return (text * (length // len(text) + 1))[:length]


def repeating_key_xor(text, key):
    return fixed_xor(text, expand_str(key, len(text)))


def hamming_dist(strone, strtwo):
    '''
    Count the number of bits that differ between two bytestrings
    :param strone:
    :param strtwo:
    :return:
    '''
    assert len(strone) == len(strtwo)

    sum = 0
    for i in range(len(strone)):
        xored = strone[i] ^ strtwo[i]
        diff = 0
        while xored > 0:
            if xored % 2 == 1:
                diff += 1
            xored = xored // 2
        sum += diff
        if DEBUG: print(strone, strtwo, strone[i], strtwo[i], diff, sum)

    return sum


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
    pass
