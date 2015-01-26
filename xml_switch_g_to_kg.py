#!/usr/bin/env python
'''
Created on Mar 11, 2014

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import re

P_value=re.compile(u'(?P<open><VALUE.*?>)(?P<no>[0-9]*\.[0-9]*)(?P<close>\</VALUE\>)')
P_attr=re.compile(u'<open><ATTRIBUTE ID="55"')
P_header=re.compile(u'<\?xml.*encoding="UTF-16".*\?>')


"""
<ATTRIBUTE ID="55" NAME_E="absolute freshweight" NAME_D="absolutes Frischgewicht" ORDER_NUMBER="0">
        <VALUE NAME_E="g" NAME_D="g FW">60.5</VALUE>

<ATTRIBUTE ID="188" NAME_E="absolute freshweight" NAME_D="absolutes Frischgewicht" ORDER_NUMBER="0">
        <VALUE NAME_E="kg" NAME_D="kg">0.184</VALUE>

<?xml version="1.0" encoding="UTF-16" standalone="yes"?>
"""



def main(argv):

    # DOS2UNIX before using this!
    
    out = open(argv[0].replace('.xml', '.ok.xml'), 'wb')
    for line in open(argv[0], 'rb'):
        hit_value = P_value.search(line)
        if hit_value:  
            # print 'HIT:', line, argv[0]
            newline = ' ' * 8 + hit_value.group('open') + '%.3f' % (float(hit_value.group('no')) / 1000.0) + hit_value.group('close')
            line = newline + '\n'
            line = line.replace('"g FW"', '"g"').replace('"g"', '"kg"')
        else:
            hit_attr = P_attr.search(line)
            if hit_attr:
                line = line.replace('"55"', '"188"')
            else:
                hit_header = P_header.search(line)
                if hit_header:
                    line = line.replace('"UTF-16"', '"UTF-8"')
                    

        out.write(line)
    out.close()

    
    out = open(argv[0].replace('.xml', '.ok.csv'), 'wb')
    for line in open(argv[0].replace('.xml', '.csv'), 'rb'):
        if not line.startswith(';;;') and line[0].isdigit():
            offset = -2
            if not line.strip().endswith(';'):
                line = line[:-1] + ';' + line[-1]
            line = line.split(';')
            line = ';'.join(line[:offset] + ['%.3f' % (float(line[offset]) / 1000.0)] + [line[offset + 1]])
        elif line.startswith('Probennummer'):
            line = line.replace(';g', ';kg')
            pass
        out.write(line)
    out.close()




    pass
    



if __name__ == '__main__': main(sys.argv[1:])
