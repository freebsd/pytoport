from setuptools import setup, find_packages

with open('README.md') as f:
    desc = f.read()

setup(
    name = "pytonorm",
    version = "0.1.0",
    packages = find_packages(),
    author = "Brendan Molloy",
    author_email = "brendan+pypi@bbqsrc.net",
    description = "Generate FreeBSD Makefiles from Python modules on PyPI",
    license = "BSD-2-Clause",
    keywords = "freebsd makefile pypi module",
    url = "https://github.com/bbqsrc/pytonorm/",
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
    entry_points = {
        'console_scripts': [
            'pytonorm = pytonorm:main'
        ]
    }
)
