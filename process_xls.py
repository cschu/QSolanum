#!/usr/bin/python

import os
import sys
import math

import xlrd

import data_objects as DO 
import cast


""" Excel cell type decides which cast function to use. """
CAST_FUNC = {xlrd.XL_CELL_EMPTY: str,
             xlrd.XL_CELL_TEXT: cast.cast_str,
             xlrd.XL_CELL_NUMBER: float,
             xlrd.XL_CELL_DATE: cast.cast_str,
             xlrd.XL_CELL_BOOLEAN: int,
             xlrd.XL_CELL_ERROR: int,
             xlrd.XL_CELL_BLANK: cast.cast_str}

""" Parcelle information is stored on sheet 3, at least for Golm.xls. """
DEFAULT_PARCELLE_INDEX = 2
""" Treatment/Aliquot relations are stored on sheet 1. """
DEFAULT_TREATMENT_ALIQUOT_INDEX = 0





#
def read_xls_data(fn, sheet_index=0):
    data = []
    book = xlrd.open_workbook(fn)
    sheet = book.sheet_by_index(sheet_index)    
    col_headers = [str(cell.value).replace(' ', '_')
                   for cell in sheet.row(0)]
    for i in xrange(1, sheet.nrows):
        row = []
        for cell in sheet.row(i):
            if cell.ctype == xlrd.XL_CELL_DATE:
                # print 'DATE', cell.value
                # print xlrd.xldate_as_tuple(cell.value, book.datemode)
                cell_date = xlrd.xldate_as_tuple(cell.value, book.datemode)
                row.append('%4i-%02i-%02i' % cell_date[:3])
            else:
                row.append(CAST_FUNC[cell.ctype](cell.value))
        # row = [CAST_FUNC[cell.ctype](cell.value) for cell in sheet.row(i)]
        data.append(DO.DataObject(col_headers, row))
        # print data[-1].__dict__
    return data, col_headers



if __name__ == '__main__': main(sys.argv[1:])
