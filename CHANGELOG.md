# Changelog for pytoport

## v0.4.0 - 2015-12-31

- Generate a simple `pkg-descr` from given metadata
- Improved messaging further
- If it can be detected all >2.7 are supported, drop suffix

## v0.3.1 - 2015-12-30

- Fix logic error for handling updating detected licenses
- Fix logic error for major version only trove ids (eg, no more '3.-1')

## v0.3.0 - 2015-12-30

- Can handle more exotic dependency lists now
- Dropped ruby `licensee` dependency (but it was fun while it lasted)
- Added `spdx-lookup` dependency (Python this time)
- Supported Python versions are now supplied in a comment in the generated `Makefile`
- More helpful messaging
- Fixed several bugs (see commits)

## v0.2.0

- Let's just call this the first release.
