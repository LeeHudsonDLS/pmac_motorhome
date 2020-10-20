============
Installation
============

TODO - this needs fleshing out once we have github and pypi deployments

Prerequisites
-------------
- Python 3.7 or greater
- pipenv

Steps to install for development
--------------------------------
- checkout from source control

  - clone git@gitlab.diamond.ac.uk:controls/python3/dls_motorhome.git
- cd to source root
- pipenv install --dev
- run tests

  - pipenv run pytest
- build an example PLC to /tmp/PLC12_SLITS1_HM.pmc

  - pipenv run python docs/tutorials/example.py
- generate documentation in <root>/build/html

  - pipenv run docs
