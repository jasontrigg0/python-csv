#!/usr/bin/env python
import xlrd
import csv
import argparse
import sys
import utils

def readCL():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--sheet", default="0", help="either sheet number or sheet name")
    parser.add_argument("--sheet_names",action="store_true",help="print list of sheet names")
    parser.add_argument("infile",default=sys.stdin)
    args = parser.parse_args()
    return args.infile, args.sheet, args.sheet_names


def parse_cell(cell, datemode):
    if cell.ctype == xlrd.XL_CELL_DATE:
        dt = xlrd.xldate.xldate_as_datetime(cell.value, datemode)
        return dt.strftime("%Y-%m-%d")
    elif cell.ctype == xlrd.XL_CELL_NUMBER and int(cell.ctype) == cell.ctype:
        return int(cell.value)
    else:
        return cell.value.encode("utf-8")
    

if __name__ == "__main__":
    infile, sheet, print_sheet_names = readCL()

    #I think xlrd reads from the filename twice, which breaks on /dev/stdin
    #So try passing file_contents instead of filename
    wb = xlrd.open_workbook(file_contents = open(infile).read()) 

    sheet_names = wb.sheet_names()
    if print_sheet_names:
        sys.stdout.write(str(sheet_names) + "\n")
        sys.exit()

    if sheet in sheet_names:
        sh = wb.sheet_by_name(sheet)
    elif utils.str_is_int(sheet) and int(sheet) < len(sheet_names):
        sh = wb.sheet_by_index(int(sheet))
    else:
        raise Exception("-s argument not in xls list of sheets ({})".format(str(sheet_names)))

    wr = csv.writer(sys.stdout, lineterminator="\n")
    for i in xrange(sh.nrows):
        r = [parse_cell(sh.cell(i,j), wb.datemode) for j in xrange(sh.ncols)]
        wr.writerow(r)
