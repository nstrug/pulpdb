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
    create_cv.py creates a content view from one or more repositories.
    
    %s [options]
    """) % sys.argv[0]

    parser = OptionParser(usage=usage)
    parser.add_option("-r", "--repoid", action='append',
        help=_("specify repo ids to add to the CV, can be specified multiple times (default is all enabled)"))
    parser.add_option("-c", "--cv",
        help=_("name of the Content View"))
    (opts, args) = parser.parse_args()
    return (opts, args)

def main():
    (opts, dummy) = parseArgs()
    
    if not opts.repoid:
        print "You must specify at least a repo to include in the CV"
        sys.exit(1)
    else:
        repos=opts.repoid
        
    if not opts.cv:
        print "You must specify a CV name"
        sys.exit(1)
    else:
        cv=opts.cv
    
    print("Creating content view %s from repos %s" % (cv, repos))
    cur.execute("""INSERT INTO cvs (name,latest_ver) VALUES (%s, %s)""", (cv,1))
    cur.execute("""SELECT cv_id from cvs where name = %s""", (cv,))
    cv_id = cur.fetchone()[0]
    cur.execute("""INSERT INTO cvvers (cv_id, ver) VALUES (%s, %s)""", (cv_id,1))
    cur.execute("""SELECT cvver_id FROM cvvers WHERE cv_id = %s AND ver = 1""", ([cv_id]))
    cvver_id = cur.fetchone()[0]
    for repo in repos:
        cur.execute("""INSERT INTO cvs_repos (cv_id, repo_id) VALUES ((SELECT cv_id FROM cvs WHERE name = %s),(SELECT repo_id FROM repos WHERE repoid = %s))""", (cv, repo))
        # create initial CV version
        repo_mv = "repo_mv_" + repo + "_" + cv + "_" + '1'
        #print cur.mogrify("""INSERT INTO repo_mvs (mat_view, cvver_id) VALUES (%s, %s)""", (repo_mv, cvver_id))
        #sys.exit()
        cur.execute("""INSERT INTO repo_mvs (mat_view, cvver_id) VALUES (%s, %s)""", (repo_mv, cvver_id))
        cur.execute("""CREATE MATERIALIZED VIEW """ + repo_mv + """ AS (SELECT rpms.* FROM rpms, rpms_repos, repos WHERE rpms.rpm_id = rpms_repos.rpm_id and rpms_repos.repo_id = repos.repo_id and repos.repoid = %s)""", ([repo]))
    conn.commit()    
 
    
    sys.exit(0)
    
if __name__ == "__main__":
    main()
    