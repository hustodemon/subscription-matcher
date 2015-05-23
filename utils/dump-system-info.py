#! /usr/bin/python

import json
from optparse import OptionParser
from spacewalk.common.rhnConfig import CFG, initCFG
from spacewalk.server import rhnSQL

initCFG('server')
rhnSQL.initDB()

result = []

parser = OptionParser(version="%prog 0.1",
                      description="Dump system info as JSON")

parser.add_option("-o", "--output", action="store", dest="outfile",
                  help="Write to OUTFILE instead of STDOUT")
parser.add_option("-p", "--pretty", action="store_true", dest="pretty",
        help="Pretty printing")

(options, args) = parser.parse_args()


q_system_products = rhnSQL.prepare("""
SELECT sp.product_id
FROM suseServerInstalledProduct sip
JOIN suseInstalledProduct ip ON sip.suse_installed_product_id = ip.id
JOIN suseProducts sp ON sp.name = LOWER(ip.name)
     AND (sp.version IS NULL OR sp.version = LOWER(COALESCE(ip.version, '')))
     AND (sp.release IS NULL OR sp.release = LOWER(COALESCE(ip.release, '')))
     AND (sp.arch_type_id IS NULL OR sp.arch_type_id = ip.arch_type_id)
WHERE sip.rhn_server_id = :server_id
""")

q_system_virtual_systems = rhnSQL.prepare("""
SELECT virtual_system_id from rhnVirtualInstance where host_system_id = :server_id and virtual_system_id is not NULL
""")

h = rhnSQL.prepare("""
SELECT s.id, s.org_id, s.name,
       (SELECT UUID FROM rhnVirtualInstance vi WHERE vi.virtual_system_id = s.id) vm_uuid,
       c.nrsocket cpus
from rhnServer s
left join rhnCpu c ON s.id = c.server_id
order by s.org_id, s.id
""")
h.execute()
while 1:
    item = h.fetchone_dict()
    if not item:
        break
    if item['vm_uuid'] is None:
        item['is_virtual'] = False
    else:
        item['is_virtual'] = True
    q_system_products.execute(server_id=item['id'])
    item['product_ids'] = map(lambda x: x['product_id'], q_system_products.fetchall_dict() or [])
    q_system_virtual_systems.execute(server_id=item['id'])
    item['virtual_system_ids'] = map(lambda x: x['virtual_system_id'], q_system_virtual_systems.fetchall_dict() or [])
    result.append(item)

if options.outfile:
    with open(options.outfile, 'w') as f:
        if options.pretty:
            json.dump(result, f, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            json.dump(result, f, sort_keys=True)
else:
    if options.pretty:
        print json.dumps(result, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        print json.dumps(result, sort_keys=True)

