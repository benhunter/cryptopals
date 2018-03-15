# pycrypto library
# https://pypi.python.org/pypi/pycrypto/
# https://pythonhosted.org/pycrypto/

import base64
import itertools

from Crypto.Cipher import AES

import util
import xor

BLOCK_SIZE = 16

def pkcs7pad(text, length):
    # Common padding for CBC mode block ciphers
    if len(text) > length:
        raise RuntimeError("Text for padding is longer than requested length.")
    if type(text) is not bytes:
        raise TypeError("Text must be bytes.")
    diff = length - len(text)
    padding = bytearray([diff for x in range(diff)])
    return text + padding


def aes_cbc_decrypt(data, key, IV):
    '''
    Decrypt Cipher Block Chaining (CBC) with AES on each block.
    https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher_Block_Chaining_(CBC)
    :param data: Encrypted bytes.
    :param key: Bytes to decrypt.
    :param IV: Initialization Vector. Must be block size (16 bytes default).
    :return:
    '''
    #

    if len(IV) is not BLOCK_SIZE:
        raise ValueError("IV must be " + str(BLOCK_SIZE) + " bytes.")

    # 0th block with IV
    # decrypt first block
    aes_cipher = AES.new(key=key, mode=AES.MODE_ECB)

    # iterator for grabbing sequential blocks from data
    next_block = util.groups(data, BLOCK_SIZE)
    all_blocks = list(next_block)
    # first block
    cipher_block = all_blocks[0]
    decrypt_block = aes_cipher.decrypt(cipher_block)

    # xor with IV
    xor_block = xor.fixed_xor(decrypt_block, IV)
    print(xor_block, len(xor_block), type(xor_block))
    result = xor_block

    prev_cipher_block = cipher_block
    # while more data:
    for cipher_block in all_blocks[1:]:
        decrypt_block = aes_cipher.decrypt(cipher_block)
        xor_block = xor.fixed_xor(prev_cipher_block, decrypt_block)
        print(xor_block, len(xor_block))
        result += xor_block
        prev_cipher_block = cipher_block
        # encrypt next block
    return result


def test_decrypt_aes_ecb():
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


def test_pkcs7_padding():
    # Set 2, Challenge 9
    assert pkcs7pad(b"YELLOW SUBMARINE", 20) == b"YELLOW SUBMARINE\x04\x04\x04\x04"


def test_aes_cbc_decrypt():
    # Set 2, Challenge 10
    file = '10.txt'
    key = b'YELLOW SUBMARINE'
    IV = bytearray([0 for i in range(16)])

    with open(file) as f:
        ciphertext = base64.b64decode(f.read())  # TODO use my base_64 for this
        print(type(ciphertext))

    plaintext = aes_cbc_decrypt(ciphertext, key, IV)
    print(plaintext.decode())
