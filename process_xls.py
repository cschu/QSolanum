#!/usr/bin/python

import os
import sys
import math

import xlrd

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

""" Excel cell type decides which cast function to use. """
CAST_FUNC = {xlrd.XL_CELL_EMPTY: str,
             xlrd.XL_CELL_TEXT: cast_str,
             xlrd.XL_CELL_NUMBER: float,
             xlrd.XL_CELL_DATE: float,
             xlrd.XL_CELL_BOOLEAN: int,
             xlrd.XL_CELL_ERROR: int,
             xlrd.XL_CELL_BLANK: cast_str}

""" Parcelle information is stored on sheet 3, at least for Golm.xls. """
DEFAULT_PARCELLE_INDEX = 2
""" Treatment/Aliquot relations are stored on sheet 1. """
DEFAULT_TREATMENT_ALIQUOT_INDEX = 0


#
class DataObject(object):
    def __init__(self, headers=[], values=[]):
        for header, value in zip(headers, values):
            setattr(self, header, value)
        pass
    def __add__(self, other):
        res = DataObject(self.__dict__.keys(), self.__dict__.values())
        res.__dict__.update(other.__dict__)
        return res
    pass

# TODO: Sanity checks!
class StarchData(DataObject):
    starch_content_sanity_interval = [100, 300]
    pass

#
def read_xls_data(fn, sheet_index=0):
    data = []
    book = xlrd.open_workbook(fn)
    sheet = book.sheet_by_index(sheet_index)    
    col_headers = [str(cell.value).replace(' ', '_')
                   for cell in sheet.row(0)]
    for i in xrange(1, sheet.nrows):
        row = [CAST_FUNC[cell.ctype](cell.value) for cell in sheet.row(i)]
        data.append(DataObject(col_headers, row))
    return data, col_headers



if __name__ == '__main__': main(sys.argv[1:])
