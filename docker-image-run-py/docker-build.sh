#! /bin/sh
cp ../course/page/code_feedback.py ../course/page/code_runpy_backend.py .
docker build -t "dzhuang/learning-what-runpy-i386" .
rm code_feedback.py code_runpy_backend.py

