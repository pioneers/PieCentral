import unittest
from unnecessary_math import multiply
from upper import uppers

class TestUM(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_numbers_3_4(self):
        self.assertEqual( multiply(3,4), 12)
 
    def test_strings_a_3(self):
        self.assertEqual( multiply('a',3), 'aaa')

    def test_uppers_a_a(self):
        self.assertEqual( uppers('hello'), 'hello'.upper())



 
if __name__ == '__main__':
    unittest.main()
