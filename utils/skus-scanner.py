#! /usr/bin/python

import csv
import re
import os
import os.path
import collections

import jinja2

printGroups = True
printUnknown = True

Groups = {}
Partnumbers = {}
Unknown = []
Obj = []

recpu = re.compile(r'(\d+)\s*(cpu|socket)')

def parseRow(row):
    cpu = None      # I = Instance, <num>cpus, <num>ifls
    virt = "UV"     # UV = unlimited Virtualization, PHY = physical, 2=2 = 2 Sockets or 2 Virtual, INH = inherit
    stack = "N"     # N = non-stackable, S = Stackable
    support = "BS"  # BS = Basic, ST = Standard, PR = Priority, INH = inherit, L3PR = vendor priority, L3ST = vendor standard
    quantityFactor = None

    desc = row['Long Item Description:'].lower()
    pnum = row['Item Number:']

    if pnum in Partnumbers:
        # duplicate
        return

    # ignore bundels. Needs special handling
    if pnum in ('051-004968','051-004972','051-004969',
                '051-004970','051-004971','874-006862','876-000258',
                '874-006697', '874-006713'):
        Unknown.append(row)
        return

    # arch needed as indicator for stacking
    a = []
    if ("x86" in desc or
        "amd64" in desc):
        a.append("x86")
    if "power" in desc:
        a.append("ppc")
    if ("zseries" in desc or
        "system z" in desc):
        a.append("z")
    if "itanium" in desc:
        a.append("ia64")

    if "ppc" in a and len(a) == 1:
        stack = "S"
    if "ia64" in a and len(a) == 1:
        stack = "S"
    if "z" in a and len(a) == 1:
        stack = "S"


    if (" hosted " in desc or
        " 1-instance " in desc or
        " 1 instance " in desc or
        " 1-device " in desc):
        cpu = "I"
    elif "2 sockets or 2 virtual" in desc:
        cpu = "2"
        virt = "2=2"
        stack = "S"
    elif recpu.search(desc):
        num = recpu.search(desc).groups()[0]
        cpu = num
        #print "CPUS: %s - %s" % (cpu, desc)
    elif " ifl " in desc:
        cpu = "1"
    elif ("suse manager server" in desc or
          "suse manager proxy" in desc):
        cpu = "I"
    elif ("suse manager management" in desc or
          "suse manager provisioning" in desc or
          "suse manager monitoring" in desc or
          "suse manager lifecycle management" in desc):
        cpu = "I"
        if "single instance" in desc:
            virt = "PHY"

    if (" phy" in desc or
        " for appliance " in desc):
        virt = "PHY"
    elif "inherited virtualization" in desc:
        virt = "INH"

    if "priority" in desc:
        support = "PR"
    elif "standard" in desc:
        support = "ST"
    elif "inherited subscription" in desc:
        support = "INH"

    if "long term service pack" in desc:
        cpu = "I"
        virt = "INH"
        stack = "N"
        support = "INH"
        if "unlimited servers" in desc:
            quantityFactor = -1
        elif "500 servers" in desc:
            quantityFactor = 500
        elif "100 servers" in desc:
            quantityFactor = 100
        elif "10 ifls" in desc:
            quantityFactor = 10
        elif "5 ifls" in desc:
            quantityFactor = 5
        elif "unlimited ifls" in desc:
            quantityFactor = -1
        else:
            #print "Unknown quantityFactor for %s" % desc
            cpu = None
            return

    if cpu is None:
        Unknown.append(row)
        return

    if cpu == "I":
        group = "I-%s-%s-%s" % (virt, stack, support)
        obj = {"cpu": None,
               "virt": virt,
               "stack": stack,
               "supp": support,
               "pnum": pnum,
               "desc": desc,
               "quantityFactor": quantityFactor}
    else:
        group = "%scpus-%s-%s-%s" % (cpu, virt, stack, support)
        obj = {"cpu": cpu,
               "virt": virt,
               "stack": stack,
               "supp": support,
               "pnum": pnum,
               "desc": desc,
               "quantityFactor": quantityFactor}

    Partnumbers[pnum] = obj
    if not Groups.has_key(group):
        Groups[group] = []
    Groups[group].append((pnum, desc))
    Obj.append(obj)

