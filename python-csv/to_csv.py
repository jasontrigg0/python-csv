#!/usr/bin/env python
import xlrd
import csv
import argparse
import sys
import utils

def readCL():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--xls_sheet", default="0", help="either sheet number or sheet name")
    parser.add_argument("--xls_sheet_names",action="store_true",help="print list of sheet names")
    parser.add_argument("--json_path", help="comma separated path string. Example: 0,2,1")
    parser.add_argument("infile",default=sys.stdin, nargs="?", type=argparse.FileType('r'))
    args = parser.parse_args()
    if not args.json_path:
        args.json_path = []
    else:
        args.json_path = args.json_path.split(",")
    return args.infile, args.xls_sheet, args.xls_sheet_names, args.json_path


def parse_cell(cell, datemode):
    if cell.ctype == xlrd.XL_CELL_DATE:
        dt = xlrd.xldate.xldate_as_datetime(cell.value, datemode)
        return dt.strftime("%Y-%m-%d")
    elif cell.ctype == xlrd.XL_CELL_NUMBER and int(cell.ctype) == cell.ctype:
        return int(cell.value)
    else:
        return cell.value.encode("utf-8")

    
def read_xls(txt):
    #when a filename is passed, I think xlrd reads from it twice, which breaks on /dev/stdin
    #so try passing file_contents instead of filename
    wb = xlrd.open_workbook(file_contents = txt) 

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

        
def read_json(txt, json_path):
    import json
    json_obj = json.loads(txt)
    # print json_obj
    json_obj = follow_json_path(json_obj, json_path)
    # print json_obj
    # print type(json_obj)
    if isinstance(json_obj, list):
        cols = set()
        for i in json_obj:
            cols = cols.union(i.viewkeys())
        cols = list(cols)
        # print "here: ", cols
        yield cols
        for i in json_obj:
            r = [i.get(c,"") for c in cols]
            yield r
    else:
        cols = list(json_obj.viewkeys())
        yield cols
        r = [json_obj.get(c,"") for c in cols]
        yield r


        
def follow_json_path(json_obj, path):
    if path == []:
        return json_obj

    if isinstance(json_obj, list):
        if utils.str_is_int(path[0]):
            index = int(path[0])
            return follow_json_path(json_obj[index],path[1:])
        else:
            raise
    elif isinstance(json_obj, dict):
        if path[0] in json_obj:
            key = path[0]
            return follow_json_path(json_obj[key],path[1:])
        elif utils.str_is_int(path[0]):
            index = int(path[0])
            return follow_json_path(json_obj.values()[index],path[1:])
        else:
            raise
    else:
        raise
                
                    
    
def write_csv(rows):
    wr = csv.writer(sys.stdout, lineterminator="\n")
    for r in rows:
        wr.writerow(r)


if __name__ == "__main__":
    infile, xls_sheet, xls_sheet_names, json_path = readCL()

    txt = infile.read()
    
    try:
        rows = read_xls(txt)
        write_csv(rows)
        sys.exit()
    except xlrd.biffh.XLRDError:
        pass

    try:
        rows = read_json(txt, json_path)
        write_csv(rows)
        sys.exit()
    except ValueError:
        pass


    raise Exception("ERROR: File doesn't match xls or json format!" + "\n")
