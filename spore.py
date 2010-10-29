#!/usr/bin/python

# -*- coding: utf-8 -*-
#  Copyright (C) 2010 Elias Showk
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__="elishowk@nonutc.fr"

import getopt
import sys
from pprint import pformat
import spore

def usage():
    print "USAGE : python spore.py config_file_path"

if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:],'')
    if len(args) < 1:
        usage()
        exit()

    configURL = args[0]

    try:
        spore_instance = spore.SporeCore(configURL)
    except Exception, exc:
        print exc
        usage()
        exit()

    print spore_instance.spec
    # TODO : parse confFile for every method defined
    req = spore_instance.askhn_posts()
    print req
