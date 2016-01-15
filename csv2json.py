import sys
import json
import csv
from collections import OrderedDict
csv_file = open(sys.argv[1], 'r')
reader = csv.reader(csv_file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
def create_device(csv_row):
    device = OrderedDict()
    device['deviceID']       = csv_row[0]
    device['deviceName']     = csv_row[1]
    dataFormat     = csv_row[2]
    scalingFactors = [float(item.strip()) for item in csv_row[3].split(",") if item.strip()]
    machineNames   = [item.strip() for item in csv_row[4].split(",") if item.strip()]
    humanNames     = [item.strip() for item in csv_row[5].split(",") if item.strip()]

    device['dataFormat'] = OrderedDict([
        ("formatString",  dataFormat),
        ("parameters", [OrderedDict([("scalingFactor", s), ("machineName", m), ("humanName", h)]) for s, m, h in zip(scalingFactors, machineNames, humanNames)])
        ])
    device['params']         = [param for param in csv_row[6:] if param != '']
    return device

rows = [row for row in reader][1:]
output = {"devices":[create_device(row) for row in rows]}
print json.dumps(output, indent=4, separators=(',', ': '))