import re
from setuptools import setup, find_packages


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ""
    with open(fname, "r") as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError("Cannot find version information")
    return version


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name="promptr",
    version=find_version("promptr/__init__.py"),
    packages=find_packages(exclude=("test*", )),
    package_dir={"promptr": "promptr"},
    url="https://github.com/mattdavis90/promptr",
    license="MIT",
    author="Matt Davis",
    author_email="mattdavis90@googlemail.com",
    install_requires=("six", "prompt_toolkit"),
    tests_require=(),
    description=(
        "promptr is a toolkit for building CLI shells, similar to that found on a Cisco router."
    ),
    long_description=read("README.rst"),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
