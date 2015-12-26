#!/usr/bin/env python
import argparse
import codecs
import csv
import sys
import itertools
import os
import utils
import StringIO

# input: csv file
# output: excel-style pretty printing of that csv

def readCL():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile",default=sys.stdin,nargs="?")
    parser.add_argument("-n","--no_header",action="store_true")
    parser.add_argument("-c","--cache_freq",default="100")
    parser.add_argument("-t","--trim_wide_fields",action="store_true")
    parser.add_argument("-d","--delimiter", default=",")
    parser.add_argument("-s","--max_field_size",help="maximum field size (truncated + ellipses added)", type=int)
    args = parser.parse_args()

    if args.infile == sys.stdin:
        f_in = sys.stdin
    else:
        f_in = open(args.infile)

    return f_in, args.cache_freq, args.trim_wide_fields, args.no_header, args.delimiter, args.max_field_size
    

def width(string, max_field_size):
    """
    compute the length of the string as printed by less
    which can be complicated for unicode characters

    chinese characters are twice the normal width
    http://stackoverflow.com/questions/2476953/python-utf-8-howto-align-printout
    """
    #invalid unicode characters are usually printed like '<E6>'
    #ie they take up *four characters*
    #replace them with four spaces to calculate width correctly
    codecs.register_error('four_space',lambda x: (u"    ",x.start+1)) 
    string = preprocess_field(string, max_field_size)
    string = string.decode("utf8", "four_space")


    #some unicode characters are printed like <U+052A>
    #ie they take up *eight characters*
    #replace them with eight spaces
    bad_unicode = u'\u052a' + u'\u0377' + u'\u037f' + u'\ufeff'
    string = "".join([u" "*8 if (c in bad_unicode) else c for c in string])


    #early ascii characters are printed like ^W
    #ie take up *two characters*
    #replace them with two spaces
    early_unicode = [chr(i) for i in range(0,9)] + \
                    [chr(11) + chr(12)] + \
                    [chr(i) for i in range(14,27)] + \
                    [chr(i) for i in range(28,32)]
    string = "".join([u" "*2 if (c in early_unicode) else c for c in string])


    #chinese characters take up double the width of normal characters
    import unicodedata
    return sum(1 + (unicodedata.east_asian_width(c) in "WF") for c in string)

def spacing_line(widths):
    """
    special string printed three times:
    before hdr, between hdr and first row, and after last row
    """
    return '|-' + '+'.join(['-'*(w+2) for w in widths]) + '-|' + "\n"

def preprocess_field(field, max_field_size):
    field = field.replace("\t"," "*4)
    field = field.replace("\n","")
    field = field.replace("\r","")
    if max_field_size and len(field) > max_field_size:
        field = field[:(max_field_size - 3)] + "..."
    return field

def pretty_print_field(full_width, field, max_field_size):
    """
    pad the field string to have len full_width
    "fieldvalue" --> " fieldvalue     "
    """
    field = preprocess_field(field, max_field_size)
    extra_spaces = full_width - width(field, max_field_size)
    return " " + field + " "*extra_spaces + " "
    
def pretty_print_row(col_full_widths, row, max_field_size):
    """
    pretty print a row such that each column is padded to have the widths in the col_full_widths vector
    """
    start = "| "
    if len(row) == len(col_full_widths):
        end = " |"
    else:
        end = "|"
    return start + "|".join(pretty_print_field(full_width, field, max_field_size) for full_width, field in zip(col_full_widths, row)) + end + "\n"

    
def compute_full_widths(hdr, cached_lines, max_field_size):
    """
    input a hdr and a list of rows and compute the maximum printed width of each column
    """
    full_widths = []
    for l in (cached_lines + [hdr]):
        if not l: continue #skip hdr if empty
        l_widths = [width(f, max_field_size) for f in l]
        if not full_widths:
            full_widths = l_widths
        else:
            full_widths = [max(x1,x2) for x1,x2 in itertools.izip_longest(full_widths, l_widths)]
    return full_widths


def update_full_widths(full_widths, r, max_field_size):
    """
    input a list of maximum column widths and update that list given a new row
    """
    l_widths = [width(f, max_field_size) for f in r]
    full_widths_new = [max(x1,x2) for x1,x2 in itertools.izip_longest(full_widths, l_widths)]
    return full_widths_new
    

def print_cache(full_widths, hdr, cached_lines, max_field_size):
    if hdr:
        yield spacing_line(full_widths)
        yield pretty_print_row(full_widths, hdr, max_field_size)
    yield spacing_line(full_widths)
    for r in cached_lines:
        yield pretty_print_row(full_widths, r, max_field_size)

def pretty_print_csv(s):
    f_in = StringIO.StringIO(s)
    return "".join(get_all_lines(f_in, 100, False, False, ","))


def get_all_lines(f_in, cache_freq, trim_wide_fields, no_header, delimiter, max_field_size):
    cache_freq = int(cache_freq)
    hdr = None
    cached_lines = []
    full_widths = None
    #default max field size of ~131k crashes at times
    csv.field_size_limit(sys.maxsize)
    for i,r in enumerate(csv.reader(f_in, delimiter=delimiter)):
        if trim_wide_fields:
            r = [f[:100] for f in r]
        if not hdr and not no_header:
            hdr = r
        elif i <= cache_freq:
            #cache first few lines
            cached_lines.append(r)
        else:
            #print cached lines all at once
            if not full_widths:
                full_widths = compute_full_widths(hdr, cached_lines, max_field_size)
                full_widths_new = full_widths
                for l in print_cache(full_widths, hdr, cached_lines, max_field_size):
                    yield l
            #continue updating full_widths with each row
            full_widths_new = update_full_widths(full_widths_new, r)
            if i % cache_freq == 0:
                full_widths = full_widths_new
            #print current row
            yield (pretty_print_row(full_widths,r,max_field_size))

        
    #if we never printed the cache above
    if not full_widths:
        full_widths = compute_full_widths(hdr, cached_lines, max_field_size)
        full_widths_new = full_widths
        for l in print_cache(full_widths, hdr, cached_lines, max_field_size):
            yield l
    yield spacing_line(full_widths_new)



if __name__ == "__main__":
    f_in, cache_freq, trim_wide_fields, no_header, delimiter, max_field_size  = readCL()

    lesspager = utils.LessPager()

    
    for l in get_all_lines(f_in, cache_freq, trim_wide_fields, no_header, delimiter, max_field_size):
        lesspager.write(l)
    
