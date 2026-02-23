#!/usr/bin/env python
import sys

from wallabag.wallabag import cli

if __name__ == "__main__":
    sys.argv[0] = sys.argv[0].removesuffix(".exe")
    sys.exit(cli())
