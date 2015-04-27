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

class BaseParser:
    def __init__(self):
        self.partnumber = None
        self.description = None
        self.unknown = False

        self.cpu = None      # I = Instance, <num>cpus, <num>ifls
        self.virt = "UV"     # UV = unlimited Virtualization, PHY = physical, 2=2 = 2 Sockets or 2 Virtual, INH = inherit
        self.stack = "N"     # N = non-stackable, S = Stackable
        self.support = "BS"  # BS = Basic, ST = Standard, PR = Priority, INH = inherit, L3PR = vendor priority, L3ST = vendor standard
        self.quantityFactor = None

    def isUnknown(self):
        return self.unknown

    def parse(self, pnum, descr):
        self.partnumber = pnum
        self.description = descr.lower()

        if not self.partnumber or self.partnumber == "N/A":
            self.unknown = True
            return
        # ignore bundels. Needs special handling
        if self.partnumber in ('051-004968','051-004972','051-004969',
                    '051-004970','051-004971','874-006862','876-000258',
                    '874-006713', '873-010151', '877-006629'):
            self.unknown = True
            return {'pnum': self.partnumber, 'desc': self.description}

        # arch needed as indicator for stacking
        a = []
        if ("x86" in self.description or
            "amd64" in self.description):
            a.append("x86")
        if "power" in self.description:
            a.append("ppc")
        if ("zseries" in self.description or
            "system z" in self.description):
            a.append("z")
        if "itanium" in self.description:
            a.append("ia64")

        if "ppc" in a and len(a) == 1:
            self.stack = "S"
        if "ia64" in a and len(a) == 1:
            self.stack = "S"
        if "z" in a and len(a) == 1:
            self.stack = "S"

        if (" hosted " in self.description or
            " 1-instance " in self.description or
            " 1 instance" in self.description or
            " 1-device " in self.description or
            " 1 scom instance" in self.description or
            #" single instance" in self.description or # ???
            " additional instance" in self.description):
            self.cpu = "I"
            self.virt = "INST"
            self.stack = 'N'
        elif "1-2 sockets or 1-2 virtual" in self.description:
            self.cpu = "2"
            self.virt = "2=2"
        elif "socket pair" in self.description:
            self.cpu = 2
        elif "2 sockets or 2 virtual" in self.description:
            self.cpu = "2"
            self.virt = "2=2"
            self.stack = "S"
        elif recpu.search(self.description):
            num = recpu.search(self.description).groups()[0]
            self.cpu = num
            if "4 osd node" in self.description:
                self.quantityFactor = 4
            #print "CPUS: %s - %s" % (self.cpu, self.description)
        elif " ifl" in self.description:
            self.cpu = "1"
            self.virt = "UV"
        elif " 1 physical server" in self.description:
            self.cpu = "I"
            self.stack = "N"
        elif ("suse manager server" in self.description or
              "suse manager proxy" in self.description):
            self.cpu = "I"
            self.virt = "INST"
        elif ("suse manager management" in self.description or
              "suse manager provisioning" in self.description or
              "suse manager monitoring" in self.description or
              "suse manager lifecycle management" in self.description):
            self.cpu = "I"
            if "single instance" in self.description:
                # single instance for system entitlements was meant
                # really physical
                self.virt = "PHY"
        elif "per "in self.description and ("engine" in self.description or "socket" in self.description or "ifl" in self.description):
            self.cpu = 1
        elif " 1-2 instances" in self.description:
            self.cpu = "I"
            self.quantityFactor = 2


        if (" phy" in self.description or
            " for appliance " in self.description):
            self.virt = "PHY"
        elif " unlimited virtual machines" in self.description:
            self.virt = "UV"
        elif "inherited virtualization" in self.description:
            self.virt = "INH"

        if "l3-priority" in self.description:
            self.support = "L3PR"
        elif "priority" in self.description:
            self.support = "PR"
        elif "l3-standard" in self.description:
            self.support = "L3ST"
        elif "standard" in self.description:
            self.support = "ST"
        elif "inherited subscription" in self.description:
            self.support = "INH"

        if "long term service pack" in self.description:
            self.cpu = "I"
            self.virt = "INH"
            self.stack = "N"
            self.support = "INH"
            if "unlimited servers" in self.description:
                self.quantityFactor = -1
            elif "500 servers" in self.description:
                self.quantityFactor = 500
            elif "100 servers" in self.description:
                self.quantityFactor = 100
            elif "10 ifls" in self.description:
                self.quantityFactor = 10
            elif "5 ifls" in self.description:
                self.quantityFactor = 5
            elif "unlimited ifls" in self.description:
                self.quantityFactor = -1
            else:
                #print "Unknown self.quantityFactor for %s" % self.description
                self.cpu = None

        if self.cpu is None:
            self.unknown = True
            return {'pnum': self.partnumber, 'desc': self.description}

        obj = {"cpu": self.cpu,
               "virt": self.virt,
               "stack": self.stack,
               "supp": self.support,
               "pnum": self.partnumber,
               "desc": self.description,
               "quantityFactor": self.quantityFactor}
        if self.cpu == "I":
            obj["cpu"] = None

        return obj


class OldSubscriptionParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self.cpu = None      # I = Instance, <num>cpus, <num>ifls
        self.virt = "UV"     # UV = unlimited Virtualization, PHY = physical, 2=2 = 2 Sockets or 2 Virtual, INH = inherit
        self.stack = "N"     # N = non-stackable, S = Stackable
        self.support = "BS"  # BS = Basic, ST = Standard, PR = Priority, INH = inherit, L3PR = vendor priority, L3ST = vendor standard
        self.quantityFactor = None

class NewSubscriptionParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self.cpu = None      # I = Instance, <num>cpus, <num>ifls
        self.virt = "PHY"    # UV = unlimited Virtualization, PHY = physical, 2=2 = 2 Sockets or 2 Virtual, INH = inherit, INST = Instance
        self.stack = "S"     # N = non-stackable, S = Stackable
        self.support = "BS"  # BS = Basic, ST = Standard, PR = Priority, INH = inherit
        self.quantityFactor = None

ParsedItems = dict()
ParsedObjects = list()
ParsedUnknown = list()


if not os.path.exists("./legacy_skus.csv"):
    os.system("wget http://w3.suse.de/~mc/SUSEManager/SKUs/legacy_skus.csv")
if not os.path.exists("./ihv_isv.csv"):
    os.system("wget http://w3.suse.de/~mc/SUSEManager/SKUs/ihv_isv.csv")

with open('./ihv_isv.csv', 'rb') as csvfile:
    skusreader = csv.DictReader(csvfile, delimiter=',')
    for row in skusreader:
        pnum = row['Part Number']
        if pnum in ParsedItems:
            # duplicate
            continue
        #print "row: %s" % row
        nsp = NewSubscriptionParser()
        item = nsp.parse(pnum, row['Product Description'])
        if not item:
            continue
        ParsedItems[pnum] = item
        if nsp.isUnknown():
            ParsedUnknown.append(item)
        else:
            ParsedObjects.append(item)

with open('./legacy_skus.csv', 'rb') as csvfile:
    skusreader = csv.DictReader(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
    for row in skusreader:
        pnum = row['Item Number:']
        if pnum in ParsedItems:
            # duplicate
            continue
        #print "row: %s" % row
        osp = OldSubscriptionParser()
        item = osp.parse(pnum, row['Long Item Description:'])
        if not item:
            continue
        ParsedItems[pnum] = item
        if osp.isUnknown():
            ParsedUnknown.append(item)
        else:
            ParsedObjects.append(item)

od = collections.OrderedDict(sorted(Groups.items(), key=lambda t: t[0]))

templateLoader = jinja2.FileSystemLoader( searchpath="./" )
templateEnv = jinja2.Environment( loader=templateLoader, trim_blocks=True, lstrip_blocks=True )
template = templateEnv.get_template("./PartNumbers.drl.jinja")

template.stream(obj=ParsedObjects).dump("./PartNumbers.drl")


if printUnknown:
    print "UNKNOWN:"
    for u in ParsedUnknown:
        print "%s: %s" % (u['pnum'], u['desc'])

print "parsed items : %d" % len(ParsedObjects)
print "unknown items: %d" % len(ParsedUnknown)
