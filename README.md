**python-csv**

Python tools for manipulating csv files. Some parts (eg plook) inspired by the excellent csvkit (https://github.com/onyxfish/csvkit)
    
    
    

Brief summaries of various files:

---

**Data manipulation**

pcsv: remove or keep certain rows, remove or keep certain columns, adjust columns or create new columns from old (some similarity to awk)

pagg: run aggregations on the csv (somewhat like GROUP BY in SQL) 

pjoin: run a join on two csv files

psort: sort csv files by a column

to_csv: import xls files and json files to csv

---

**Data summaries + viewing**

plook: pretty print csv in less

pgraph: quick plotting of one and two dimensional numeric datasets in csv

ptable: show the frequencies of different values in a one-column csv

pset: union, and difference of two one-column csvs

pdiff: view differences between two csv files





More detailed summaries + examples

pcsv.py 