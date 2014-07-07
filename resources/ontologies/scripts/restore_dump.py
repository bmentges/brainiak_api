#!/usr/bin/env python
# python restore_dump.py /usr/local/virtuoso-git/var/lib/virtuoso/db/dumps/ > x.isql
# isql localhost dba dba x.isql
"""
restore_dump.py

Created by rodrigo.senra on 2013-03-18.
Copyright (c) 2013 Globo.com - Semantic Team (42). All rights reserved.
"""

import sys
import os
from glob import glob

template = """

SPARQL DROP SILENT GRAPH <%(graph)s/>;
SPARQL CREATE GRAPH <%(graph)s/>;
rdfs_rule_set('http://semantica.globo.com/ruleset', '%(graph)s');
DB.DBA.TTLP_MT_LOCAL_FILE('%(ttl_file)s', '', '%(graph)s/');

"""

def main(target_dir):
    for full_ttl_file in glob(os.path.join(target_dir, "*.ttl")):
        ttl_file = "dumps/" + os.path.basename(full_ttl_file)
        graph_name = open(full_ttl_file+".graph").read().strip()[:-1]
        cmd = template % {"graph":graph_name, "ttl_file":ttl_file}
        print(cmd)


if __name__ == '__main__':  
    # Inform directory with .ttl and .ttl.graph
    target_dir = sys.argv[1]
    main(target_dir)

