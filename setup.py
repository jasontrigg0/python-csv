from distutils.core import setup
setup(
    name = 'python-csv',
    packages = ['python-csv'],
    version = "0.0.1",
    description = 'Python tools for manipulating csv files',
    author = "Jason Trigg",
    author_email = "jasontrigg0@gmail.com",
    url = "https://github.com/jasontrigg0/python-csv",
    download_url = 'https://github.com/jasontrigg0/python-csv/tarball/0.0.1',
    scripts=[
        "python-csv/pcsv",
        "python-csv/pagg",
        "python-csv/pgraph",
        "python-csv/pjoin",
        "python-csv/plook",
        "python-csv/psort",
        "python-csv/pset",
        "python-csv/ptable",
        "python-csv/to_csv"
    ],
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "xlrd"
    ],
    keywords = [],
    classifiers = [],
)
