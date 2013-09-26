#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import optparse
import tempfile
import logging

import SkypeLog

def print_epilog(self, formatter):
    return self.epilog

def main():
    # handling commandline arguments
    optparse.OptionParser.format_epilog = lambda self, formatter: self.epilog
    
    usage = "usage: %prog [options] file [file ...]"
    epilog = """
Examples:

%s -o ~/Desktop/ -L ja ~/Library/Application\ Support/Skype/my_skype_name/main.db
""" % os.path.basename(__file__)

    parser = optparse.OptionParser(usage=usage, epilog=epilog)
    parser.add_option("-o", "--output-dir", dest="output_dir", default=".",
                help="write output to OUTPUT_DIR", metavar="OUTPUT_DIR")
    parser.add_option("-L", "--locale", dest="locale", default="en",
                help="set locale to LOCALE", metavar="LOCALE")
    parser.add_option("-T", "--name-table", dest="nametable", default="",
                help="load id-to-name table from NAMETABLE file", metavar="NAMETABLE")
    parser.add_option("-N", "--no-write", dest="dry_run", action="store_true",
                help="do not output files")
    parser.add_option("-v", "--verbose", dest="verbose", action="count",
                help="print verbose output")
    parser.add_option("", "--debug", dest="debug", action="store_true",
                help="debug mode, same as -vv -N")
    (options, args) = parser.parse_args()
    
    # debug, verbose
    if options.debug:
        options.verbose = 2
        options.dry_run = True
    
    if options.verbose == 1:
        logging.basicConfig()
    elif options.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    
    # load id2name table
    nametable = {}
    if options.nametable:
        for ln in open(options.nametable):
            ln_split = ln.split(" ")
            _key = ln_split[0]
            _value = " ".join(ln_split[1:])
            nametable[_key] = _value

    # convert logs
    for f in args:
        reader = SkypeLog.Reader()
        reader.set_nametable(nametable)
        reader.load(f)
        chats = reader.read()
        for c in chats:
            conv = SkypeLog.EmailConverter(chat=c, locale=options.locale)
            if not options.dry_run:
                output_file = tempfile.NamedTemporaryFile(dir=options.output_dir,
                                prefix="skypelog-", suffix=".eml", delete=False)
                conv.write(output_file)
                output_file.close()

if __name__ == "__main__":
    main()