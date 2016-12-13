import re, os, getpath

def splitPath(string1='',string2=''):
    commonpath = getpath.commonprefix([string1,string2], '/')+'/'
    if commonpath == '/':
        rest1 = re.split( r'/', string1, 1)[1]
        rest2 = re.split( r'/', string2, 1)[1]
        return [commonpath, rest1, rest2]
    elif commonpath:
        re_commonpath = re.escape(commonpath)
        rest = re.split(re_commonpath, string1)
        rest1, rest2 = '', ''
        if len(rest) > 1:
            rest1 = rest[1]
        rest = re.split(re_commonpath, string2)
        if len(rest) > 1:
            rest2 = rest[1]
        return [commonpath, rest1, rest2]
    else:
        return ['','','']

def makeRelPath(string1='', string2=''):
    commonpath, rest1, rest2 = splitPath(string1, string2)
    if rest1 =='':
        return '../'
    if rest2 =='':
        return rest1 + '/'
    elif rest2:
        rel_path = ''
        for i in rest2.split('/'):
            rel_path = rel_path + '../'
        return rel_path + rest1+'/'


print os.path.isfile('./uuid4.py')