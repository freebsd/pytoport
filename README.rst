pytoport
========

A fairly normal way to generate FreeBSD port Makefiles straight from
PyPI.

Installation
------------

FreeBSD
~~~~~~~

You can install ``pytoport`` using
`pkg(8) <https://github.com/freebsd/pkg>`__, or the Ports framework:

::

    $ pkg install -g pyXY-pytoport # Where XY is Python version eg. 34
    or
    $ make -C /usr/ports/ports-mgmt/py-pytoport install clean

From source (for development)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is recommended to create a ``virtualenv`` to install your
dependencies in order to not pollute your system installation:

::

    $ virtualenv --python=python3.X /path/to/venv
    $ source /path/to/venv/bin/activate
    $ pip install -r requirements.txt

You can then install from the ``setup.py`` directly, use ``pip``, or run
locally with:

::

    $ python -m pytoport

Usage
-----

You specify a base directory for the packages to be generated into, then
just let it rip!

::

    $ pytoport ~/my-ports/devel nosetests fixtures

In your ``~/my-ports/devel`` directory, you will find ``py-nosetests``
and ``py-fixtures`` with a ``Makefile`` and if you're lucky, a
``distinfo`` and ``pkg-descr`` too.

You should also create a ``~/.porttools`` file with the following
details:

::

    EMAIL="your@email.address"
    FULLNAME="Your Name"

If you don't create this file, you'll have to fill out the
relevant parts of the ``Makefile`` yourself.

License
-------

BSD 2-clause. See LICENSE.
