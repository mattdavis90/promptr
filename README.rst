promptr |Version| |Build| |Coverage| |Health| |Docs| |CLA|
==========================================================

|Compatibility| |Implementations| |Format| |Downloads|

promptr is a toolkit for building CLI shells, similar to that found on a Cisco router.

The library uses a click and flask style decorator driven interface that allows you to quickly and easily build a shell.

Documentation
-------------
promptr's documentation can be found at `https://promptr.readthedocs.io <https://promptr.readthedocs.io>`_


Installing promptr
------------------
promptr can be installed from Pypi using pip::

    pip install promptr

Thanks
------

Thanks to prompt-toolkit for the underlying functionality, and the thanks to pallets for the click and flask inspiration.

Contributing
------------
To contribute to promptr, please make sure that any new features or changes
to existing functionality **include test coverage**.

*Pull requests that add or change code without coverage will most likely be rejected.*

Additionally, please format your code using `yapf <http://pypi.python.org/pypi/yapf>`_
with ``facebook`` style prior to issuing your pull request.

``yapf --style=facebook -i -r promptr setup.py``


.. |Build| image:: https://travis-ci.org/mattdavis90/promptr.svg?branch=master
   :target: https://travis-ci.org/mattdavis90/promptr
.. |Coverage| image:: https://img.shields.io/coveralls/mattdavis90/promptr.svg
   :target: https://coveralls.io/r/mattdavis90/promptr
.. |Health| image:: https://codeclimate.com/github/mattdavis90/promptr/badges/gpa.svg
   :target: https://codeclimate.com/github/mattdavis90/promptr
.. |Version| image:: https://img.shields.io/pypi/v/promptr.svg
   :target: https://pypi.python.org/pypi/promptr
.. |Docs| image:: https://readthedocs.org/projects/promptr/badge/?version=latest
   :target: https://promptr.readthedocs.io
.. |CLA| image:: https://cla-assistant.io/readme/badge/mattdavis90/promptr
   :target: https://cla-assistant.io/mattdavis90/promptr
.. |Downloads| image:: https://img.shields.io/pypi/dm/promptr.svg
   :target: https://pypi.python.org/pypi/promptr
.. |Compatibility| image:: https://img.shields.io/pypi/pyversions/promptr.svg
   :target: https://pypi.python.org/pypi/promptr
.. |Implementations| image:: https://img.shields.io/pypi/implementation/promptr.svg
   :target: https://pypi.python.org/pypi/promptr
.. |Format| image:: https://img.shields.io/pypi/format/promptr.svg
   :target: https://pypi.python.org/pypi/promptr
