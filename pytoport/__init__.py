#!/usr/bin/env python3
#
# Copyright (c) 2015 Brendan Molloy <brendan+freebsd@bbqsrc.net>
# Copyright (c) 2019 Steve Wills <steve@mouf.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import json
import re
import os
import sys
import textwrap
from io import StringIO
from urllib import request
from os.path import expanduser, join, abspath
from subprocess import Popen

import docutils
import docutils.frontend
import docutils.utils
import docutils.parsers.rst
import spdx_lookup
from FreeBSD_ports import FreeBSD_ports
from pkg_resources import parse_version
import packaging.requirements


def rst_to_text(rst_data):
    settings = docutils.frontend.OptionParser(
        components=(docutils.parsers.rst.Parser,)).get_default_values()
    doc = docutils.utils.new_document('', settings)
    parser = docutils.parsers.rst.Parser()
    parser.parse(rst_data, doc)
    return doc.astext()


def get_sdist(data):
    version = data['info']['version']
    for o in data['releases'][version]:
        if o['packagetype'] == 'sdist':
            return o


def get_package_metadata(name):
    url = 'https://pypi.python.org/pypi/{}/json'.format(name)
    with request.urlopen(url) as f:
        data = json.loads(f.read().decode('utf-8'))
    return data


def generate_pkg_descr(data, path=os.getcwd()):
    info = data['info']
    no_desc = '!! NO DESCRIPTION FOUND. !!'
    desc = info.get('description', no_desc)

    try:
        desc = rst_to_text(desc)
    except:
        pass

    d = "\n\n".join(textwrap.fill(x, width=80) for x in desc.split('\n\n'))
    with open(join(path, 'pkg-descr'), 'w') as f:
        f.write("%s\n" % d)


def get_licenses(data):
    return data['info']['license']


def attempt_detect_license(path):
    return spdx_lookup.match_path(path)

classifier_re = re.compile('\s*::\s*')
pl_prefix = ("Programming Language", "Python")


def version_iter(data):
    for k in data['info']['classifiers']:
        parts = tuple(classifier_re.split(k))
        plen = len(parts)
        if plen >= 3 and parts[:2] == pl_prefix:
            raw = parts[2].split('.')
            if raw[0] not in ('2', '3'):
                continue
            elif len(raw) == 1:
                yield (int(raw[0]), -1)
            else:
                yield tuple(int(x) for x in raw)

def version_parse(version):
    if len(version) == 0:
        return('>=0')
    vdep = version.split(',')
    newv = None
    veq = None
    for v in vdep:
        if v[0] == '>' or v[0] == '=':
            if v[1] == '=':
                newv = v[2:]
                veq = True
            else:
                newv = v[1:]
    if newv != None:
        version = newv
    if not parse_version(version) > parse_version('0'):
        version = '>=0'
    else:
        if veq == True:
            version = ">=" + version
        else:
            version = ">" + version
    return version


# Keep in synch with _PYTHON_VERSIONS in bsd.default-versions.mk
all_python_ports_versions = [(3, 9), (3, 8), (3, 7), (3, 10), (3, 11), (2, 7)]

def get_upstream_versions(upstream_supported):
    # Join the list of upstream versions into a string to be
    # used as a comment on the USE+=python line

    versions = []
    for v in upstream_supported:
        if v[1] == -1:
            versions.append("%s" % v[0])
        else:
            versions.append("%s.%s" % v)

    return ", ".join(versions)


def get_matching_versions(upstream_supported):
    # The intersections of the ports supported versions and upstream supported
    # versions in order
    py_port_versions = [
        v for v in upstream_supported
            if v in all_python_ports_versions
    ]

    # No specific matching versions, but upstream may specify just the major
    # version.
    if len(py_port_versions) == 0:
        print("Warning: upstream declared python versions do not intersect with ports supported python versions.")
        if (3, -1) in upstream_supported:
            print("Assuming generic compatibility with python 3.x")
            py_port_versions = [
                v for v in upstream_supported if v[0] == 3
            ]
        elif (2, -1) in upstream_supported:
            print("Assuming generic compatibility with python 2.x")
            py_port_versions = [
                v for v in upstream_supported if v[0] == 2
            ]

    # No matching versions at all
    if len(py_port_versions) == 0:
        print("No matching versions found")

    return py_port_versions


