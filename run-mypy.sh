#! /bin/bash

mypy \
  --fast-parser \
  --strict-optional \
  --ignore-missing-imports \
  --follow-imports=skip \
  --disallow-untyped-calls \
  relate course image_upload
  # --disallow-untyped-defs \
