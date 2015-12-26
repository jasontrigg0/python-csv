from distutils.core import setup
setup(
    name = 'python-csv',
    packages = ['python-csv'],
    version = "0.0.0",
    description = 'Python tools for manipulating csv files',
    author = "Jason Trigg",
    author_email = "jasontrigg0@gmail.com",
    url = "https://github.com/jasontrigg0/python-csv",
    download_url = 'https://github.com/jasontrigg0/python-csv/tarball/0.0.0',
    scripts=[
        "python-csv/pcsv.py",
        "python-csv/pcagg.py",
        "python-csv/pcgraph.py",
        "python-csv/pcjoin.py",
        "python-csv/pclook.py",
        "python-csv/pcsort.sh",
        "python-csv/pcset.py",
        "python-csv/pctable.py",
        "python-csv/to_csv.py"
    ],
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib"
    ],
    keywords = [],
    classifiers = [],
)
