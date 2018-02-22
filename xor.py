import base_64


def fixed_xor(one, two):
    '''
    Returns XOR combination of two equal length bytestrings.
    :param one:
    :param two:
    :return:
    '''

    result = ''

    print(len(one))
    # test equal len
    if len(one) != len(two):
        raise Exception('Parameter lengths are not equal.')
    # xor byte by byte

    for i in range(len(one)):
        print(one, one[i], type(one[i]))
        # result += chr(one[i] ^ two[i]).encode()
        result += format(one[i] ^ two[i], 'x')
        print(result, type(result))

    return result


def test_fixed_xor():
    hexstr = b'1c0111001f010100061a024b53535009181c'
    one = hexstr
    two = b'686974207468652062756c6c277320657965'

    onebytestr = base_64.hexbytes_to_bytestr(one)
    print(onebytestr)
    print(str(onebytestr))
    print(len(onebytestr))
    xor_result = fixed_xor(onebytestr, base_64.hexbytes_to_bytestr(two))
    print('xor_result', xor_result, type(xor_result))
    answer = b'746865206b696420646f6e277420706c6179'
    print('answer', answer)
    assert xor_result.encode() == answer
