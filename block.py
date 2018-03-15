# pycrypto library
# https://pypi.python.org/pypi/pycrypto/
# https://pythonhosted.org/pycrypto/

import base64
import itertools
# import secrets
import os  # TODO use Python 3.6 secrets
import random

from Crypto.Cipher import AES

import util
import xor

BLOCK_SIZE = 16

def pkcs7pad(text, length):
    # Common padding for CBC mode block ciphers
    if len(text) > length:
        raise RuntimeError("Text to be padded is longer than requested length.")
    if type(text) is not bytes:
        raise TypeError("Text must be bytes.")
    diff = length - len(text)
    padding = bytearray([diff for x in range(diff)])
    return text + padding


def aes_ecb_encrypt(data, key):
    '''
    Encrypt bytes using AES ECB algorithm.
    :param data:
    :param key:
    :return:
    '''
    diff = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    padding = bytearray([diff for x in range(diff)])
    return AES.new(key=key, mode=AES.MODE_ECB).encrypt(data + padding)


def aes_ecb_decrypt(data, key):
    '''
    Decrypt bytes using AES ECB algorithm.
    :param data:
    :param key:
    :return:
    '''

    plaintext = AES.new(key=key, mode=AES.MODE_ECB).decrypt(data)
    # TODO remove padding
    # detect and remove PKCS7 padding
    if plaintext[-1] < BLOCK_SIZE:
        # how many bytes to remove? BLOCK_SIZE - result[-1]
        plaintext = plaintext[:-plaintext[-1]]
    return plaintext


def aes_cbc_encrypt(data, key, IV):
    '''
    Encrypt Cipher Block Chaining (CBC) with AES on each block.
    https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher_Block_Chaining_(CBC)
    :param data: Plaintext bytes.
    :param key: Bytes to encrypt.
    :param IV: Initialization Vector. Must be block size (16 bytes default).
    :return:
    '''

    if len(IV) is not BLOCK_SIZE:
        raise ValueError("IV must be " + str(BLOCK_SIZE) + " bytes.")

    # AES instance for decrypting
    aes_cipher = AES.new(key=key, mode=AES.MODE_ECB)

    # iterator for grabbing sequential blocks from data
    next_block = util.groups(data, BLOCK_SIZE)
    all_blocks = list(next_block)

    # first block
    plain_block = all_blocks[0]

    # xor with IV
    xor_block = xor.fixed_xor(plain_block, IV)
    # print(xor_block, len(xor_block), type(xor_block))

    # encrypt
    encrypt_block = aes_cipher.encrypt(xor_block)
    result = encrypt_block

    prev_cipher_block = encrypt_block
    # while more data:
    for plain_block in all_blocks[1:]:
        if len(plain_block) < BLOCK_SIZE:
            plain_block = pkcs7pad(plain_block, BLOCK_SIZE)
        xor_block = xor.fixed_xor(prev_cipher_block, plain_block)
        decrypt_block = aes_cipher.encrypt(xor_block)
        # print(xor_block, len(xor_block))
        result += decrypt_block
        prev_cipher_block = decrypt_block
        # encrypt next block
    return result


def aes_cbc_decrypt(data, key, IV):
    '''
    Decrypt Cipher Block Chaining (CBC) with AES on each block.
    https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher_Block_Chaining_(CBC)
    :param data: Encrypted bytes.
    :param key: Bytes to decrypt.
    :param IV: Initialization Vector. Must be block size (16 bytes default).
    :return:
    '''

    if len(IV) is not BLOCK_SIZE:
        raise ValueError("IV must be " + str(BLOCK_SIZE) + " bytes.")

    # AES instance for decrypting
    aes_cipher = AES.new(key=key, mode=AES.MODE_ECB)

    # iterator for grabbing sequential blocks from data
    next_block = util.groups(data, BLOCK_SIZE)
    all_blocks = list(next_block)

    # 0th block with IV
    cipher_block = all_blocks[0]

    # decrypt first block
    decrypt_block = aes_cipher.decrypt(cipher_block)

    # xor with IV
    xor_block = xor.fixed_xor(decrypt_block, IV)
    # print(xor_block, len(xor_block), type(xor_block))
    result = xor_block

    prev_cipher_block = cipher_block
    # while more data:
    for cipher_block in all_blocks[1:]:
        decrypt_block = aes_cipher.decrypt(cipher_block)
        xor_block = xor.fixed_xor(prev_cipher_block, decrypt_block)
        # print(xor_block, len(xor_block))
        result += xor_block
        prev_cipher_block = cipher_block
        # decrypt next block

    # detect and remove PKCS7 padding
    if result[-1] < BLOCK_SIZE:
        # how many bytes to remove? BLOCK_SIZE - result[-1]
        result = result[:-result[-1]]

    return result


def random_aes_key():
    # return secrets.token_bytes(16)
    return os.urandom(16)


