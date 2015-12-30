from setuptools import setup, find_packages

with open('README.rst') as f:
    desc = f.read()

setup(
    name = "pytoport",
    version = "0.3.0a1",
    packages = find_packages(),
    author = "Brendan Molloy",
    author_email = "brendan+pypi@bbqsrc.net",
    description = "Generate FreeBSD Makefiles from Python modules on PyPI",
    license = "BSD-2-Clause",
    keywords = "freebsd makefile pypi module",
    url = "https://github.com/freebsd/pytoport/",
    long_description=desc,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ],
    install_requires = [
        'spdx_lookup>=0.3.0'
    ],
    entry_points = {
        'console_scripts': [
            'pytoport = pytoport:main'
        ]
    }
)
