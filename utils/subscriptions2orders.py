#! /usr/bin/python

import sys
import cx_Oracle
import json
import httplib2
import re
import os.path
import copy
import datetime
from optparse import Option, OptionParser

def _get_oracle_error_info(self, error):
    if isinstance(error, cx_Oracle.DatabaseError):
        e = error[0]
        return (e.code, e.message, e.context)
    return str(error)

def process_rels(response):
  if "link" not in response:
      return {}
  links = response["link"].split(',')
  regex = re.compile(r'<(.*?)>; rel="(\w+)"')
  hash_refs = {}
  for link in links:
    href, name = regex.findall(link)[0]
    hash_refs[name] = href
  return hash_refs

options_table = [
    Option("--dbpw", action="store", help="Database password"),
    Option("--orgcreds", action="append", type="string", help="Organization credentials <user>:<password>"),
    Option("--debug", action="store_true", help="Enable debug logging")
]
help_text = """%prog [options] <outfile>"""
parser = OptionParser(usage=help_text, option_list=options_table)

(options, args) = parser.parse_args()

if not args or not args[0]:
    print "missing outfile"
    sys.exit(1)

try:
    dbh = cx_Oracle.connect("NCCQUERY/%s@//wwworacleprod.provo.novell.com:1521/novUTF8" % options.dbpw)
    cursor = dbh.cursor()
except self.OracleError, e:
    ret = self._get_oracle_error_info(e)
    if isinstance(ret, types.StringType):
        print "Unable to connect to database: %s" % ret
        sys.exc_info()[2]
    else:
        (errno, errmsg) = ret[:2]
        print "Connection attempt failed (%s): %s" % (errno, errmsg)
    sys.exit(1)

cursor.prepare("""
    SELECT na.parent_part, na.fulfill_start_date,
           na.fulfill_end_date, na.fulfill_node_count,
           na.fulfillment_id
      FROM NCC.ncc_all_by_address_v na
     WHERE na.address_id = :orgname
       AND na.key_value = :regcode
       """)

result = []
for cred in options.orgcreds:
    subscriptions = []
    (orgname, orgpass) = cred.split(':', 2)
    h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
    h.add_credentials(orgname, orgpass)
    (resp, content) = h.request("https://scc.suse.com/connect/organizations/subscriptions", "GET")
    if options.debug:
        print "download subscriptions for user %s" % orgname
    while True:
        subscriptions.extend(json.loads(content))
        rels = process_rels(resp)
        if not 'next' in rels:
            break
        (resp, content) = h.request(rels['next'], "GET")
        if options.debug:
            print "download subscriptions"

    for item in subscriptions:
        item['scc_org_id'] = orgname
        cursor.execute(None, {'orgname': orgname, 'regcode': item['regcode']})
        if options.debug:
            print "enhance item"

        res = cursor.fetchall()
        for (part_number, start_date, end_date, node_count, fulfillment_id) in res:
            if not start_date:
                start_date = datetime.datetime(1970, 1, 1, 0, 0, 0)
            if not end_date:
                end_date = datetime.datetime(2100, 12, 31, 23, 59, 59)

            if options.debug:
                print "id: %s, part_number: %s, start_date: %s, end_date: %s, node_count: %s" % (
                    fulfillment_id, part_number, start_date, end_date, node_count)
            item['part_number'] = part_number
            item['starts_at'] = start_date.strftime('%FT%TZ')
            item['expires_at'] = end_date.strftime('%FT%TZ')
            item['system_limit'] = node_count
            item['id'] = fulfillment_id
            result.append(copy.deepcopy(item))

with open(args[0], 'w') as f:
    json.dump(result, f, sort_keys=True, indent=4, separators=(',', ': '))

print "Wrote %s. Finished successfully" % args[0]
