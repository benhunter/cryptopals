# hex to base64 conversion
# one base64 digit is six bits of data
# https://cryptopals.com/sets/1/challenges/1

import base64
import binascii

base64_table = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+',
                '/', '=']


def groups(seq, length):
    '''

    :param seq: A slicable object like string or list.
    :param length: The length of each group (ie. 2 for pairs)
    :return:
    '''
    for i in range(0, len(seq), length):
        # print(i)
        yield seq[i:i+length]


def hexbytes_to_bytestr(bytes_data):

    l = list(map(lambda x: chr(int(x, 16)).encode(), groups(bytes_data, 2)))
    s = b''.join(l)
    return s


def bytes_to_base64(data):
    # print('input', data)

    b64 = ''
    for triplet in groups(data, 3):
        len_triplet = len(triplet)  # Store in case len(triplet) == 1.
        # 6 bits from triplet[0]
        r0 = triplet[0] >> 2

        if len_triplet == 1:
            # Add a byte with zeros so that triplet[1] succeeds.
            # This changes the len(triplet), which is why we stored it earlier.
            triplet = b''.join((triplet, b'\x00'))
            r2 = 64
            r3 = 64

        # 2 bits from triplet[0] and 4 bits from triplet[1].
        r1 = triplet[0] & 0b11
        r1 = r1 << 4
        temp = triplet[1] >> 4
        r1 = r1 | temp

        if len_triplet > 1:

            # 4 bits from triplet[1] and 2 bits from triplet[2].
            r2 = triplet[1] & 0b00001111
            r2 = r2 << 2

            if len_triplet == 3:

                temp = triplet[2] & 0b11000000
                temp = temp >> 6
                r2 |= temp

                # 6 bits from triplet[2]
                r3 = triplet[2] & 0b00111111

            elif len_triplet == 2:

                # triplet[2] is empty
                r3 = 64


        b64 += base64_table[r0]
        b64 += base64_table[r1]
        b64 += base64_table[r2]
        b64 += base64_table[r3]

    # print('output', b64)
    return b64


def bytes_to_base64_original(data):
    b64 = ''
    for triplet in groups(data, 3):

        # 6 bits from triplet[0]
        r0 = triplet[0] >> 2

        if len(triplet) == 3:
            r1 = triplet[0] & 0b11
            r1 = r1 << 4
            temp = triplet[1] >> 4
            r1 = r1 | temp

            # 4 bits from triplet[1] and 2 bits from triplet[2]
            r2 = triplet[1] & 0b00001111
            r2 = r2 << 2
            temp = triplet[2] & 0b11000000
            temp = temp >> 6
            r2 |= temp

            # 6 bits from triplet[2]
            r3 = triplet[2] & 0b00111111

        elif len(triplet) == 2:

            # 2 bits from triplet[0] and 4 bits from triplet[1]
            r1 = triplet[0] & 0b11
            r1 = r1 << 4
            temp = triplet[1] >> 4
            r1 = r1 | temp

            # 4 bits from triplet[1] and 2 bits from triplet[2]
            r2 = triplet[1] & 0b00001111
            r2 = r2 << 2

            # triplet[2] is empty
            r3 = 64

        elif len(triplet) == 1:
            print('triplet is length 1')
            print('before join', triplet)
            triplet = b''.join((triplet, b'\x00'))
            print('after join', triplet)

            # 2 bits from triplet[0] and 4 bits from triplet[1]
            r1 = triplet[0] & 0b11
            r1 = r1 << 4
            temp = triplet[1] >> 4
            r1 = r1 | temp

            r2 = 64
            r3 = 64

        b64 += base64_table[r0]
        b64 += base64_table[r1]
        b64 += base64_table[r2]
        b64 += base64_table[r3]

    return b64


def test_hex_to_base64():

    tests = {'49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d':'SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t',
             '49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6': 'SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb28G',
             '49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f': 'SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb28=',
             '49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6': 'SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hybwY=',
             '49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f': 'SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hybw==',
             '49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726': 'SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyBg=='
             }

    # Test everything in the dict. Key is hexbytes, value is base64.
    for test in tests:
        assert bytes_to_base64(hexbytes_to_bytestr(test.encode())) == tests[test]

        if len(test) % 2 != 0:
            pass
        else:
            assert bytes_to_base64(hexbytes_to_bytestr(test.encode())) == base64.b64encode(binascii.unhexlify(test)).decode()

    # Test a single case if needed:
    # t = '49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f'
    # a = bytes_to_base64(hexbytes_to_bytestr(t.encode()))
    # b = base64.b64encode(binascii.unhexlify(t)).decode()
    # assert a == b


if __name__ == '__main__':

    data = '49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d'

    bin_data = data.encode()
    unhex = binascii.unhexlify(data)
    # unhex = binascii.unhexlify(bin_data)
    print(unhex)
    b64 = base64.b64encode(unhex)
    print(b64.decode())
    # print(b64)

    s = hexbytes_to_bytestr(bin_data)
    print(bytes_to_base64(s))

    # hexlify output test
    print('hexlify output type:', type(binascii.hexlify(unhex)))


''' Base64 Table

 0 A
 1 B
 2 C
 3 D
 4 E
 5 F
 6 G
 7 H
 8 I
 9 J
10 K
11 L
12 M
13 N
14 O
15 P
16 Q                                 
17 R
18 S
19 T
20 U
21 V
22 W
23 X
24 Y
25 Z
26 a
27 b
28 c
29 d
30 e
31 f
32 g
33 h
34 i
35 j
36 k
37 l
38 m
39 n
40 o
41 p
42 q
43 r
44 s
45 t
46 u
47 v
48 w
49 x
50 y
51 z
52 0
53 1
54 2
55 3
56 4
57 5
58 6
59 7
60 8
61 9
62 +
63 /
(pad) =

'''
