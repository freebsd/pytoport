# pytoport

A fairly normal way to generate FreeBSD port Makefiles straight from PyPI.

## Usage

You specify a base directory for the packages to be generated into, then just
let it rip!

```
$ pytoport ~/my-ports/devel nosetests fixtures
```

In your `~/my-ports/devel` directory, you will find `py-nosetests` and
`py-fixtures` with a `Makefile` and if you're lucky, a `distinfo` too.

## License

BSD 2-clause. See LICENSE.
