#!/usr/bin/env python
import sys
import optparse
import csv
import re
from utils import readcsv, is_int, str_is_float, str_is_int, md5hash
from pyindent import pyindent

def readCL():
    usagestr = "%prog"
    parser = optparse.OptionParser(usage=usagestr)
    parser.add_option("-f","--infile")
    parser.add_option("-c","--keep_list",help="csv of column names or indices. Can include currently non-existent columns")
    parser.add_option("-C","--drop_list",help="csv of column names or indices")
    parser.add_option("-b","--begin_code")
    parser.add_option("-g","--grep_code")
    parser.add_option("-p","--process_code")
    parser.add_option("-e","--end_code")
    parser.add_option("-d","--delimiter", default=",")
    parser.add_option("--exceptions_allowed", action="store_true")
    parser.add_option("-n","--no_header",action="store_true")
    parser.add_option("--fix", action="store_true")
    parser.add_option("--autofix",action="store_true")
    parser.add_option("--set", help="load a file with no header, storing each line as an element of a set")

    options, args = parser.parse_args()
    if not options.infile:
        f_in = sys.stdin
    else:
        f_in = open(options.infile)

    keep_list = process_cut_csv(options.keep_list)
    drop_list = process_cut_csv(options.drop_list)

    return f_in, keep_list, drop_list, options.begin_code, options.grep_code, options.process_code, options.end_code, options.exceptions_allowed, options.no_header, options.delimiter, options.fix, options.autofix, options.set


def process_cut_csv(i,delim=","):
    if i:
        i = i.split(',')
        return list(process_cut_list(i))
    else:
        return None

def process_cut_list(l, delim=","):
    for i in l:
        if "-" in i:
            x,y = i.split('-')
            for r in range(int(x),int(y)+1):
                yield r
        elif str_is_int(i):
            yield int(i)
        else:
            yield i


#dict_and_row function to return a tuple with both unprocessed row and csv.reader() output
#http://stackoverflow.com/questions/29971718/reading-both-raw-lines-and-dicionaries-from-csv-in-python
class FileWrapper:
  def __init__(self, f_in):
    self.f_in = f_in
    self.prev_line = None

  def __iter__(self):
    return self

  def next(self):
    self.prev_line = next(self.f_in).strip("\n\r")
    return self.prev_line

def csvlist_and_raw(f_in, delimiter):
    wrapper = FileWrapper(f_in)
    #default max field size of ~131k crashes at times
    csv.field_size_limit(sys.maxsize) 
    reader = csv.reader(wrapper, delimiter=delimiter)
    for csvlist in reader:
        yield wrapper.prev_line, csvlist



#fast-ish index dictionary:
#an ordered dictionary that can be accessed by string keys
#or index values
class IndexDict():
    def __init__(self, keyhash, values):
        self._keyhash = keyhash
        self._values = values
    def __setitem__(self, key, value):
        if is_int(key):
            #'key' is actually an index, 
            #must be an already existing item
            self._values[key] = value
        else:
            len_vals = len(self._values)
            index = self._keyhash.get(key,len_vals)
            if index >= len(self._values):
                self._keyhash[key] = len(self._values)
                self._values.append(value)
            else:
                self._values[index] = value
    def __getitem__(self, key):
        if isinstance(key, slice):
            return self._values.__getitem__(key)
        elif is_int(key):
            return self._values.__getitem__(key)
        elif key in self._keyhash:
            index = self._keyhash[key]
            return self._values.__getitem__(index)
        else:
            raise Exception("Couldn't find value {0} in IndexDict".format(key))
    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except:
            if default is not None:
                return default
            else:
                raise
    def __str__(self):
        return dict((k,self._values[v]) for k,v in self._keyhash.items() if v < len(self._values[v])).__str__()
    def __len__(self):
        return len(self._values)
    def keys(self):
        return self._keyhash.keys()
    def values(self):
        return self._values


def write_line(rout):
    if isinstance(rout, IndexDict):
        rout = rout.values()
    # sys.stdout.write(','.join(rout) + '\n')
    # csv.writer(sys.stdout, lineterminator= '\n').writerows([rout],quoting=csv.QUOTE_NONE)
    csv.writer(sys.stdout, lineterminator= '\n').writerows([rout])

def proc_field(f):
    try:
        int(f)
        return int(f)
    except:
        pass
    return f

def gen_grep_code(grep_code):
    if grep_code:
        grep_string = re.findall("^/(.*)/$",grep_code)
        if grep_string:
            grep_string = grep_string[0]
            grep_code = 're.findall("{grep_string}",",".join(l))'.format(**vars())
    return grep_code

def gen_outhdr(hdr, add_list, keep_list, drop_list):
    outhdr = hdr[:]
    if keep_list:
        if not add_list:
            add_list = [x for x in keep_list if x not in hdr and not is_int(x)]
        tmp_dict = dict(list(enumerate(outhdr)) + zip(outhdr,outhdr))
        outhdr = [tmp_dict[x] for x in keep_list if x not in add_list]
    if add_list:
        outhdr += [x for x in add_list if x not in outhdr]
    if drop_list:
        outhdr = [x for ix,x in enumerate(outhdr) if (ix not in drop_list and x not in drop_list)]
    return outhdr