def get_python_version_range(data):
    upstream_supported = list(version_iter(data))
    upstream_supported.sort()

    upstream_versions = get_upstream_versions(upstream_supported)

    py_port_versions = get_matching_versions(upstream_supported)
    if len(py_port_versions) == 0:
        return (None, upstream_versions)

    # A USES=python version range specification is built from two part
    # "major.minor" version strings: either a simple version string, eg. 3.9;
    # an open-ended range above a minimum, eg. 3.9+ (This is the most common);
    # a bounded range at both extremes, eg. 3.9-3.11 or an open ended range
    # below a maximum eg. -3.9 (very rare).

    min_version = ""
    max_version = ""
    range_indicator = ""

    if min(all_python_ports_versions) < min(py_port_versions):
        min_version = "%s.%s" % min(py_port_versions)

    if max(all_python_ports_versions) > max(py_port_versions):
        max_version = "%s.%s" % max(py_port_versions)

    if min_version:
        if max_version:
            range_indicator = "-"
        else:
            range_indicator = "+"
    elif max_version:
        range_indicator = "-"

    version_range = "%s%s%s" % (min_version, range_indicator, max_version)

    return (version_range, upstream_versions)


# Needs to track bsd.default-versions.mk
python_pkgprefix = "py39-"

def gen_dep(pkg):
    ports = FreeBSD_ports()
    portpath = ports.find_portdir(python_pkgprefix + pkg)
    if portpath is None:
        portpath = "XXX/py-" + pkg
    return portpath

def add(o, k, v):
    o.write("%s=" % k)
    if len(k) < 7:
        o.write('\t')
    o.write("\t%s\n" % v)


def generate_makefile(data, path=os.getcwd(), name=None, email=None):
    info = data['info']
    o = StringIO()

    add(o, "PORTNAME", info['name'].lower())
    add(o, "PORTVERSION", info['version'])
    add(o, "CATEGORIES", "devel python")
    add(o, "MASTER_SITES", "PYPI")
    add(o, "PKGNAMEPREFIX", "${PYTHON_PKGNAMEPREFIX}")
    o.write('\n')

    if email is None:
        add(o, "MAINTAINER", "# FILL ME")
    else:
        add(o, "MAINTAINER", email)
    summary = info.get('summary', '# FILL ME')
    add(o, "COMMENT", "{}".format(summary.capitalize().rstrip('.')))
    www = info.get('home_page', info['package_url'])
    add(o, "WWW", www)
    o.write('\n')

    if info.get('licfile', None):
        add(o, "LICENSE", info['license'])
        add(o, "LICENSE_FILE", "${WRKSRC}/%s" % info['licfile'])
    else:
        add(o, "# LICENSE", ("%s # Ensure this is valid! " +
            "See ${PORTSDIR}/Mk/bsd.licenses.db.mk.") % get_licenses(data))
    o.write('\n')

    deps = data['info'].get('requires_dist', None)
    if deps is not None:
        d = []
        for dep in sorted(deps, key=str.lower):
            x = packaging.requirements.Requirement(dep)

            pkg = x.name
            version = version_parse(str(x.specifier))

            if "extra" in str(x.marker):
                print("%s has extra info: %s" % (pkg, x.marker))

            portpath = gen_dep(pkg)
            d.append("${PYTHON_PKGNAMEPREFIX}%s%s:%s@${PY_FLAVOR}" % (
                pkg, version, portpath))

        add(o, 'RUN_DEPENDS', ' \\\n\t\t'.join(d))
        o.write('\n')

    py_version_range = get_python_version_range(data)
    if py_version_range[0] is None or py_version_range[0] == "":
        add(o, "USES", "python # %s" % py_version_range[1])
    else:
        add(o, "USES", "python:%s # %s" % py_version_range)

    add(o, "USE_PYTHON", "autoplist distutils")
    o.write('\n.include <bsd.port.mk>\n')

    with open(join(path, 'Makefile'), 'w') as f:
        f.write(o.getvalue())
    print('[-] Makefile generated.')


