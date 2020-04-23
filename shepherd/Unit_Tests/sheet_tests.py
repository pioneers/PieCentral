import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))
import Sheet as sheet
import unittest

print(sheet.get_online_match(5))

def get_online_match(match_number):
	"""
	hello!
	>>> get_online_match(5)
	{'b1name': 'El Cerrito', 'b1num': '12', 'b2name': 'Hercules', 'b2num': '9', 'g1name': 'LPS Richmond', 'g1num': '4', 'g2name': 'Middle College', 'g2num': '6'}
	"""
	sheet.get_online_match(match_number)

class TestStringMethods(unittest.TestCase):

    def test_online(self):
    	match_five = {'b1name': 'El Cerrito', 'b1num': '12', 'b2name': 'Hercules', 'b2num': '9', 'g1name': 'LPS Richmond', 'g1num': '4', 'g2name': 'Middle College', 'g2num': '6'}
    	self.assertEqual(sheet.get_online_match(5), match_five)

if __name__ == '__main__':
    unittest.main()