# @profile
def process(f_in, keep_list, drop_list, begin_code, grep_code, process_code, end_code, exceptions_allowed, no_header, delimiter, fix, autofix, load_set):
    in_hdr = None
    out_hdr = None
    has_exceptions = False
    has_printed_incomplete_line = False
    # do_write = process_code and ("print" in process_code or "write_line" in process_code)
    if begin_code:
        begin_code = compile(begin_code,'','exec')
    if grep_code:
        grep_code = compile(grep_code,'','eval')
    if process_code:
        process_code = compile(process_code,'','exec')
    if end_code:
        end_code = compile(end_code,'','exec')
    if begin_code:
        exec(begin_code)

    if load_set:
        s = set(l.strip() for l in open(load_set))
        
    for i,(l,_csvlist) in enumerate(csvlist_and_raw(f_in, delimiter = delimiter)):
        is_header_line = (i==0 and not no_header)
        if no_header:
            #create a dummy header from the length of the line
            in_hdr = ["X"+str(j) for j,_ in enumerate(_csvlist)]
            hdrhash = dict((jx,j) for j,jx in enumerate(in_hdr))
            #jtrigg@20151120 out_hdr computed below
            # outhdr = in_hdr[:]
            # outhdr = gen_outhdr(in_hdr, add_list, keep_list, drop_list)
            r = IndexDict(hdrhash,_csvlist) #IndexDict can be accessed by string or index (all keys must be strings)
        elif not in_hdr:
            in_hdr = _csvlist[:]
            if len(in_hdr) != len(set(in_hdr)):
                sys.stderr.write("WARNING: duplicated header columns. Using dummy header instead" + '\n')
                #create a dummy header from the length of the line
                in_hdr = ["X"+str(j) for j,_ in enumerate(_csvlist)]
            hdrhash = dict((jx,j) for j,jx in enumerate(in_hdr))
            #jtrigg@20151120 out_hdr computed below
            # outhdr = in_hdr[:]
            # outhdr = gen_outhdr(in_hdr, add_list, keep_list, drop_list)
            #r on the first line is just a dictionary from in_hdr -> in_hdr
            continue
        else:
            #jtrigg@20150518: removing do_write variable
            # if len(_csvlist) != len(hdr) and not do_write and not has_printed_incomplete_line:
            if len(_csvlist) != len(in_hdr):
                if fix:
                    sys.stdout.write(l + "\n")
                    continue
                elif autofix:
                    continue
                elif not has_printed_incomplete_line:
                    raise Exception("ERROR: line length not equal to header length. Try running pcsv.py --fix or pcsv.py --autofix")
                    # sys.stderr.write("Header length " + str(len(hdr)) + "." + "  Row length " + str(len(_csvlist)) + "." + "\n")
                    # csv.writer(sys.stderr, lineterminator= '\n').writerows([_csvlist])
                    has_printed_incomplete_line = True
            if not _csvlist:
                _csvlist = [''] * len(in_hdr)
            r = IndexDict(hdrhash,_csvlist) #IndexDict can be accessed by string or index (all keys must be strings)


        try:
            if grep_code and not is_header_line and not eval(grep_code):
                continue

            #do_write on every line including header
            #otherwise skip the header
            # if do_write or (process_code and not is_header_line):
            if (process_code and not is_header_line):
                exec(process_code)
        except:
            if not exceptions_allowed:
                raise
            else:
                if not has_exceptions:
                    sys.stderr.write("WARNING: exception" + '\n')
                    has_exceptions = True
                continue

        #jtrigg@20150518: phasing out do_write
        # if not do_write:
        #     rout = [str(r.get(h,"")) for h in outhdr]
        #     write_line(rout)

        if (fix and i>0):
            pass
        elif not out_hdr:
            #set and print header
            add_list = [k for k in r.keys() if k not in in_hdr] #add any keys from r that aren't in the in_hdr
            out_hdr = gen_outhdr(in_hdr, add_list, keep_list, drop_list)
            csv.writer(sys.stdout, lineterminator= '\n').writerows([out_hdr])
        else:
            #print regular line
            # rout = [str(r.get(h,"")) for h in outhdr]
            rout = [str(r[h]) for h in out_hdr]
            write_line(rout)
    if end_code:
        exec(end_code)


if __name__ == "__main__":
    f_in, keep_list, drop_list, begin_code, grep_code, process_code, end_code, exceptions_allowed, no_header, delimiter, fix, autofix, load_set = readCL()
    #following two lines solve 'Broken pipe' error when piping
    #script output into head
    from signal import signal, SIGPIPE, SIG_DFL
    signal(SIGPIPE,SIG_DFL)

    if begin_code:
        begin_code = pyindent(begin_code)
    if grep_code:
        grep_code = pyindent(grep_code)
    if process_code:
        process_code = pyindent(process_code)
    #preprocess /.*/ syntax
    grep_code = gen_grep_code(grep_code)

    process(f_in,keep_list,drop_list,begin_code,grep_code,process_code,end_code,exceptions_allowed,no_header,delimiter,fix,autofix,load_set)
