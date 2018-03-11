from itertools import zip_longest

one = b"abcdefghijklmnop"
two = b"1234567890"

zipped_list_of_tuples = zip_longest(one, two)
print(zipped_list_of_tuples)
print(list(zipped_list_of_tuples))
# print(list(zip(*zip(one, two))))  # unzips
# print(bytes(list(zip(*zip(one, two)))))

zipped_list_of_tuples = zip_longest(one, two)
b = bytearray()
for x in zipped_list_of_tuples:
    # print(x)
    for y in x:
        # print(y)
        if y:
            b.append(y)
print(b)

one = b"abcdefghijklmnop"
two = b"1234567890"
three = b"ABCDEFGHIJKL"

zipped_list_of_tuples = zip_longest(one, two, three)
b = bytearray()
for x in zipped_list_of_tuples:
    print(x)
    for y in x:
        print(y)
        if y:
            b.append(y)
print(b)

one = b"abcdefghijklmnop"
two = b"1234567890"
three = b"ABCDEFGHIJKL"

zipped_list_of_tuples = zip_longest(one, two, three)
b = bytearray()
for x in zipped_list_of_tuples:
    print(x)
    for y in x:
        print(y)
        if y:
            b.append(y)
print(b)
