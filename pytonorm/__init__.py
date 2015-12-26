#!/usr/bin/env python3
#
# Copyright (c) 2015  Brendan Molloy <brendan+freebsd@bbqsrc.net>
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
#
# $FreeBSD$

# pytonorm is Swedish for python. ;)

import json
import os
import sys
from io import StringIO
from urllib import request
from os.path import expanduser, join, abspath
from subprocess import Popen, PIPE

LICENSEE_SCRIPT = """\
require 'json'
require 'licensee'

path = '%s'

project = Licensee::FSProject.new(path, detect_packages: true)

if project.license_file && project.matched_file && project.matched_file.license
  file = project.matched_file
  puts JSON.generate({
    :key => file.license.key,
    :filename => project.license_file.filename,
    :license => file.license.meta,
    :confidence => file.confidence
  })
else
  puts "null"
end
"""

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

def get_licenses(data):
    return data['info']['license']

def attempt_detect_license(path):
    p = Popen(['ruby'], stdin=PIPE, stdout=PIPE)
    out, err = p.communicate((LICENSEE_SCRIPT % path).encode('utf-8'))
    if p.returncode == 0:
        return json.loads(out.decode('utf-8'))

    return None

pl_prefix = "Programming Language :: Python :: "

def get_minimum(data):
    lowest = (1000, 1000)

    has_3 = False

    for k in data['info']['classifiers']:
        if k.startswith(pl_prefix):
            raw = k.strip(pl_prefix)
            if raw[0] not in ('2', '3'):
                continue
            if len(raw) == 1:
                major = int(raw[0])
                minor = 0
            else:
                major, minor = (int(x) for x in raw.split('.'))
            if major == 3:
                has_3 = True
            if (major, minor) < lowest:
                lowest = (major, minor)

    if lowest == (1000, 1000):
        return None

    if lowest[0] == 2:
        lowest = (2, 7)
    n = "%d.%d" % lowest
    if has_3:
        return "%s+" % n
    return n

def add(o, k, v):
    o.write("%s=" % k)
    if len(k) < 7:
        o.write('\t')
    o.write("\t%s\n" % v)

def generate_makefile(data, path=os.getcwd(), name=None, email=None):
    info = data['info']
    o = StringIO()
    o.write("# Created by: ")
    if name is not None and email is not None:
        o.write("%s <%s>" % (name, email))
    o.write("\n# $FreeBSD$\n\n")

    add(o, "PORTNAME", info['name'].lower())
    add(o, "PORTVERSION", info['version'])
    add(o, "CATEGORIES", "devel")
    add(o, "MASTER_SITES", "CHEESESHOP")
    add(o, "PKGNAMEPREFIX", "${PYTHON_PKGNAMEPREFIX}")
    o.write('\n')

    if email is None:
        add(o, "MAINTAINER", "# FILL ME")
    else:
        add(o, "MAINTAINER", email)
    add(o, "COMMENT", info['summary'])
    o.write('\n')

    if info.get('licfile', None):
        add(o, "LICENSE", info['license'])
        add(o, "LICENSE_FILE", "${WRKSRC}/%s" % info['licfile'])
    else:
        add(o, "# LICENSE", "%s # Ensure this is valid!" % get_licenses(data))
    o.write('\n')

    deps = data['info'].get('requires_dist', None)
    if deps is not None:
        d = []
        for dep in deps:
            name, ver = dep.split(' ')
            ver = ver[1:-1] # remove brackets
            d.append("${PYTHON_PKGNAMEPREFIX}%s%s:${PORTSDIR}/XXX/py-%s" % (
                name, ver, name))

        add(o, 'RUN_DEPENDS', ' \\\n\t\t\t'.join(d))
        o.write('\n')

    min_py = get_minimum(data)
    if min_py:
        add(o, "USES", "python:%s" % min_py)
    else:
        add(o, "USES", "python")

    add(o, "USE_PYTHON", "distutils autoplist")
    o.write('\n.include <bsd.port.mk>')

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
    key = license_data['key']
    lic = LICENSEE_KEYS.get(key, None)

    if lic is None:
        return

    data['info']['license'] = lic
    data['info']['licfile'] = license_data['filename']

def main():
    if len(sys.argv) < 3:
        print("Usage: pytonorm [path] [modules...]")
        sys.exit(1)

    try:
        with open(join(expanduser("~"), ".pytonorm")) as f:
            user = json.load(f)
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
        print("[-] Generating %s..." % name)

        if name.lower().startswith('py-'):
            name = name[3:]

        path = abspath(join(base, 'py-%s' % name.lower()))
        os.makedirs(path)
        generate_makefile(data, path, **user)
        src = download_source(data, path, distdir)

        if src is None:
            no_src.append(name)
            continue

        extract_source(join(distdir, src), distdir)

        src_dir = join(distdir, src.rstrip('.tar.gz'))
        license_data = attempt_detect_license(src_dir)
        if license_data:
            update_license_data(data, license_data)
            print("[-] Updating data with correct license")
            regen = True

        if regen:
            print("[-] Regenerating makefile with new data")
            generate_makefile(data, path, **user)

    if len(no_src):
        print('[!] The following packages had no source dist:')
        for src in no_src:
            print('  - %s' % src)

if __name__ == "__main__":
    main()
