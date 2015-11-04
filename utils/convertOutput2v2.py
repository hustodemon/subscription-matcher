#! /usr/bin/python

import sys
import argparse
import json

def renameKey(d, oldkey, newkey):
    if oldkey in d:
        d[newkey] = d.pop(oldkey)
    return d

def convertGhz(d):
    oldkey = "ghz"
    newkey = "cpuMhz"
    if oldkey in d:
        d[newkey] = (d.pop(oldkey) * 1000)
    return d

def main():

    parser = argparse.ArgumentParser(
        description='Convert gatherer output format v1 to v2')
    parser.add_argument(
        '-i', '--infile', action='store',
        help="json input file or '-' to read from stdin"
    )
    parser.add_argument(
        '-o', '--outfile', action='store',
        help='to write the output (json) file instead of stdout'
    )
    options = parser.parse_args()

    if options.infile == '-':
        gout = json.load(sys.stdin)
    else:
        with open(options.infile) as input_file:
            gout = json.load(input_file)
    if not gout:
        print "ERROR: no input file"
        sys.exit(1)

    for vhm in gout:
        for host in gout[str(vhm)]:
            renameKey(gout[str(vhm)][str(host)], "cores", "totalCpuCores")
            renameKey(gout[str(vhm)][str(host)], "sockets", "totalCpuSockets")
            renameKey(gout[str(vhm)][str(host)], "threads", "totalCpuThreads")
            renameKey(gout[str(vhm)][str(host)], "ram", "ramMb")
            convertGhz(gout[str(vhm)][str(host)])
            gout[str(vhm)][str(host)]["hostIdentifier"] = gout[str(vhm)][str(host)]["name"]
            gout[str(vhm)][str(host)]["type"] = "vmware"

    if options.outfile:
        with open(options.outfile, 'w') as out_file:
            json.dump(gout, out_file, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        print(json.dumps(gout, sort_keys=True, indent=4, separators=(',', ': ')))

# Start program
if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("-h")  # Display "help" by default.
    main()


