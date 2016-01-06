#!/usr/bin/env python
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
    elif python_csv.utils.str_is_int(sheet) and int(sheet) < len(sheet_names):
        sh = wb.sheet_by_index(int(sheet))
    else:
        raise Exception("-s argument not in xls list of sheets ({})".format(str(sheet_names)))

    wr = csv.writer(sys.stdout, lineterminator="\n")
    for i in xrange(sh.nrows):
        r = [parse_cell(sh.cell(i,j), wb.datemode) for j in xrange(sh.ncols)]
        wr.writerow(r)

def read_json(txt, json_path):
    import json
    dict_list_obj = json.loads(txt)
    for l in process_dict_list_obj(dict_list_obj, json_path):
        yield l


def read_xml(txt, xml_path):
    import xmltodict
    dict_list_obj = xmltodict.parse(txt)
    for l in process_dict_list_obj(dict_list_obj, xml_path):
        yield l
        
def process_dict_list_obj(dict_list_obj, path):
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
