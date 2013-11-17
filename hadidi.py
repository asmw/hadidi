#!/usr/bin/env python
"""HaDiDi (HashDirDiff)
Compares the content of two directories based on file hashes

Usage: hadidi.py [-hvqsa] [-f regex...] [-l <alg>] <directory> <directory>

Options:
  -h --help                    Show this screen.
  -v --version                 Show version.
  -q --quiet                   Return 1 for differences, 0 if all files correspond
  -s --same                    Print files with the same hash
  -f <regex> --filter=<regex>  Filter files from comparison. re.compile is used
  -a --hash                    Also print hashes for files
  -l <alg> --alg <alg>         Set hashlib algorithm [default: md5]

"""
from docopt import docopt
from os import walk
from os.path import join
import re
import hashlib
import sys

def hashdir(path, filt = None, alg = "md5"):
    ret = {}
    for root, paths, files in walk(path):
        for filepath in [join(root, name) for name in files if (not filt or not filt.match(name))]:
            hasher = hashlib.new(alg)
            with open(filepath, 'rb') as fd:
                # TODO: Large files? Links?
                hasher.update(fd.read())
                # TODO: Same file in one tree?
                ret[hasher.hexdigest()] = filepath
    return ret

def hashdiff(left, right):
    same = {}
    only_left = {}
    for filehash, filename in left.iteritems():
        if filehash in right:
            same[filehash] = [filename, right[filehash]]
            right.pop(filehash, None)
        else:
            only_left[filehash] = filename
    return same, only_left, right

def print_hashes(list, banner = None, print_hash = False):
    if len(list) > 0:
        if banner:
            print banner
        for h, f in list.iteritems():
            if print_hash:
                print(" %s[%s] %s" % (print_hash, h, f))
            else:
                print("  %s" % f)

if __name__ == "__main__":
    args = docopt(__doc__, version='hadidi 0.1')
    quiet = args['--quiet']
    show_same = args['--same']
    alg = args['--alg']
    print_hash = args['--hash'] and alg or False
    left = args['<directory>'][0]
    right = args['<directory>'][1]
    filt = len(args['--filter']) and re.compile("(%s)" % ')|('.join(args['--filter']))

    same, only_left, only_right = hashdiff(hashdir(left, filt, alg), hashdir(right, filt, alg))
    if quiet:
        if (len(only_left) + len(only_right)) > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        print_hashes(only_left, "Only in %s:" % left, print_hash)
        print_hashes(only_right, "Only in %s:" % right, print_hash)
    if show_same:
        print("Files with the same hashes:")
        for h, [l, r] in same.iteritems():
            print("\t%s = %s" % (l, r))

