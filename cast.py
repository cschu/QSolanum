#!/usr/bin/python

import os
import sys
import math

def cast(obj):
    try:
        return float(obj)
    except:
        if obj is None:
            return obj
        else:
            return str(obj)

#
def cast_str(string):
    """ I hate Unicode. """
    try:
        return str(string)
    except:
        return cast_unicode(string)
    pass

umlaute = {u'\u00E4': 'ae',
           u'\u00C4': 'AE',
           u'\u00F6': 'oe',
           u'\u00D6': 'OE',           
           u'\u00FC': 'ue',
           u'\u00DC': 'UE',
           u'\u00DF': 'ss'}
#
def cast_unicode(string):    
    """ Maybe this is dilletantish, but I don't know better... yet! """
    try:
        ustr = unicode(string, 'utf-8')
        for k, v in umlaute.items():
            ustr = ustr.replace(k, v)
        return str(ustr)
    except:
        return 'UNICRAP'
    pass




###
def main(argv):
    return None

if __name__ == '__main__': main(sys.argv[1:])
