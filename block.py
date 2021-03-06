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

    data = pre + data + post

    # choose ECB or CBC randomly
    # encrypt_func = random.SystemRandom().choice([aes_ecb_encrypt, aes_cbc_encrypt])  # won't work becuase different function signatures.
    if random.SystemRandom().choice((True, False)):
        return aes_ecb_encrypt(data, key)
    else:
        IV = os.urandom(BLOCK_SIZE)
        return aes_cbc_encrypt(data, key, IV)


def detect_aes_ecb(data):
    '''
    Detects AES ECB by looking for two identical blocks.
    :param data: Encrypted bytes.
    :return: Bool, true if CBC is detected.
    '''
    for combo in itertools.combinations(util.groups(data[:-1], BLOCK_SIZE), 2):
        if combo[0] == combo[1]:
            return True
    return False


def detect_aes_mode(data):
    # detect AES mode ECB or CBC
    return 'ECB' if detect_aes_ecb(data) else 'CBC'


def parse_cookie(string):
    d = {}
    print(string)
    for i in string.split('&'):
        pair = i.split('=')
        d[pair[0]] = pair[1]
    return d


def profile_format(email):
    email = email.replace('&', '')
    email = email.replace('=', '')

    return parse_cookie('email=' + email + '&uid=10&role=user')


def encode_profile(profile):
    return ('email=' + profile['email'] + '&uid=' + profile['uid'] + '&role=' + profile['role']).encode()


def test_aes_ecb_encrypt():
    # Set 1, Challenge 7
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
    assert detect_aes_ecb(lines[132])


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
    # plaintext = b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"  # before padding, min length of repeating char is 32 for 2 blocks of 16
    plaintext = b"DEADBEEFISSOGOODDEADBEEFISSOGOODDEADBEEFISSOGOODDEADBEEFISSOGOOD"  # or same 16 char must repeat
    unknown_crypto = encrypt_randomly(plaintext, random_aes_key())
    # print(unknown_crypto)
    # print(len(unknown_crypto))
    # print(detect_aes_cbc(unknown_crypto))

    count = 0
    for i in range(10000):
        unknown_crypto = encrypt_randomly(plaintext, random_aes_key())
        if detect_aes_ecb(unknown_crypto):
            count += 1
            print(True)
    print('count:', count)
    # print(detect_aes_mode(unknown_crypto))


def test_decrypt_ecb_byte_at_time():
    # Set 2, Challenge 12

    my_str = b'A'
    unknown_str = 'Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK'

    print(base64.b64decode(unknown_str))
    print(len(base64.b64decode(unknown_str)))

    random_key = random_aes_key()

    # detect block size
    # print('unknown_str', len(base64.b64decode(unknown_str)))
    low = len(aes_ecb_encrypt(base64.b64decode(unknown_str), random_key))
    detected_block_length = 0
    for i in range(50):
        ciphertext = aes_ecb_encrypt(my_str * i + base64.b64decode(unknown_str), random_key)
        # print(ciphertext)
        if len(ciphertext) > low:
            print(len(ciphertext) - low)
            detected_block_length = len(ciphertext) - low
            break
        # print(len(ciphertext))
    print('Detected block size:', detected_block_length)

    # detect ECB
    assert detect_aes_ecb(aes_ecb_encrypt(my_str * 40 + base64.b64decode(unknown_str), random_key))

    plaintext = b''

    for block in range((len(base64.b64decode(unknown_str)) // detected_block_length) + 1):
        for position in range(detected_block_length, 0, -1):
            short_block = b'A' * (position - 1)
            print('1. block:', block, 'short_block:', short_block, 'length:', len(short_block))
            known_crypt = b''

            # build lookup table for unknown last character
            lastchar_dict = {}
            for i in range(256):
                my_str = short_block + plaintext + chr(i).encode()
                # print('2. my_str', my_str)
                lastchar_dict[aes_ecb_encrypt(my_str, random_key)[
                              detected_block_length * block:detected_block_length * (block + 1)]] = chr(i)

            # print('3. lastchar_dict')
            # pprint(lastchar_dict)
            # print('length lastchar_dict:', len(lastchar_dict))

            # print('4. plaintext before oracle:', short_block + base64.b64decode(unknown_str), 'length:',
            #       len(short_block + base64.b64decode(unknown_str)))

            crypt_block = aes_ecb_encrypt(short_block + base64.b64decode(unknown_str), random_key)[
                          detected_block_length * block:detected_block_length * (block + 1)]
            print('5. crypt_block:', crypt_block, 'len(crypt_block):', len(crypt_block))

            # if last byte of block is \x01, padding may be in use
            if lastchar_dict[crypt_block] == '\x01':
                print('Possible padding detected by last character.')
                break
            try:
                print('6. char:', lastchar_dict[crypt_block], ord(lastchar_dict[crypt_block]), 'type:',
                      type(lastchar_dict[crypt_block]))
            except KeyError as ke:
                print('Possible padding detected by KeyError.')
                print(ke)
                break

            plaintext += lastchar_dict[crypt_block].encode()
            print('7. plaintext solved', plaintext, 'len(plaintext)', len(plaintext))

        print('8. plaintext:', plaintext)
    assert plaintext == b"Rollin' in my 5.0\nWith my rag-top down so my hair can blow\nThe girlies on standby waving just to say hi\nDid you stop? No, I just drove by\n"
    assert plaintext == base64.b64decode(unknown_str)


def test_ecb_cut_and_paste():
    # Set 2, Challenge 13
    c = parse_cookie('foo=bar&baz=qux&zap=zazzle')
    print(c)
    print(profile_format('foo@bar.com'))
    print(profile_format('foo@bar.com&role=admin'))
    print(encode_profile(profile_format('foo@bar.com')))

    key = random_aes_key()

    cipher = aes_ecb_encrypt(encode_profile(profile_format('foo@bar.com')), key)
    plain = parse_cookie(aes_ecb_decrypt(cipher, key).decode())
    print(plain)

    # make a role=admin profile
    attack = b'email=foo@bar.com&uid=10&role=admin'
    attack_cipher = aes_ecb_encrypt(attack, key)

    attack_cipher = attack_cipher[BLOCK_SIZE:]
    # print(attack_cipher, len(attack_cipher))

    attack_cipher = cipher[:BLOCK_SIZE] + attack_cipher
    print(aes_ecb_decrypt(attack_cipher, key))
