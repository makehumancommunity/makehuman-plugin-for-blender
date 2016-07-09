#!/usr/bin/python

import sys
from mhrc.JsonCall import JsonCall

def usage():
    print "USAGE:\n"
    print "  applyModifier.py <modifier name> <power>\n";
    print "Modifier name is the name as listed by the listAvailableModifiers"
    print "script. Power is either (usually) between 0.0 and +1.0, but some"
    print "modifiers may accept a range between -1.0 and +1.0."
    sys.exit(1)

if len(sys.argv) < 3:
    usage()

if len(sys.argv) > 3:
    usage()

modname = sys.argv[1]
modval = sys.argv[2]

jsc = JsonCall()

jsc.setFunction("applyModifier")
jsc.setParam("modifier",modname);
jsc.setParam("power",modval);

response = jsc.send()

if not response:
    print "Command failed (returned null response)\n"
    sys.exit(1)

if hasattr(response,"error") and getattr(response,"error"):
    print "ERROR: " + getattr(response,"error")
    sys.exit(1)

print "OK"