def encrypt_randomly(data, key):
    # randomly use ECB or CBC encryption

    # Add random 5-10 bytes before data.
    pre = os.urandom(5) + os.urandom(ord(os.urandom(1)) % 6)
    # print(pre, len(pre))
    # Add random 5-10 bytes after data.
    post = os.urandom(5) + os.urandom(ord(os.urandom(1)) % 6)

    # choose ECB or CBC randomly
    # encrypt_func = random.SystemRandom().choice([aes_ecb_encrypt, aes_cbc_encrypt])  # won't work becuase different function signatures.
    if random.SystemRandom().choice((True, False)):
        return aes_ecb_encrypt(data, key)
    else:
        IV = os.urandom(BLOCK_SIZE)
        return aes_cbc_encrypt(data, key, IV)


def detect_aes_cbc(data):
    '''
    Detects AES CBC by looking for two identical blocks.
    :param data: Encrypted bytes.
    :return: Bool, true if CBC is detected.
    '''
    for combo in itertools.combinations(util.groups(data[:-1], 16), 2):
        if combo[0] == combo[1]:
            return True
    return False


def detect_aes_mode(data):
    # TODO detect AES mode ECB or CBC
    return 'ECB' if detect_aes_cbc(data) else 'CBC'


def test_aes_ecb_encrypt():
    # Set 1, Challenge 7
    # TODO implement
    data = b"Ehrsam, Meyer, Smith and Tuchman invented the Cipher Block Chaining (CBC) mode of operation in 1976."
    key = 'YELLOW SUBMARINE'
    ciphertext = aes_ecb_encrypt(data, key)
    plaintext = aes_ecb_decrypt(ciphertext, key)
    # print(plaintext)
    assert plaintext == data


def test_aes_ecb_decrypt():
    # Set 1, Challenge 7
    # TODO should we strip that padding bytes at the end?

    cipher_file = '7.txt'
    key = 'YELLOW SUBMARINE'

    with open(cipher_file) as f:
        text = f.read()
        # print(text)
        # print(len(text))
        text = text.replace('\n', '')
        # print(text)
        # print(len(text))

        # ciphertext = base64.b64decode(f.read())  # TODO fix my base_64 code to do this. Some weird parse error
        ciphertext = base64.b64decode(text)

        # ends with: {~\xaf\x80\xc8p\xedr\xbb\xce\x1f\xff\x8c-\x87

        # ciphertext = base_64.base64_to_bytes(f.read())
        # ciphertext = base_64.base64_to_bytes(text)
        # ends with: {~\xaf\x80\xc8p\xedr\xbb\xce\x1f\xff\x8c-\x87

        # lines = ''.join([x.rstrip('\n') for x in f.readlines()])
        # ciphertext = base_64.base64_to_bytes(lines)

        # print(ciphertext)
        # print(len(ciphertext))

        aes_cipher = AES.new(key=key, mode=AES.MODE_ECB)
        plaintext = aes_cipher.decrypt(ciphertext)
        print()
        print(plaintext)

        print(aes_ecb_decrypt(ciphertext, key))


def test_detect_aes_ecb():
    # Set 1, Challenge 8
    # 16 byte blocks
    with open("8.txt") as f:
        lines = f.readlines()
        for index, line in enumerate(lines):
            for combo in itertools.combinations(util.groups(util.hexbytes_to_bytestr(line[:-1]), 16), 2):
                if combo[0] == combo[1]:
                    print(index, line)
        print(lines)
    assert detect_aes_cbc(lines[132])


def test_pkcs7_padding():
    # Set 2, Challenge 9
    assert pkcs7pad(b"YELLOW SUBMARINE", 20) == b"YELLOW SUBMARINE\x04\x04\x04\x04"


def test_aes_cbc_encrypt():
    # Set 2, Challenge 10
    data = b"Ehrsam, Meyer, Smith and Tuchman invented the Cipher Block Chaining (CBC) mode of operation in 1976."
    key = b'YELLOW SUBMARINE'
    IV = bytearray([1 for i in range(16)])
    encrypted_data = aes_cbc_encrypt(data, key, IV)
    decrypted_data = aes_cbc_decrypt(encrypted_data, key, IV)
    # print(data)
    # print(decrypted_data)
    assert data == decrypted_data


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


def test_random_aes_key():
    print(random_aes_key())
    print(type(random_aes_key()))


def test_encrypt_randomly():
    # Set 2, Challenge 11
    # plaintext = b"This is only a test. Please keep your seats in the upright and locked position. Prepare for landing."
    plaintext = b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    unknown_crypto = encrypt_randomly(plaintext, random_aes_key())
    # print(unknown_crypto)
    # print(len(unknown_crypto))
    # print(detect_aes_cbc(unknown_crypto))

    # for i in range(100000):
    #     unknown_crypto = encrypt_randomly(plaintext, random_aes_key())
    #     if detect_aes_cbc(unknown_crypto):
    #         print(True)
    print(detect_aes_mode(unknown_crypto))
