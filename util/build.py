#!/usr/bin/env python

# modified version of build.py from three.js project.
# https://github.com/mrdoob/three.js",

import urllib
import os
import tempfile
import sys
import zipfile

COMMON_FILES = [
    "url.js",
    "sha1.js",
    #"rand.js",
    "ec_secp192r1.js",
    "ec.js",
    "cpk_private_matrix.js",
    "cpk.js",
    #"bn_nist.js",
    # TODO
    # What on earth happened to bn_barret.js?
    #"bn_barrett.js",
    #"bn.js",
    "base64.js",
    "aes_ctr.js",
    "aes.js",
]

EXTRAS_FILES = [
]

TEST_FILES = [
]

def merge(files):

    buffer = []

    for filename in files:
        with open(os.path.join('..', 'src', filename), 'r') as f:
            buffer.append(f.read())

    return "".join(buffer)


def output(text, filename):

    with open(os.path.join('..', 'build', filename), 'w') as f:
        f.write(text)


def compress(text):

    in_tuple = tempfile.mkstemp()
    with os.fdopen(in_tuple[0], 'w') as handle:
        handle.write(text)

    out_tuple = tempfile.mkstemp()

    os.system("java -jar compiler/compiler.jar --language_in=ECMASCRIPT5 --js %s --js_output_file %s" % (in_tuple[1], out_tuple[1]))

    with os.fdopen(out_tuple[0], 'r') as handle:
        compressed = handle.read()

    os.unlink(in_tuple[1])
    os.unlink(out_tuple[1])

    return compressed


def addHeader(text, endFilename):
    with open(os.path.join('..', 'REVISION'), 'r') as handle:
        revision = handle.read().rstrip()

    return ("// %s r%s - https://github.com/zooko/jscrypto\n" % (endFilename, revision)) + text


def makeDebug(text):
    position = 0
    while True:
        position = text.find("/* DEBUG", position)
        if position == -1:
            break
        text = text[0:position] + text[position+8:]
        position = text.find("*/", position)
        text = text[0:position] + text[position+2:]
    return text


def buildLib(files, debug, unminified, filename):

    text = merge(files)

    if debug:
        text = makeDebug(text)
        filename = filename + 'Debug'

    folder = ''

    filename = filename + '.js'

    print "=" * 40
    print "Compiling", filename
    print "=" * 40

    if not unminified:
        text = compress(text)

    output(addHeader(text, filename), folder + filename)


def buildIncludes(files, filename):

    template = '\t\t<script type="text/javascript" src="../src/%s"></script>'
    text = "\n".join(template % f for f in files)

    output(text, filename + '.js')


def makeTestRunner():
    path = '../build/test_jscrypto.js'
    tpl = "function runTestSuite() {\n%s\n}"
    contents = tpl % open(path).read()
    with open(path, 'w') as out:
        out.write(contents)

def get_compiler():
    if not os.path.exists('compiler/compiler.jar'):
        print 'downloading closure compiler'
        down = urllib.urlopen('http://closure-compiler.googlecode.com/files/compiler-latest.zip')
        with open('compiler/compiler-latest.jar', 'wb') as out:
            out.write(down.read())
        zf = zipfile.ZipFile('compiler/compiler-latest.jar')
        zf.extract('compiler.jar', path='compiler')
        zf.close()


def main():
    here = os.path.dirname(__file__)
    os.chdir(here)

    get_compiler()

    debug = False
    unminified = False
    build_all = True
    includes = ()

    lib_config = [
        ['jscrypto', 'includes', COMMON_FILES + EXTRAS_FILES, True],
    ]
    test_config = [
        ['test_jscrypto', 'includes', TEST_FILES, True],
    ]

    for config in (lib_config, test_config):
        for fname_lib, fname_inc, files, enabled in config:
            if enabled or build_all:
                buildLib(files, debug, unminified, fname_lib)
                if includes:
                    buildIncludes(files, fname_inc)

    makeTestRunner()

if __name__ == "__main__":
    main()

