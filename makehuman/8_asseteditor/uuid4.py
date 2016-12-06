# Very (!) simple random uuid4 generator, to replace makeclothes uuid4.py
# using the uuid format XXXXXXXX-XXXX-4XXX-YXXX-XXXXXXXXXXXX, with a random hex digit for X and a random digit of "8,9,a,b" for Y
# see https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_.28random.29
#
#
# License: Public Domain



import random

def get_charList():
    charList=[]
    for i in range(0,10):
        charList.append(str(i))
    for i in range(ord('a'), ord('f')+1):
        charList.append(chr(i))
    return charList

def uuid4():
    uuid_str=list("XXXXXXXX-XXXX-4XXX-YXXX-XXXXXXXXXXXX")
    charList = get_charList()
    x_charList = ['8','9','a','b']
    random.seed()
    for i in range(36):
        c = uuid_str[i]
        if c == 'X':
            uuid_str[i] = charList[random.randint(0, len(charList) - 1)]
        if c == 'Y':
            uuid_str[i] = x_charList[random.randint(0, len(x_charList) - 1)]
    return str().join(uuid_str)