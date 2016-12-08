# Very (!) simple random uuid4 generator, to replace makeclothes uuid4.py
# using the uuid format XXXXXXXX-XXXX-4XXX-YXXX-XXXXXXXXXXXX, with a random hex digit for X and a random digit of "8,9,a,b" for Y
# see https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_.28random.29
#
#
# License: Public Domain

import random

def uuid4():
    uuid_str=list('XXXXXXXX-XXXX-4XXX-YXXX-XXXXXXXXXXXX')
    hex_str= list('0123456789abcdef')
    random.seed()
    for i in range(36):
        if uuid_str[i] == 'X':
            uuid_str[i] = hex_str[random.randint(0, 15)]
        elif uuid_str[i] == 'Y':
            uuid_str[i] = hex_str[random.randint(8,11)]
    return str().join(uuid_str)

for i in range(30):
    print uuid4()