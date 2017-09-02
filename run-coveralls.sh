#! /bin/bash

.env/bin/activate

export PATH=`pwd`/.env/local/bin:$PATH

PIP="${PY_EXE} $(which pip)"

$PIP install coveralls

coverage run --source=. manage.py test test/
