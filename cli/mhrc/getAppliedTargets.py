#!/usr/bin/python

import sys
from mhrc.JsonCall import JsonCall

jsc = JsonCall()
jsc.setFunction("getAppliedTargets")
response = jsc.send()

if not response:
    print "Command failed (returned null response)\n"
    sys.exit(1)

if hasattr(response,"error") and getattr(response,"error"):
    print "ERROR: " + getattr(response,"error")
    sys.exit(1)

data = response.getData()

for name in data.keys():
    print name + " " + str(data[name])