def download_source(data, path=os.getcwd(), distdir=None):
    if distdir is None:
        distdir = path
    sdist = get_sdist(data)
    if sdist is None:
        print('[!] No source distribution could be found!')
        return None

    env = os.environ.copy()
    env['DISTDIR'] = distdir

    p = Popen(['make', 'makesum'], env=env, cwd=path)
    p.wait()
    if p.returncode != 0:
        print("[!] Error generating checksum (errno %d)" % p.returncode)
        sys.exit(1)

    return sdist['filename']


def extract_source(path, dest):
    p = Popen(['tar', 'xf', path], cwd=dest)
    p.wait()

LICENSEE_KEYS = {
    "agpl-3.0": "AGPLv3",
    "apache-2.0": "APACHE20",
    "artistic-2.0": "ART20",
    "bsd-2-clause": "BSD2CLAUSE",
    "bsd-3-clause-clear": "BSD3CLAUSE",
    "bsd-3-clause": "BSD3CLAUSE",
    "cc0-1.0": "CC0-1.0",
    "epl-1.0": "EPL",
    "gpl-2.0": "GPLv2",
    "gpl-3.0": "GPLv3",
    "isc": "ISCL",
    "lgpl-2.1": "LGPL21",
    "lgpl-3.0": "LGPL3",
    "mit": "MIT",
    "mpl-2.0": "MPL",
    "ofl-1.1": "OFL11"
}


def update_license_data(data, license_data):
    key = license_data.license.id.lower()
    id_ = LICENSEE_KEYS.get(key, None)

    if id_ is None:
        return

    data['info']['license'] = id_
    data['info']['licfile'] = license_data.filename


def parse_dot_porttools(f):
    config = {}

    for line in f:
        try:
            key, val = line.split("=")
            key = key.strip()
            val = val.strip()
            if key == "EMAIL":
                config['email'] = val[1:-1]
            if key == "FULLNAME":
                config['name'] = val[1:-1]
        except:
            pass

    return config


def main():
    if len(sys.argv) < 3:
        print("Usage: pytoport [path] [modules...]")
        sys.exit(1)

    try:
        with open(join(expanduser("~"), ".porttools")) as f:
            user = parse_dot_porttools(f)
    except:
        user = {}

    base = sys.argv[1]
    distdir = abspath(join(base, '_distdir'))
    os.makedirs(distdir, exist_ok=True)

    no_src = []

    for arg in sys.argv[2:]:
        regen = False
        data = get_package_metadata(arg)
        name = data['info']['name']
        print("[-] Generating files for %s..." % name)

        if name.lower().startswith('py-'):
            name = name[3:]

        path = abspath(join(base, 'py-%s' % name.lower()))
        os.makedirs(path, exist_ok=True)

        print("[-] Generating Makefile")
        generate_makefile(data, path, **user)

        print("[-] Generating pkg-descr")
        generate_pkg_descr(data, path)

        print("[-] Downloading source files")
        src = download_source(data, path, distdir)

        if src is None:
            no_src.append(name)
            continue

        print("[-] Extracting source files")
        extract_source(join(distdir, src), distdir)

        src_dir = join(distdir, src.rstrip('.tar.gz'))
        license_data = attempt_detect_license(src_dir)
        if license_data:
            update_license_data(data, license_data)
            print("[-] Updating data with correct license")
            regen = True
        else:
            print("[-] No LICENSE file found in package, couldn't update")

        if regen:
            print("[-] Regenerating makefile with new data")
            generate_makefile(data, path, **user)

        print("[*] GENERATED: %s" % name)

    if len(no_src):
        print('[!] The following packages had no source dist:')
        for src in no_src:
            print('  - %s' % src)

if __name__ == "__main__":
    main()
