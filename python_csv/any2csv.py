#!/usr/bin/env python
import python_csv.utils
import xlrd

###
def any2csv(txt, xls_sheet=None, xls_sheet_names=None, path=[], to_stdout=False):
    try:
        xls2csv(txt, xls_sheet, xls_sheet_names, to_stdout)
    except xlrd.biffh.XLRDError:
        pass

    try:
        json2csv(txt, path, to_stdout)
    except ValueError:
        pass

    try:
        xml2csv(txt, path, to_stdout)
    except xml.parsers.expat.ExpatError:
        pass
    
    raise Exception("ERROR: File doesn't match xls, json or xml format!" + "\n")


def xls2csv(txt, xls_sheet, xls_sheet_names, to_stdout=False):
    rows = read_xls(txt, xls_sheet, xls_sheet_names)
    return process_rows(rows, to_stdout)

def json2csv(txt, path, to_stdout=False):
    rows = read_json(txt, path)
    return process_rows(rows, to_stdout)

def xml2csv(txt, path, to_stdout=False):
    rows = read_xml(txt, path)
    return process_rows(rows, to_stdout)

def rows2csv(rows):
    """http://stackoverflow.com/a/9157370"""
    import io
    import csv
    output = io.BytesIO()
    wr = csv.writer(output)
    for r in rows:
        wr.writerow([s.encode("utf-8") for s in r if s])
    return output.getvalue().strip()

def csv2df(txt):
    pass

def df2csv(df):
    pass

# def csv2dict(txt):
#     pass

def csv2pretty(txt):
    from python_csv.plook import _csv2pretty
    return _csv2pretty(txt)





def print_csv(rows):
    wr = csv.writer(sys.stdout, lineterminator="\n")
    for r in rows:
        wr.writerow([s.encode("utf-8") for s in r if s])


def process_rows(rows, to_stdout):
    if to_stdout:
        print_csv(rows)
        sys.exit()
    else:
        return rows2csv(rows)
###    

def parse_cell(cell, datemode):
    if cell.ctype == xlrd.XL_CELL_DATE:
        dt = xlrd.xldate.xldate_as_datetime(cell.value, datemode)
        return dt.strftime("%Y-%m-%d")
    elif cell.ctype == xlrd.XL_CELL_NUMBER and int(cell.ctype) == cell.ctype:
        return int(cell.value)
    else:
        return cell.value.encode("utf-8")

    
def read_xls(txt, sheet, print_sheet_names):
    #when a filename is passed, I think xlrd reads from it twice, which breaks on /dev/stdin
    #so try passing file_contents instead of filename
    wb = xlrd.open_workbook(file_contents = txt) 

    sheet_names = wb.sheet_names()
    if print_sheet_names:
        sys.stdout.write(str(sheet_names) + "\n")
        sys.exit()

    if sheet in sheet_names:
        sh = wb.sheet_by_name(sheet)
    elif python_csv.utils.str_is_int(sheet) and int(sheet) < len(sheet_names):
        sh = wb.sheet_by_index(int(sheet))
    else:
        raise Exception("-s argument not in xls list of sheets ({})".format(str(sheet_names)))

    wr = csv.writer(sys.stdout, lineterminator="\n")
    for i in xrange(sh.nrows):
        r = [parse_cell(sh.cell(i,j), wb.datemode) for j in xrange(sh.ncols)]
        wr.writerow(r)

def read_json(txt, json_path):
    if not isinstance(json_path, list):
        t = json_path
        raise Exception("read_json function argument json_path requires a list, received '{json_path}', type {t}".format(**vars()))
    import json
    dict_list_obj = json.loads(txt)
    for r in process_dict_list_obj(dict_list_obj, json_path):
        yield r


def read_xml(txt, xml_path):
    if not isinstance(xml_path, list):
        t = type(xml_path)
        raise Exception("read_xml function argument xml_path requires a list, received '{xml_path}', type: {t}".format(**vars()))
    import xmltodict
    dict_list_obj = xmltodict.parse(txt)
    for r in process_dict_list_obj(dict_list_obj, xml_path):
        yield r


def process_dict_list_obj(dict_list_obj, path):
    """json-style nested objects consisting of 
    a (dictionary OR list) of (dictionary OR list) of (dictionary OR list) etc
    """
    dict_list_obj = follow_path(dict_list_obj, path)
    if isinstance(dict_list_obj, list):
        cols = set()
        for i in dict_list_obj:
            cols = cols.union(i.viewkeys())
        cols = list(cols)
        # print "here: ", cols
        yield cols
        for i in dict_list_obj:
            r = [unicode(i.get(c,"")) for c in cols]
            yield r
    else:
        cols = list(dict_list_obj.viewkeys())
        yield cols
        r = [unicode(dict_list_obj.get(c,"")) for c in cols]
        yield r


def follow_path(dict_list_obj, path):
    if path == []:
        return dict_list_obj

    if isinstance(dict_list_obj, list):
        if python_csv.utils.str_is_int(path[0]):
            index = int(path[0])
            return follow_path(dict_list_obj[index],path[1:])
        else:
            raise
    elif isinstance(dict_list_obj, dict):
        if path[0] in dict_list_obj:
            key = path[0]
            return follow_path(dict_list_obj[key],path[1:])
        elif python_csv.utils.str_is_int(path[0]):
            index = int(path[0])
            return follow_path(dict_list_obj.values()[index],path[1:])
        else:
            raise
    else:
        raise
