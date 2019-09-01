#!/bin/bash
echo "Checking rst files in 'docs'" && \
find docs -name "*.rst" -exec rst2html.py --exit-status=2 {} \; > /dev/null && \
echo "Checking rst files in '.'" && \
find . -maxdepth 1 -name "*.rst" -exec rst2html.py -q --exit-status=2 {} \; > /dev/null && \
echo "Checking 'setup.py'" && \
python setup.py check --strict --restructuredtext --metadata && \
echo "Checking code style" && \
yapf -dr --style=facebook setup.py promptr
