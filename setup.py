from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pbi-admin',
    version='0.0.1',

    description='pbi.io - CLI admin tools',
    long_description=long_description,

    url='https://github.com/palmbeach-interactive/pbi-admin',
    author='Jonas Ohrstrom',
    author_email='jonas@pbi.io',
    license='GPLv3',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='Palmbeach Interactive - Internal project handling tool',
    packages=find_packages(exclude=[
        'contrib',
        'docs',
        'tests'
    ]),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #  py_modules=["pbi_admin"],

    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'Fabric>=1.10.1,<1.20',
        'configobj',
        'netifaces',
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest<0.30'],
        'test': ['coverage', 'docutils'],
    },

    entry_points={
        'console_scripts': [
            'pbi_vm=pbi_admin:vm',
        ],
    },
)
