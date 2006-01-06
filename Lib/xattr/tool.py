#!/usr/bin/python

import sys
import os
import getopt
import xattr

##
# Handle command line
##

# Defaults
attr_name = None
attr_value = None
long_format = False

def usage(e=None):
    if e:
        print e
        print ""

    print "usage: %s [-l] file [attr_name [attr_value]]" % (sys.argv[0],)
    print "  -l: print long format (attr_name: attr_value) when listing xattrs"
    print "  With no optional arguments, lists the xattrs on file"
    print "  With attr_name only, lists the contents of attr_name on file"
    print "  With attr_value, set the contents of attr_name on file"

    if e:
        sys.exit(1)
    else:
        sys.exit(0)

def main():
    # Read options
    try:
        (optargs, args) = getopt.getopt(sys.argv[1:], "hl", ["help"])
    except getopt.GetoptError, e:
        usage(e)

    for opt, arg in optargs:
        if opt in ("-h", "--help"):
            usage()
        elif opt == "-l":
            long_format = True

    if args:
        filename = args.pop(0)
    else:
        usage("No file argument")

    if args:
        attr_name  = args.pop(0)
    if args:
        attr_value = args.pop(0)

    ##
    # Do The Right Thing
    ##

    attrs = xattr.xattr(filename)

    if attr_name:
        if attr_value:
            attrs[attr_name] = attr_value
        else:
            if attr_name in attrs:
                if long_format:
                    print "%s: %s" % (attr_name, attrs[attr_name])
                else:
                    print attrs[attr_name]
            else:
                print "No such attribute."
                sys.exit(1)
    else:
        for attr_name in attrs:
            if long_format:
                print "%s: %s" % (attr_name, attrs[attr_name])
            else:
                print attr_name

if __name__ == '__main__':
    main()
