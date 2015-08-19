#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>


"""
    Find the best books to perform an amazing magic trick!
"""

import sys
import os
import argparse
import logging
import contextlib
import random
import itertools
import collections


log = logging.getLogger(os.path.basename(os.path.splitext(__file__)[0]))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__)

    parser.add_argument('-q', '--quiet', dest='loglevel',
                        const=logging.WARNING,
                        default=logging.INFO,
                        action="store_const",
                        help="Suppress informative messages.")

    parser.add_argument('-v', '--verbose', dest='loglevel',
                        const=logging.DEBUG,
                        action="store_const",
                        help="Verbose mode, output extra info.")

    parser.add_argument( '-b', '--books', default=4,
                        type=int, metavar="NUM",
                        help="How many books to choose."
                            " [Default: %(default)s]")

    parser.add_argument( '-c', '--chapters', default=16,
                        type=int, metavar="NUM",
                        help="How many chapters per book."
                            " [Default: %(default)s]")

    parser.add_argument('-r', '--randomize',
                        default=False,
                        action="store_true",
                        help="Randomize book data.")

    parser.add_argument( '-l', '--list', default=1,
                        type=int, metavar="NUM",
                        help="List the best NUM combinations."
                            " [Default: %(default)s]")

    parser.add_argument(dest='file', nargs="?", metavar="FILE",
                        help="File to export to or import from."
                            " [Default: stdout / stdin]")

    args = parser.parse_args(argv)
    args.debug = args.loglevel == logging.DEBUG
    args.ltoken = 'E'
    args.rtoken = 'D'
    args.tokens = args.ltoken + args.rtoken

    return args


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)s: %(message)s')
    log.debug(args)

    with openstd(args.file, 'r') as (fd, name):
        log.debug("Reading from %s", name)
        books = tuple([_i] + _.split('\n')[:3]
                      for _i, _ in
                        enumerate(fd.read()[:-1].strip().split('\n\n'), 1)
                      if _.strip())

    if len(books) < args.books:
        log.error("Need at least %d books to perform the magic!",
                  args.books)
        return 1

    if args.randomize:
        books = tuple(_[:3] + ["".join(random.choice(args.tokens)
                                       for _ in xrange(args.chapters))]
                      for _ in books)

    # Sanity tests
    for book in books:
        try:
            idx, title, author, chapters = book
        except ValueError:
            log.error("Data is incomplete for book: %s", book)
            log.error("Requires Title, Author, and Chapter data"
                      " (optional when using --randomize)")
            return 1

        if not args.randomize and len(chapters) != 16:
            log.error("Book %s does not have %d chapters", book, args.chapters)
            return 1

        log.info("Book %2d: %s, '%s' [%s]",
                  idx, chapters, title, author)

    combos = []
    for combo in itertools.combinations(books, args.books):
        log.debug(("\n%s\n" % "\n".join("%s\t%s" % (_[3], _[1])
                                        for _ in combo)).rstrip())
        data   = zip(*combo)[3]
        words  = ("".join(_) for _ in zip(*data))
        counts = collections.Counter(words)
        reps   = sorted((_ for _ in counts.values() if _ > 1),
                        reverse=True)
        score = sum(reps) - len(reps)

        combos.append((score, reps, combo))

        log.debug(counts)
        log.debug("Score: %2d  %s", score, reps)

    log.info("")
    log.info("Best %s out of %d combinations of %d books in %d:",
             args.list, len(combos), args.books, len(books))

    for score, reps, combo in sorted(combos)[:args.list]:
        log.info("")
        log.info("Dupes: %s (Total %d)%s", reps, score,
                 " NO DUPLICATES, hooray! :D" if score==0 else "")
        for book in combo:
            log.info("\t%2d - %s", *book[:2])




@contextlib.contextmanager
def openstd(filename=None, mode="r"):
    if filename and filename != '-':
        fh = open(filename, mode)
        name = "'%s'" % filename
    else:
        if mode.startswith("r"):
            fh = sys.stdin
            name = "<stdin>"
        else:
            fh = sys.stdout
            name = "<stdout>"
    try:
        yield fh, name
    finally:
        if fh is not sys.stdout:
            fh.close()




if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        log.critical(e, exc_info=True)
        sys.exit(1)
    except KeyboardInterrupt:
        pass