import csv

def r(filename):
    """
    Read the configuration information given in 'filename'
    Handle all IO Exceptions
    Fill out self.deviceParams and self.version

    Config file format:
    deviceID1, deviceName1, param1, param2, ...
    deviceID2, deviceName2, param1, param2, ...

    self.deviceParams format:
    self.deviceParams = {deviceID : (param1, param2, ...)}

    self.version format:
    self.version = <string repr of version info>
    """
    csv_file = open('hibikeDevices.csv', 'r')
    reader = csv.reader(csv_file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    list_of_rows = [row for row in reader]
    #print(list_of_rows)
    csv_file.close()
    return {lst[0]: [elem for elem in lst[1:] if elem != ''] for lst in list_of_rows}

print(r())
