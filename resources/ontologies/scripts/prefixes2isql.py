#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script will parse all unique prefixes from the *.ttl files
in the directory given as input parameter.

All the unique prefixes found will de added to an isql script
capable of inserting them into the target virtuoso database.
"""

from os.path import join
from glob import glob
import re

prefix_pattern = re.compile(r"@prefix\s+(\w*)\:\s+\<(.+?)\>")
DELETE_TEMPLATE = "delete from DB.DBA.SYS_XML_PERSISTENT_NS_DECL where NS_PREFIX='{0}';"
#INSERT_TEMPLATE = "insert into DB.DBA.SYS_XML_PERSISTENT_NS_DECL (NS_PREFIX, NS_URL) values ('{0}','{1}');"
INSERT_TEMPLATE = "DB.DBA.XML_SET_NS_DECL ('{0}', '{1}', 2);"
def main(dir_with_schemas):
    unique_prefixes = {}
    ttl_file_path = join(dir_with_schemas, "prefixes.ttl")
    ttl_file = open(ttl_file_path).read()
    prefixes = prefix_pattern.findall(ttl_file)
    partial_prefixes = dict(prefixes)
    unique_prefixes.update(partial_prefixes)
    for prefix, uri in unique_prefixes.items():
        print(DELETE_TEMPLATE.format(prefix))
        print(INSERT_TEMPLATE.format(prefix, uri))

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
