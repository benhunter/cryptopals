def pkcs7pad(text, length):
    if len(text) > length:
        raise RuntimeError("Text for padding is longer than requested length.")
    if type(text) is not bytes:
        raise TypeError("Text must be bytes.")
    diff = length - len(text)
    padding = bytearray([diff for x in range(diff)])
    return text + padding


def test_pkcs7_padding():
    assert pkcs7pad(b"YELLOW SUBMARINE", 20) == b"YELLOW SUBMARINE\x04\x04\x04\x04"
