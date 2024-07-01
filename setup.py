import sys
from setuptools import setup

if sys.version_info < (3, 0):
    sys.exit('Sorry, Python lower than 3.0 is not supported')

setup(
    name = "generic-templates",
    version = "0.4.1",
    author = "Kevin Smathers",
    author_email = "kevin@ank.com",
    description = ("Python library for preprocessor expansion of template files to configured source code"),
    license = " ",
    keywords = " ",
    url = "https://github.com/ksmathers/generic-templates",
    packages = ['generic_templates'],
    classifiers = [],
    scripts= ['bin/fill-template'],
    tests_require = ['pytest'],
    install_requires = [
       'keyring',
       'lark'
    ]
)
