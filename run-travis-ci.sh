#! /bin/bash

# before_script
if [[ $Flake8 == true ]]; then
  curl -L -O -k https://gitlab.tiker.net/inducer/ci-support/raw/master/prepare-and-run-flake8.sh
fi

if [[ $Mypy == true ]]; then
  curl -L -O -k https://gitlab.tiker.net/inducer/ci-support/raw/master/prepare-and-run-mypy.sh
  cp local_settings.example.py local_settings.py
fi

# run ci according to env variables
if [[ $PY == true ]]; then
  . ./run-tests-for-ci.sh
elif [[ $Mypy == true ]]; then
  . ./prepare-and-run-mypy.sh;
elif [[ $Flake8 == true ]]; then
  . ./prepare-and-run-flake8.sh relate course accounts test bin
fi