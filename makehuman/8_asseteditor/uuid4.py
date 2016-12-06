# Very (!) simple random uuid4 generator, to replace makecloethes uuid4.py
# License: public domain

import random

def get_charList():
    charList=[]
    for i in range(ord('a'), ord('f')+1):
        charList.append(chr(i))
    for i in range(0,10):
        charList.append(str(i))
    return charList

def uuid4():
    uuid_str=""
    charList = get_charList()
    random.seed()
    for i in range(36):
        if i in [8, 13, 18, 23]:
            uuid_str = uuid_str + '-'
        else:
            uuid_str = uuid_str + charList[random.randint(0,len(charList)-1)]
    return uuid_str