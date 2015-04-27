#!/usr/bin/python -tt

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# copyright 2006 Duke University
# author seth vidal

# sync all or the newest packages from a repo to the local path
# TODO:
#     have it print out list of changes
#     make it work with mirrorlists (silly, really)
#     man page/more useful docs
#     deal nicely with a package changing but not changing names (ie: replacement)

# criteria
# if a package is not the same and smaller then reget it
# if a package is not the same and larger, delete it and get it again
# always replace metadata files if they're not the same.





import os
import sys
import shutil
import stat

from optparse import OptionParser
from urlparse import urljoin

from yumutils.i18n import _

import yum
import yum.Errors
from yum.packageSack import ListPackageSack
import rpmUtils.arch
import logging
from urlgrabber.progress import TextMeter, TextMultiFileMeter
import urlgrabber
import psycopg2

try:
    conn = psycopg2.connect("dbname='pulpdb'")
except:
    print "I am unable to connect to the database"
cur = conn.cursor()

def parseArgs():
    usage = _("""
    update_cv.py updates a content view from one or more repositories.
    
    %s [options]
    """) % sys.argv[0]

    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--cv",
        help=_("name of the Content View"))
    (opts, args) = parser.parse_args()
    return (opts, args)

def main():
    (opts, dummy) = parseArgs()
        
    if not opts.cv:
        print "You must specify a CV name"
        sys.exit(1)
    else:
        cv=opts.cv
    
    print("Updating content view %s" % (cv,))
    # get the list of MVs to update
    cur.execute("""SELECT mat_view FROM repo_mvs, cvvers, cvs WHERE repo_mvs.cvver_id = cvvers.cvver_id AND cvvers.cv_id = cvs.cv_id AND cvvers.ver = cvs.latest_ver AND cvs.name = %s""", (cv,))
    for mat_view in cur.fetchone()[0]:  
        print mat_view
        #cur.execute("""REFRESH MATERIALIZED VIEW""" + mat_view) 
    conn.commit()    
 
    
    sys.exit(0)
    
if __name__ == "__main__":
    main()
    