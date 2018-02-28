import util


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
    # bytearray
    # extended = single_byte * len(multiple_byte)

    extended = b''.join(single_byte for i in range(len(multiple_byte)))

    # print('single_byte_xor len:', len(multiple_byte), 'extended:', len(extended), type(extended), extended)
    return fixed_xor(multiple_byte, extended)


def decode_single_byte_xor(cipherbytes):
    # print('Decoding cipherbytes:', len(cipherbytes), type(cipherbytes), cipherbytes)

    # generate and score all possible single-byte xor results

    scores = []
    for x in range(256):
        # print('decode for loop:', hex(x))
        result = single_byte_xor(cipherbytes, bytes([x]))
        # print('decode for loop: x:', x, 'result:', type(result), result)

        scores.append(util.ScoredPlaintext(result))

    # return the most probable result
    scores.sort(key=lambda x: x.score, reverse=True)
    # for sp in scores:
    #     print(sp)

    return scores[0].bytestr


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

    decode = decode_single_byte_xor(cipher_bytestr)
    # print(decode)
    assert decode == b"Cooking MC's like a pound of bacon"
