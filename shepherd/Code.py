import random
import math
import numpy as np
from Utils import *

codes = []
solutions = []
code_solution = {}
code_effect = {}

def generate_code(code_list):
    '''
    Take a list of codes that return a new random code
    '''
    temp = np.random.permutation(10)
    num = 0
    for a in temp:
        num = num * 10 + a
    while num in code_list:
        temp = np.random.permutation(10)
        num = 0
        for a in temp:
            temp = temp * 10 + a
    return num


def decode(code):
    '''
    Call all functions
    '''
    one = tennis_ball(code)
    two = remove_duplicates(one)
    three = rotate(two)
    four = next_fib(three)
    five = most_common(four)
    final = get_coins(five)
    return final

def assign_code_solution():
    '''
    Generate 16 codes and create a code_solution dictionary
    '''
    codes.clear()
    solutions.clear()
    code_solution.clear()
    code_effect.clear()
    for i in range(16):
        # pylint: disable=assignment-from-no-return
        new_code = generate_code(codes)
        codes.append(new_code)
    for code in codes:
        solutions.append(decode(code))
    for i in range(16):
        code_solution[codes[i]] = solutions[i]
    return code_solution

def assign_code_effect():
    '''
    Assign each code to a random effect
    '''
    for i in range(16):
        code_effect[codes[i]] = (EFFECTS.TWIST if random.random() <
                                 CONSTANTS.TWIST_CHANCE else
                                 EFFECTS.SPOILED_CANDY)
    return code_effect

def rotate(numbers):
    copy = numbers
    max_num = 0
    while copy:
        num = copy % 10
        copy = copy // 10
        size = math.log(numbers)//math.log(10)
        max_num = num if num > max_num else max_num
    for _ in range(max_num):
        lsd = numbers % 10
        numbers = numbers // 10
        msd = (lsd) * 10**(size)
        numbers = numbers + msd
    return int(numbers)

def tennis_ball(num):
    index = 5
    while index > 0:
        if num % 3 == 0:
            num = num // 3
        elif num % 2 == 1:
            num = num * 4 + 2
        else:
            num += 1
        index -= 1
    return num

def most_common(num):
    parse = []
    while num != 0:
        parse.append(num % 10)
        num = num // 10
    parse.reverse()
    l = list(set(parse))
    if len(l) <= 4:
        l = sorted(l, reverse=True)
    else:
        ret = []
        d = {}
        for n in parse:
            if n in d.keys():
                d[n] += 1
            else:
                d[n] = 1
        final = []
        boolean = {}
        print(d)
        for key, _ in sorted(d.items(), key=lambda kv: kv[1], reverse=True):
            final.append(key)
            boolean[key] = False
        print(final)
        boolean[final[3]] = True
        for key in final:
            if d[key] == d[final[3]]:
                boolean[key] = True
        for i in range(4):
            if not boolean[final[i]]:
                ret.append(final[i])
        print(ret)
        left = 4 - len(ret)
        print(left)
        if left != 0:
            for i in range(len(parse)):
                if boolean[parse[i]] and parse[i] not in ret:
                    print(parse[i])
                    ret.append(parse[i])
                    left -= 1
                    if left == 0:
                        break
        l = sorted(ret, reverse=True)
    final_num = 0
    while l != []:
        final_num = final_num * 10 + l[0]
        l = l[1:]
    return final_num

def remove_duplicates(num):
    l = []
    while num > 0:
        l = [num % 10] + l
        num = num // 10
    final = []
    for i in range(len(l)):
        y = 0
        exist = False
        while y < i:
            if l[i] == l[y]:
                exist = True
            y += 1
        if not exist:
            final = [l[i]] + final
    n = 0
    while final != []:
        n = 10 * n + final[-1]
        final = final[:-1]
    return n

def next_fib(num):
    first = 0
    second = 1
    total = 0
    if num == 0:
        return 0
    for _ in range(num):
        total = first + second
        if total >= num:
            return total
        first = second
        second = total
    return total

def get_coins(num):
    quarters = num // 25
    nickels = (num - 25 * quarters) // 5
    pennies = num - nickels * 5 - quarters * 25
    return int(str(quarters) + str(nickels) + str(pennies))