def parseRowNew(row):
    cpu = None      # I = Instance, <num>cpus, <num>ifls
    virt = "UV"     # UV = unlimited Virtualization, PHY = physical, 2=2 = 2 Sockets or 2 Virtual, INH = inherit
    stack = "S"     # N = non-stackable, S = Stackable
    support = "BS"  # BS = Basic, ST = Standard, PR = Priority, INH = inherit
    quantityFactor = None

    desc = row['Product Description'].lower()
    pnum = row['Part Number']

    if pnum in Partnumbers:
        # duplicate
        return

    # ignore bundels. Needs special handling
    #if pnum in (''):
    #    Unknown.append(row)
    #    return
    if "1-2 sockets or 1-2 virtual" in desc:
        cpu = "2"
        virt = "2=2"
    elif recpu.search(desc):
        num = recpu.search(desc).groups()[0]
        cpu = num
        #print "CPUS: %s - %s" % (cpu, desc)
    elif " ifl" in desc:
        cpu = "1"
    elif (" hosted " in desc or
        " 1-instance" in desc or
        " 1 instance" in desc or
        " 1-device" in desc or
        " 1 physical server" in desc or
        " 1 scom instance" in desc or
        " additional instance" in desc):
        cpu = "I"
    elif " 1-2 instances" in desc:
        cpu = "I"
        quantityFactor = 2

    if " unlimited virtual machines" in desc:
        virt = "UV"
    elif "inherited virtualization" in desc:
        virt = "INH"

    if "l3-priority" in desc:
        support = "L3PR"
    elif "priority" in desc:
        support = "PR"
    elif "l3-standard" in desc:
        support = "L3ST"
    elif "standard" in desc:
        support = "ST"
    elif "inherited subscription" in desc:
        support = "INH"

    if "long term service pack" in desc:
        cpu = "I"
        virt = "INH"
        stack = "N"
        support = "INH"
        if "unlimited servers" in desc:
            quantityFactor = -1
        elif "500 servers" in desc:
            quantityFactor = 500
        elif "100 servers" in desc:
            quantityFactor = 100
        elif "10 ifls" in desc:
            quantityFactor = 10
        elif "5 ifls" in desc:
            quantityFactor = 5
        elif "unlimited ifls" in desc:
            quantityFactor = -1
        else:
            #print "Unknown quantityFactor for %s" % desc
            cpu = None
            return

    if cpu is None:
        Unknown.append({'Item Number:': pnum,
                        'Long Item Description:': desc})
        return

    if cpu == "I":
        group = "I-%s-%s-%s" % (virt, stack, support)
        obj = {"cpu": None,
               "virt": virt,
               "stack": stack,
               "supp": support,
               "pnum": pnum,
               "desc": desc,
               "quantityFactor": quantityFactor}
    else:
        group = "%scpus-%s-%s-%s" % (cpu, virt, stack, support)
        obj = {"cpu": cpu,
               "virt": virt,
               "stack": stack,
               "supp": support,
               "pnum": pnum,
               "desc": desc,
               "quantityFactor": quantityFactor}

    Partnumbers[pnum] = obj
    if not Groups.has_key(group):
        Groups[group] = []
    Groups[group].append((pnum, desc))
    Obj.append(obj)

if not os.path.exists("./legacy_skus.csv"):
    os.system("wget http://w3.suse.de/~mc/SUSEManager/SKUs/legacy_skus.csv")
if not os.path.exists("./ihv_isv.csv"):
    os.system("wget http://w3.suse.de/~mc/SUSEManager/SKUs/ihv_isv.csv")


with open('./ihv_isv.csv', 'rb') as csvfile:
    skusreader = csv.DictReader(csvfile, delimiter=',')
    for row in skusreader:
        #print "row: %s" % row
        parseRowNew(row)
with open('./legacy_skus.csv', 'rb') as csvfile:
    skusreader = csv.DictReader(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
    for row in skusreader:
        #print "row: %s" % row
        parseRow(row)

cnt1 = 0
cnt2 = 0
if printGroups:
    od = collections.OrderedDict(sorted(Groups.items(), key=lambda t: t[0]))

    templateLoader = jinja2.FileSystemLoader( searchpath="./" )
    templateEnv = jinja2.Environment( loader=templateLoader, trim_blocks=True, lstrip_blocks=True )
    template = templateEnv.get_template("./PartNumbers.drl.jinja")

    template.stream(obj=Obj).dump("./PartNumbers.drl")

    for key,val in od.iteritems():
        print "%s:" % key
        for tup in val:
            print "    %s: %s" % tup
            cnt1 += 1

if printUnknown:
    print "UNKNOWN:"
    for u in Unknown:
        print "%s: %s" % (u['Item Number:'], u['Long Item Description:'])
        cnt2 += 1

if printGroups:
    print "items in groups: %d" % cnt1
if printUnknown:
    print "unknown items  : %d" % cnt2
