#! /usr/bin/python

import csv
import re
import os
import os.path

Groups = {}
Unknown = []

recpu = re.compile(r'(\d+)\s*cpu')

def parseRow(row):
    product = None
    archs = None
    cpu = None      # I = Instance, <num>cpus, <num>ifls
    virt = "UV"     # UV = unlimited Virtualization, PHY
    stack = "N"     # N = non-stackable, S = Stackable
    support = "BS"  # BS = Basic, ST = Standard, PR = Priority

    desc = row['Long Item Description:'].lower()

    if " sap " in desc:
        product = "SLES4SAP"
        #print "SAP: %s" % desc
    elif " desktop " in desc:
        product = "SLED"
        #print "SLED: %s" % desc
    elif " expanded support " in desc or " rhel " in desc:
        product = "RES"
        #print "RES: %s" % desc
    elif "geo clustering" in desc:
        product = "SLE-HA-GEO"
        #print "SLE-HA-GEO: %s" % desc
    elif " high availability " in desc and "server & high" not in desc:
        product = "SLE-HA"
        #print "SLE-HA: %s" % desc
    elif " enterprise server " in desc and "server & high" not in desc:
        product = "SLES"
        #print "SLES: %s" % desc
    #else:
    #    print "unknown: %s" % desc

    a = []
    if "x86" in desc:
        a.append("x86")
    if "power" in desc:
        a.append("ppc")
    if "zseries" in desc or "system z" in desc:
        a.append("z")
    if "itanium" in desc:
        a.append("ia64")

    if "ppc" in a and len(a) == 1:
        stack = "S"
    if "ia64" in a and len(a) == 1:
        stack = "S"
    if "z" in a and len(a) == 1:
        stack = "S"

    if len(a) > 0:
        archs = '|'.join(a)

    if " hosted " in desc or " 1-Instance " in desc:
        cpu = "I"
    if recpu.search(desc):
        num = recpu.search(desc).groups()[0]
        cpu = num + "cpus"
        #print "CPUS: %s - %s" % (cpu, desc)
    if " ifl " in desc:
        cpu = "1ifls"

    if " phy" in desc:
        virt = "PHY"

    if "Priority" in desc:
        support = "PR"
    if "Standard" in desc:
        support = "ST"

    if product is None or archs is None or cpu is None:
        Unknown.append(row)
        return

    group = "%s-%s-%s-%s-%s-%s" % (product, archs, cpu, virt, stack, support)
    if not Groups.has_key(group):
        Groups[group] = []
    Groups[group].append(row['Item Number:'])

if not os.path.exists("./legacy_skus.csv"):
    os.system("wget http://w3.suse.de/~mc/SUSEManager/SKUs/legacy_skus.csv")

with open('./legacy_skus.csv', 'rb') as csvfile:
    skusreader = csv.DictReader(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
    for row in skusreader:
        #print "row: %s" % row
        parseRow(row)

cnt1 = 0
cnt2 = 0

for key,val in Groups.iteritems():
    print "%s:" % key
    for partnumber in val:
        print "    %s" % partnumber
        cnt1 += 1

print "UNKNOWN:"
for u in Unknown:
    print "%s: %s" % (u['Item Number:'], u['Long Item Description:'])
    cnt2 += 1

print "items in groups: %d" % cnt1
print "unknown items  : %d" % cnt2
