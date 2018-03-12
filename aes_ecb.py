
# pycrypto library
# https://pypi.python.org/pypi/pycrypto/
# https://pythonhosted.org/pycrypto/

import base64
import itertools

from Crypto.Cipher import AES

import util


def test_decode_aes_ecb():
    # Set 1, Challenge 7

    cipher_file = '7.txt'
    key = 'YELLOW SUBMARINE'

    with open(cipher_file) as f:
        text = f.read()
        print(text)
        print(len(text))
        text = text.replace('\n', '')
        print(text)
        print(len(text))

        # ciphertext = base64.b64decode(f.read())  # TODO fix my base_64 code to do this. Some weird parse error
        ciphertext = base64.b64decode(text)

        # ends with: {~\xaf\x80\xc8p\xedr\xbb\xce\x1f\xff\x8c-\x87

        # ciphertext = base_64.base64_to_bytes(f.read())
        # ciphertext = base_64.base64_to_bytes(text)
        # ends with: {~\xaf\x80\xc8p\xedr\xbb\xce\x1f\xff\x8c-\x87

        # lines = ''.join([x.rstrip('\n') for x in f.readlines()])
        # ciphertext = base_64.base64_to_bytes(lines)

        print(ciphertext)
        print(len(ciphertext))

        aes_cipher = AES.new(key=key, mode=AES.MODE_ECB)
        plaintext = aes_cipher.decrypt(ciphertext)
        print(plaintext)


def test_detect_aes_ecb():
    # Set 1, Challenge 8
    # 16 byte blocks
    with open("8.txt") as f:
        for index, line in enumerate(f.readlines()):
            for combo in itertools.combinations(util.groups(util.hexbytes_to_bytestr(line[:-1]), 16), 2):
                if combo[0] == combo[1]:
                    print(index, line)
