from distutils.core import setup
setup(
    name = 'python-csv',
    packages = ['python_csv'],
    version = "0.0.3",
    description = 'Python tools for manipulating csv files',
    author = "Jason Trigg",
    author_email = "jasontrigg0@gmail.com",
    url = "https://github.com/jasontrigg0/python-csv",
    download_url = 'https://github.com/jasontrigg0/python-csv/tarball/0.0.3',
    scripts=[
        "python_csv/pcsv",
        "python_csv/pagg",
        "python_csv/pgraph",
        "python_csv/pjoin",
        "python_csv/plook",
        "python_csv/psort",
        "python_csv/pset",
        "python_csv/ptable",
        "python_csv/to_csv"
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
