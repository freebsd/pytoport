pytoport
========

A fairly normal way to generate FreeBSD port Makefiles straight from
PyPI.

Installation
------------

FreeBSD
^^^^^^^

You can install pytport using `pkg(8) <https://github.com/freebsd/pkg>`_ or 
port framework:

::

   # pkg install -g py\*-pytoport
   or
   # make -C /usr/ports/ports-mgmt/py-pytoport install clean

From Source
^^^^^^^^^^^

In order to use pytoport, you should install the required dependencies:

::

    $ pip install -r requirements.txt
    $ pip install pytoport

It's recommend to create a virtualenv to install your dependencies in order to
not pollute your system installation:

::

    $ virtualenv --python=python3.X /path/to/venv
    $ source /path/to/venv
    $ pip install -r requirements.txt

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

See ``man 5 porttools`` for more information. If you don't create this
file, you'll have to fill out the relevant parts of the ``Makefile``
yourself.

License
-------

BSD 2-clause. See LICENSE.
