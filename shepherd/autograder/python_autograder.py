from doctest import testmod
import challenges as ch

def convert_time(num):
    """
    >>> convert_time(0) # same as autograder (0)
    [12, 0]
    >>> convert_time(2) # one digit number (_)
    [12, 2]
    >>> convert_time(8) # random one digit number (_)
    [12, 8]
    >>> convert_time(49) # random two digit number (_._)
    [12, 49]
    >>> convert_time(55) # random two digit number (__)
    [12, 55]
    >>> convert_time(30) # two digit number ending in 0 (_0)
    [12, 30]
    >>> convert_time(40) # two digit number ending in 0 (_0)
    [12, 40]
    >>> convert_time(600) # three digit number ending in two 0’s (_00)
    [6, 0]
    >>> convert_time(400) # three digit number ending in two 0’s (_00)
    [4, 0]
    >>> convert_time(309) # (_0_)
    [3, 9]
    >>> convert_time(403) # (_0_)
    [4, 3]
    >>> convert_time(219) # random three digit number (_._._)
    [2, 19]
    >>> convert_time(328) # random three digit number (_._._)
    [3, 28]
    >>> convert_time(1249) # (12..)
    [12, 49]
    >>> convert_time(1221) # (12..)
    [12, 21]
    >>> convert_time(1341) # random four digit number
    [1, 41]
    >>> convert_time(1842) # random four digit number
    [6, 42]
    >>> convert_time(2310) # 23..
    [11, 10]
    >>> convert_time(2331) # 23..
    [11, 31]
    """
    return ch.convert_time(num)

def eta(pos):
    """
    >>> eta([5, 14]) # original position, same as autograder
    0
    >>> eta([-4, -2]) # negative coordinates
    6
    >>> eta([-3, -9]) # negative coordinates
    8
    >>> eta([7, 18]) # greater than 5 and 14
    1
    >>> eta([8, 19]) # greater than 5 and 14
    1
    >>> eta([4, 12]) # less than 5 and 14
    0
    >>> eta([3, 13]) # less than 5 and 14
    0
    >>> eta([4, 19]) # one lss and one greater
    1
    >>> eta([3, 20]) # one lss and one greater
    2
    """
    return ch.eta(pos)

def wacky_numbers(num):
    """
    >>> wacky_numbers(10) # random positive even number
    1249
    >>> wacky_numbers(12)
    24
    >>> wacky_numbers(-5) # random negative odd number
    -32
    >>> wacky_numbers(-15)
    -12
    >>> wacky_numbers(23) # random positive odd number
    2297
    >>> wacky_numbers(21)
    21498
    >>> wacky_numbers(-6) # random negative even number
    -12
    >>> wacky_numbers(-16)
    -1
    >>> wacky_numbers(0) # 0
    0
    """
    return ch.wacky_numbers(num)

def num_increases(num):
    """
    >>> num_increases(1) # not large enough to qualify
    0
    >>> num_increases(0) # not large enough to qualify
    0
    >>> num_increases(127) # basic test case of increasing sequence
    2
    >>> num_increases(468) # basic test case of increasing sequence
    2
    >>> num_increases(98431) # basic test case of decreasing sequence
    0
    >>> num_increases(76541) # basic test case of decreasing sequence
    0
    >>> num_increases(149325) # test a somewhat random sequence
    3
    >>> num_increases(346419) # test a somewhat random sequence
    3
    >>> num_increases(111111111) # flat test case
    0
    >>> num_increases(000000000) # flat test case
    0
    """
    return ch.num_increases(num)



def pie_cals_triangle(num):
    """
    >>> pie_cals_triangle(1) # small test
    15
    >>> pie_cals_triangle(2) # small test
    134
    >>> pie_cals_triangle(100) # large test
    1000202010900
    >>> pie_cals_triangle(101) # large test
    1061730343115
    >>> pie_cals_triangle(-1) # negative test
    -7
    >>> pie_cals_triangle(-3) # negative test
    819
    >>> pie_cals_triangle(0) # zero case
    0
    """
    return ch.pie_cals_triangle(num)

def road_trip(d):
    """
    >>> road_trip(0) # zero case
    0
    >>> road_trip(12) # small test
    11
    >>> road_trip(10) # small test
    10
    >>> road_trip(51) # medium test
    48
    >>> road_trip(65) # medium test
    65
    >>> road_trip(104) # large test
    102
    >>> road_trip(223) # large test
    219
    """
    return ch.road_trip(d)

def convertRoman(num):
    """
    >>> convertRoman(2) # number less than 4
    'II'
    >>> convertRoman(3)
    'III'
    >>> convertRoman(31) # two digit number without edge case
    'XXXI'
    >>> convertRoman(32)
    'XXXII'
    >>> convertRoman(45) # two digit number edge case
    'XLV'
    >>> convertRoman(47)
    'XLVII'
    >>> convertRoman(832) # three digit number
    'DCCCXXXII'
    >>> convertRoman(904) # three digit number
    'CMIV'
    >>> convertRoman(1952) # four digit number
    'MCMLII'
    >>> convertRoman(1624) # four digit number
    'MDCXXIV'
    """
    return ch.convertRoman(num)

if __name__ == '__main__':
    testmod(name ='convert_time', verbose = False)
    testmod(name ='eta', verbose = False)
    testmod(name ='wacky_numbers', verbose = False)
    testmod(name ='num_increases', verbose = False)

    testmod(name ='pie_cals_triangle', verbose = False)
    testmod(name ='road_trip', verbose = False)
    testmod(name ='convertRoman', verbose = False)
