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

You should also create a `~/.pytoport` file with the following details:

```
{
    "email": "your@email.address",
    "name": "Your Name"
}
```

If you don't, you'll have to fill out the relevant parts of the `Makefile`
yourself.

## License

BSD 2-clause. See LICENSE.
