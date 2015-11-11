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

        self.unhandled = {
            '662644470924': 'opensuse 10.2 german',
            '877-000377': 'suse/zenworks linux management suite for ibm zseries and for ibm s/390 1-cpu (category 1: multiprise g5) 3-year maintenance',
            '873-010502': 'mono tools for visual academic shopnovell license',
            '873-010513': 'mono for android professional renewal',
            '811-122103-001': 'suse linux 10 strong encryption (128+ bit) japanese',
            '051-004961': 'sap royalty allocation for sles sap- us books',
            '662644473598': 'opensuse 11.1 dvd strong encryption (128+bit) english',
            '051-004626': 'opensuse professional ticket',
            '876-000589': 'libreoffice for windows fte academic license',
            '873-010516': 'mono for android academic',
            '051-004625': 'opensuse supporter ticket',
            '876-000592': 'libreoffice for windows fte school license',
            '662644471921': 'opensuse 10.3 german',
            '113-003085-001': 'mono tools for visual studio enterprise maintenance certificate',
            '876-000590': 'libreoffice for windows workstation academic license',
            '873-010501': 'mono touch academic shopnovell license',
            '873-010367': 'mono touch enterprise upgrade license',
            '873-010368': 'mono touch enterprise 5-pack upgrade license',
            'SEG1620': 'product segment 1620 suse products -general accounting use',
            'SEG1621': 'product segment 1621 suse linux enterprise server (sles) -general accounting use',
            '113-003104-001': 'novell se for enterprise linux-business class training voucher',
            '877-006625': 'mono tools for visual studio ultimate',
            '113-002664-001': 'suse linux enterprise mono extension for zseries license',
            '113-002280-001': 'education license certificate',
            '877-006624': 'mono tools for visual studio enterprise',
            '873-010512': 'mono for android for enterprise 5-pack',
            '873-010366': 'mono touch professional upgrade license',
            '051-004882': 'suse solid driver program level 1 membership 1-year',
            '873-010511': 'mono for android enterprise',
            '662644473604': 'opensuse 11.1 dvd strong encryption (128+bit) german',
            '877-006623': 'mono tools for visual studio professional',
            '051-004883': 'suse solid driver program level 2 membership 1-year',
            '051-004884': 'suse solid driver program level 3 membership 1-year',
            'ROY-005166': 'suse moblin royalty',
            '873-010510': 'mono for android professional',
            '873-010125': 'mono touch from novell corporate edition (5-developer license)',
            '061-000142': 'developer service & offerings open platform solutions ds1000',
            '051-003557': 'ximian mono maintenance',
            '873-010582': 'do not use - suse studio license (up to 2 instances)',
            '873-010124': 'mono touch from novell corporate edition',
            '874-006445': 'individual support for nomura - sles 9 sp3 for system z',
            'ROY-005165': 'suse moblin (includes fluendo codecs bundle)',
            '873-010123': 'mono touch from novell personal edition',
            '051-002690': 'ximian mono license',
            '051-004536': 'huawei hamsta test suite license + 3-year maintenance',
            '051-003556': 'microsoft for the translator',
            'ROY-005135': 'suse linux professional 9.2',
            'ROY-005107': 'suse linux enterprise server 9 internet commercial service provider license',
            '051-003449': 'suse custom engineering -t&m type',
            '051-003889': 'suse developer service program',
            'ROY-005168': 'suse linux enterprise desktop 90-day royalty',
            '061-000147': 'non-recurring engineering for ibm',
            '874-005217': 'SUSE Linux Enterprise Virtual Machine Driver Pack, x86-64, 1-4 Virtual Machines, Inherited Subscription, 1 Year',
            '874-005219': 'SUSE Linux Enterprise Virtual Machine Driver Pack, x86-64, Unlimited Virtual Machines, Inherited Subscription, 1 Year',
            '874-005218': 'SUSE Linux Enterprise Virtual Machine Driver Pack, x86-64, 1-4 Virtual Machines, Inherited Subscription, 3 Year',
            '874-005220': 'VMDP X86-64 ULVM INH S 3Y","SUSE Linux Enterprise Virtual Machine Driver Pack, x86-64, Unlimited Virtual Machines, Inherited Subscription, 3 Year',
            '874-005215': 'SUSE Linux Enterprise Virtual Machine Driver Pack (Unlimited Images; Inherited Subscription Level; 1 Year)',
            '874-005214': 'SUSE Linux Enterprise Virtual Machine Driver Pack (Up to 4 Virtual Images; Inherited Subscription Level; 3 Year)',
            '874-005213': 'SUSE Linux Enterprise Virtual Machine Driver Pack (Up to 4 Virtual Images; Inherited Subscription Level; 1 Year)',
            '877-001509': 'SUSE Linux Enterprise Virtual Machine Driver Pack Unlimited Images 1-Year Maintenance',
            '874-005216': 'SUSE Linux Enterprise Virtual Machine Driver Pack (Unlimited Images; Inherited Subscription Level; 3 Year)',
            '877-001507': 'SUSE Linux Enterprise Virtual Machine Driver Pack Up to 4 Virtual Images 1-Year Maintenance',
            '877-001510': 'SUSE Linux Enterprise Virtual Machine Driver Pack Unlimited Images 3-Year Maintenance',
            '877-001508': 'SUSE Linux Enterprise Virtual Machine Driver Pack Up to 4 Virtual Images 3-Year Maintenance'
            }

    def isUnknown(self):
        return self.unknown

    def parse(self, pnum, descr):
        self.partnumber = pnum
        self.description = descr.lower()

        if not self.partnumber or self.partnumber == "N/A":
            self.unknown = True
            return
        # no need to match these part numbers
        if self.partnumber in self.unhandled:
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
            #self.cpu = "I"
            # LTSS makes trouble. So we ignore them for now.
            self.cpu = None
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

ParsedObjects.sort(key=lambda obj: obj['pnum'])
template.stream(obj=ParsedObjects).dump("./PartNumbers.drl")


ParsedUnknown.sort(key=lambda obj: obj['pnum'])
if printUnknown:
    print "UNKNOWN:"
    for u in ParsedUnknown:
        print "%s: %s" % (u['pnum'], u['desc'])

print "parsed items : %d" % len(ParsedObjects)
print "unknown items: %d" % len(ParsedUnknown)
