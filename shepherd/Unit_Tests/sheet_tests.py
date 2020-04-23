import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))
import Sheet as sheet
import Utils
import unittest

print(sheet.get_online_match(5))

class TestStringMethods(unittest.TestCase):

    def test_online(self):
    	match_5 = {'b1name': 'El Cerrito', 'b1num': '12', 'b2name': 'Hercules', 'b2num': '9', 'g1name': 'LPS Richmond', 'g1num': '4', 'g2name': 'Middle College', 'g2num': '6'}
    	match_24 = {'b1name': 'El Cerrito', 'b1num': '12', 'b2name': 'Albany', 'b2num': '1', 'g1name': 'REALM', 'g1num': '29', 'g2name': 'Encinal', 'g2num': '20'}
    	self.assertEqual(sheet.get_online_match(5), match_5)
    	self.assertEqual(sheet.get_online_match(24), match_24)

if __name__ == '__main__':
	Utils.CONSTANTS.SPREADSHEET_ID = Utils.CONSTANTS.TESTING_SPREADSHEET_ID
	unittest.main()
