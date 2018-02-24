import random

# Codegen for the Shepherd module.
#
# See example:
#
# def example_usage2():
#     # Example: we have 4 rfids and 4 codes, one for each RFID.
#
#     codes = [1, 1, 1, 1] # Must be initialized with non-zero values
#     rfids = [123, 234, 345, 456] # The RFIDs. These shouldn't change.
#
#     # Generate the intial set of codes
#     get_new_code(rfids, codes, 0)
#     get_new_code(rfids, codes, 1)
#     get_new_code(rfids, codes, 2)
#     get_new_code(rfids, codes, 3)
#
#     # If we need to make a new code for a given RFID, we can just run this to update it:
#     get_new_code(rfids, codes, 2) # Make a new code for RFID #2
#
#     # All the answers for each (rfid, code) pair are unique.
#     assert(len(set(staff_decode(codes[i], rfids[i]) for i in range(len(codes)))) == len(codes))
#
# def alternate_usage():
#   # This was the original way to use the API. In this case, we want there to
#   # be just a single code for all the RFIDs, for which there can be any amount
#   # of challenge codes generated for all the RFIDs.
#
#   # RIFD, list and numbers can be any non-negative size
#   rfids = [1234, 2345, 3456, 4567, 5678, 6789]
#   codegen = Codegen(rfids)
#   challenge = codegen.generate_challenge(6) # Generate 6-digit-long codes
#
#   code = challenge.get_code()
#
#   # Send this to the students somehow...
#   send_code_to_student(code)
#
#   # We receive an answer from the students somehow...
#   answer = get_answer_from_student()
#
#   # Check if the student decoded the rfid correctly, and which one
#   report = challenge.check_rfid_answer(answer)
#
#   if report == -1:
#       print("Student decoded nothing or decoded incorrectly")
#   else:
#       print("Student decoded RFID " + str(rfids[report]))
#
#   # We can continue to generate more challenge codes as needed:
#   challenge2 = codegen.generate_challenge(20) # Generate 20-digit-long codes
#

class Codegen:
    '''
    A factory for `Challenge` instances, which are then used to check rfid
    '''

    def __init__(self, rfids, rand_seed=None):
        '''
        Manages the generated code and rfid-answer pairs.
        `rfids` must be an iterable of RFID ints.
        Duplicate RFIDs in the provided iterable are ignored.

        `rand_seed` is used to seed the random number generator, to
        allow reproducable tests and bugs. If None, no specific seed
        is used
        '''

        # Seed our local RNG
        self._random = random.Random(rand_seed)
        self._rfids = rfids

        if len(set(self._rfids)) != len(rfids):
            raise RuntimeError('The RFID list cannot contain duplicates!')

        # Generate function-related data
        self._decode_precompute = staff_decode_precompute(self._rfids)
        # True iff the given function is injective over the given RFID domain
        self._is_injective = {}

        # Apply every function to every rfid. This precomputation step
        # allows us to memoize the potentially expensive example solutions for the
        # student functions.
        for i in self._decode_precompute:
            outputs = set()
            injective = True
            for rfid in self._rfids:
                output = self._decode_precompute[i][rfid]
                if output in outputs:
                    injective = False
                else:
                    outputs.add(output)
            self._is_injective[i] = injective

    def generate_challenge(self, digit_len=5, func_distrib=None):
        '''
        Generate a Challenge instance to use during the competition for a
        single code.

        `func_distrib` is a map where the keys are digits and the values
        is the weight for that digit be picked whenever we need
        to pick a digit to use randomly. There is no need for
        the total weights to add up to one. If `func_distrib` is None,
        then a uniform distribution is used by default.

        >>> cg = Codegen([1234, 2345, 3456], 0)
        >>> c0 = cg.generate_challenge(20) # 20 digit code
        >>> c0.check_solution(c0.get_solution(1234))
        1234
        >>> c1 = cg.generate_challenge(5) # 5 digit code
        >>> c1.check_solution(c1.get_solution(2345))
        2345
        >>> c0 is c1
        False
        >>> c0.get_code() == c1.get_code()
        False
        '''
        # Generate a uniform distribution if None is provided
        if func_distrib is None:
            func_distrib = {}
            for i in self._decode_precompute:
                if i == 0:
                    func_distrib[i] = 0
                    continue
                func_distrib[i] = 1
        injective_funcs_distr = _helper_filter_map(func_distrib, self._is_injective)
        return Challenge(self._random, self._rfids,
                         func_distrib, injective_funcs_distr,
                         digit_len, self._decode_precompute)

class Challenge:

    def __init__(self, rand_gen, rfids, func_distrib,
                 injective_funcs_distr, digit_len, decode_precompute):
        '''
        This class should not be instantiated directly! Use the factory Codegen
        above!
        '''

        self._rfids = rfids

        # Keep generating random codes until we get one that gives a one-to-one
        # mapping between RFIDs and answers
        hgouc = _helper_generate_potentially_unsafe_code
        while True:
            self._rfid_to_ans = {}
            self._ans_to_rfid = {}
            self._code = hgouc(rand_gen, func_distrib, injective_funcs_distr, digit_len)
            # We want there to be a one-to-one mapping between RFIDs and answers
            # Therefore only break the loop if we randomly generate a code
            # that produces unique answers for every RFID in the list
            duplicate_answers = False
            for rfid in self._rfids:
                solution = staff_decode(self._code, rfid, decode_precompute)
                if solution in self._ans_to_rfid:
                    duplicate_answers = True
                    break
                self._ans_to_rfid[solution] = rfid
                self._rfid_to_ans[rfid] = solution
            if not duplicate_answers:
                break
            print('Duplicates!')

        # This is always true since we guaranteed above that
        # the (rfid --> solution) mapping is injective
        assert len(self._rfid_to_ans) == len(self._ans_to_rfid)

    def check_solution(self, solution):
        '''
        Returns which RFID that the solution corresponds to
        return None if it doesn't match any.
        '''
        return self._ans_to_rfid.get(solution, None)

    def get_code(self):
        '''
        Get the challenge code to be sent to students
        '''
        return self._code

    def get_rfids(self):
        '''
        Get a copy of the internal list of RFIDs.
        >>> cg = Codegen([12345, 23456, 34567], 0)
        >>> c = cg.generate_challenge()
        >>> idx = c.check_rfid_answer(staff_decode(c.get_code(), 12345))
        >>> c.get_rfids()[idx]
        12345
        '''
        return list(self._rfids)

    def get_solution(self, rfid):
        '''
        Returns which solution that the RFID corresponds to
        return None if it doesn't match any.

        >>> cg = Codegen([1, 2, 3], 0)
        >>> c = cg.generate_challenge()
        >>> c.check_solution(c.get_solution(1))
        1
        >>> c.check_solution(c.get_solution(2))
        2
        >>> c.check_solution(c.get_solution(3))
        3
        '''
        return self._rfid_to_ans.get(rfid, None)

    def check_rfid_answer(self, student_answer):
        '''
        Returns one of the following:
        -   the index, idx, of the rfid in the `rfids` list for which
            staff_decode(self.get_code(), rfids[idx]) == student_answer
            is True
        -   the error code -1 iff the above is not possible
        >>> r = [31415, 12345, 14916, 77777]
        >>> cg = Codegen(r, 0)
        >>> c = cg.generate_challenge()
        >>> c.check_rfid_answer(staff_decode(c.get_code(), r[0]))
        0
        >>> c.check_rfid_answer(staff_decode(c.get_code(), r[1]))
        1
        >>> c.check_rfid_answer(staff_decode(c.get_code(), r[2]))
        2
        >>> c.check_rfid_answer(staff_decode(c.get_code(), r[3]))
        3
        >>> c.check_rfid_answer(0)
        -1
        >>> c.check_rfid_answer(12345)
        -1
        '''

        corresponding_rfid = self.check_solution(student_answer)
        if corresponding_rfid is None:
            return -1
        idx = -1
        for i in range(len(self._rfids)):
            if self._rfids[i] == corresponding_rfid:
                idx = i
                break
        if idx == -1:
            return -1
        assert staff_decode(self.get_code(), self._rfids[idx]) == student_answer
        return idx

def _helper_generate_potentially_unsafe_code(rand, func_distrib, injective_funcs_distr, digit_len):
    '''
    Helper function for this module.

    Clients should *not* use this function directly, as it makes no
    guarantees on the quality of the generated code. That responsibility
    belongs to the Codegen class above!

    Generates a code corresponding to a random sequence of
    concatenated functions for the students to decode and apply to RFID tags.
    See student_decode() below.
    '''
    if digit_len < 1:
        return 0

    injective_digit = 0 # Use the fallback by default
    if injective_funcs_distr:
        injective_digit = _helper_pick_random(rand.uniform(0, 1), injective_funcs_distr)

    # Randomly generate the remaining digits
    code = 0
    for _ in range(digit_len - 1):
        code *= 10
        code += _helper_pick_random(rand.uniform(0, 1), func_distrib)
    code *= 10
    code += injective_digit

    return code

def _helper_filter_map(data_map, filter_map):
    '''
    Helper function for this module.

    Makes a copy of data_map that only includes keys contained in
    filter_map and only if filter_map[key] evaluates to True
    '''
    return {key : data_map[key] for key, to_keep in filter_map.items() if to_keep}


def _helper_pick_random(rand_normalized, weighted_choice_dict):
    '''
    Helper function for this module.

    Given a random number in the range [0.0, 1.0], pick a key from
    the provided dictionary where the values are weighted probabilities
    that that key will be picked. The total weight does not need to
    add to one.
    '''

    wcd = weighted_choice_dict

    fallback = wcd[next(iter(wcd.keys()))]

    total = 0
    for key in wcd:
        total += wcd[key]
    rand = rand_normalized * total

    for key in wcd:
        if rand <= wcd[key]:
            return key
        rand -= wcd[key]
    return fallback


# Various ideas for functions for the students
# Included are example student implementations
# Of course, the example solutions are optimized
# for pedagogical simplicity, not runtime speed or memory

# Functions presented in no particular order of difficulty
# Both inputs and outputs guaranteed to be nonnegative integers

def next_power(num):
    '''
    The next biggest (whole) power of two

    >>> next_power(2)
    2
    >>> next_power(3)
    4
    >>> next_power(23)
    32
    >>> next_power(2557)
    4096
    >>> next_power(12510)
    16384
    >>> next_power(0)
    1
    '''
    solution = 1
    while solution < num:
        solution = solution * 2
    return solution
def reverse_digits(num):
    '''
    The number with digits reversed

    >>> reverse_digits(2)
    2
    >>> reverse_digits(3)
    3
    >>> reverse_digits(23)
    32
    >>> reverse_digits(2557)
    7552
    >>> reverse_digits(12510)
    1521
    >>> reverse_digits(0)
    0
    '''
    solution = 0
    while num > 0:
        solution = solution * 10
        solution = solution + (num % 10)
        num = num // 10
    return solution
def smallest_prime_fact(num):
    '''
    Smallest prime factor

    >>> smallest_prime_fact(2)
    2
    >>> smallest_prime_fact(3)
    3
    >>> smallest_prime_fact(3127)
    53
    >>> smallest_prime_fact(2557)
    2557
    >>> smallest_prime_fact(1251)
    3
    >>> smallest_prime_fact(0)
    0
    >>> smallest_prime_fact(1)
    1
    '''
    for i in range(2, num):
        if num % i == 0:
            return i
    return num
def prime_factor(num):
    '''
    Output a concatenated sequence of prime factors

    >>> prime_factor(2)
    2
    >>> prime_factor(3)
    3
    >>> prime_factor(2 * 3)
    23
    >>> prime_factor(2 * 5 * 5 * 7)
    2557
    >>> prime_factor(12510)
    2335139
    >>> prime_factor(1)
    0
    '''
    solution = '0'
    while num > 1:
        for divisor in range(2, num + 1):
            if num % divisor == 0:
                solution = solution + str(divisor)
                num = num // divisor
                break
    return int(solution)
def silly_base_two(num):
    '''
    Convert to base two (with digits interpreted as if in base ten)

    >>> silly_base_two(2)
    10
    >>> silly_base_two(3)
    11
    >>> silly_base_two(3127)
    110000110111
    >>> silly_base_two(2557)
    100111111101
    >>> silly_base_two(1251)
    10011100011
    >>> silly_base_two(0)
    0
    '''
    output = 0
    place = 0
    while num > 0:
        bit = num % 2
        num = num // 2
        output += bit * (10 ** place)
        place += 1
    return output

def most_common_digit(num):
    '''
    Every digit in the input occurs N times. (exclude zero)
    Output the digit with the greatest N.
    (If there is a tie, use the largest digit)
    Return that digit

    Special case: 0 outputs 0

    >>> most_common_digit(2)
    2
    >>> most_common_digit(3)
    3
    >>> most_common_digit(3127)
    7
    >>> most_common_digit(2557)
    5
    >>> most_common_digit(1251)
    1
    >>> most_common_digit(111222333444)
    4
    >>> most_common_digit(314159265358979324)
    9
    >>> most_common_digit(0)
    0
    '''
    counts = {}
    for digit in range(0, 10):
        counts[digit] = 0
    while num > 0:
        digit = num % 10
        num = num // 10
        counts[digit] += 1
    output = 0
    biggest_count = 1
    for digit in range(1, 10):
        if counts[digit] >= biggest_count:
            biggest_count = counts[digit]
            output = digit
    return output
def valid_isbn_ten(num):
    '''
    ISBN-10 validation: Check that the given ISBN-10 number is valid.
    Return the number if it is valid, or the next integer after which is valid.
    Use only the bottom 10 digits if the input is longer than 10 digits.
    Use zeros in place of missing digits if the input is shorter than 10 digits.

    >>> valid_isbn_ten(2)
    19
    >>> valid_isbn_ten(3)
    19
    >>> valid_isbn_ten(128122765)
    128122765
    >>> valid_isbn_ten(128122760)
    128122765
    >>> valid_isbn_ten(60)
    78
    >>> valid_isbn_ten(123456788)
    123456789
    '''
    valid = False
    while not valid:
        total = 0
        digit_list = num
        for i in range(0, 10):
            digit = digit_list % 10
            digit_list = digit_list // 10
            total += digit * (10 - i)
        valid = total % 11 == 0
        if not valid:
            num += 1
    return num
def simd_four_square(num):
    '''
    Evenly divide the input digits into four groups, treating each group as if
    it were its own integer. Square each group, and then rejoin the squared
    integers into a single value such that the total number of digits within
    each group is preserved. If the number of input digits is not evenly
    divisible by four, pad the left of the input with as few zeros necessary
    until the input digit count is evenly divisble by four.

    >>> simd_four_square(3210)
    9410
    >>> simd_four_square(11121314)
    21446996
    >>> simd_four_square(54321) # treat as "00054321"
    254941
    >>> simd_four_square(0)
    0
    '''
    num_digits = 1
    while num // (10 ** num_digits) > 0:
        num_digits += 1

    if num_digits % 4 != 0:
        num_digits += 4 - (num_digits % 4)

    group_len = num_digits // 4

    output = 0

    for group_idx in [3, 2, 1, 0]:
        group = (num // (10 ** (group_idx * group_len))) % (10 ** group_len)
        squared = (group * group) % (10 ** group_len)
        output *= 10 ** group_len
        output += squared

    return output
def double_caesar_cipher(key):
    '''
    Use the given input as a double-caesar-cipher encryption key for the first
    ten digits of pi. If the key is not long enough, reuse it to encrypt the
    unencrypted digits, starting from the least significant digit.

    >>> double_caesar_cipher(0)
    3141592653
    >>> double_caesar_cipher(1)
    4252603764
    >>> double_caesar_cipher(9677799275)
    2718281828
    >>> double_caesar_cipher(10000000000)
    3141592653
    >>> double_caesar_cipher(3141592653)
    6282084206
    >>> double_caesar_cipher(12136)
    4354104789
    >>> double_caesar_cipher(969518457)
    0
    >>> double_caesar_cipher(123)
    6264615776
    '''
    msg = 3141592653
    pi_str = str(msg)
    key_str = str(key)
    # expand key_str to be at least as long as pi_str
    key_str *= (len(pi_str) // len(key_str)) + 1
    result = ''
    for i in range(len(pi_str)):
        ciph = (int(pi_str[-1 - i]) + int(key_str[-1 - i])) % 10
        result = str(ciph) + result
    return int(result)

def memoize(func):
    '''
    Memoizes a function
    '''
    cache = {}
    def memoized(*args):
        nonlocal cache
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return memoized

@memoize
def limit_input_to(limit):
    '''Generate a function to limit size of inputs'''
    def retval(input_val):
        while input_val > limit:
            input_val = (input_val % limit) + (input_val // limit)
        return input_val
    return retval

@memoize
def compose_funcs(func_a, func_b):
    '''
    Composes two single-input functions together, A(B(x))
    '''
    def composed(input_x):
        return func_a(func_b(input_x))
    return composed


def identity(x):
    '''
    Used only in the (hopefully) rare event that none of the other
    functions are bijections with a given domain of RFIDs
    '''
    return x

def get_function_mapping():
    '''
    Returns a dictionary that maps code digits to the function to run
    on the RFID values. Always returns values which are equal to each other
    by value. It is safe to mutate the return value.
    >>> get_function_mapping() == get_function_mapping()
    True
    '''

    func_map = {}
    func_map[0] = identity
    func_map[1] = next_power
    func_map[2] = reverse_digits
    func_map[3] = compose_funcs(smallest_prime_fact, limit_input_to(1000000))
    func_map[4] = double_caesar_cipher
    func_map[5] = silly_base_two
    func_map[6] = most_common_digit
    func_map[7] = valid_isbn_ten
    func_map[8] = simd_four_square

    return func_map

def staff_decode_precompute(rfids):
    '''
    To speed up calls to staff_decode over the same domain of known RFIDs, we
    can run this precomputation and pass the return value to the `staff_decode`
    function as the `precompute` argument.

    Returns a dictionary of dictionaries, where the first-level key is the digit
    corresponding with that student function, and the second-level key is the
    rfid we wish to evalute the student function on.
    '''
    applied_map = {} # Precomputation to use for speeding up staff_decode calls
    func_map = get_function_mapping()

    # Apply every function to every rfid. This precomputation step
    # allows us to memoize the potentially expensive example solutions for the
    # student functions.
    for i in func_map:
        applied_map[i] = {}
        for rfid in rfids:
            applied_map[i][rfid] = func_map[i](rfid)
    return applied_map

def staff_decode(challenge_code, rfid_seed, precompute=None):
    '''
    Staff solution for the student decoder. Takes as input a code and the data
    collected by an RFID scanner, and outputs the result of applying the
    encoded functions onto that RFID "seed".
    '''
    if precompute is None:
        func_map = get_function_mapping()

    code = challenge_code
    output = ''
    while code > 0:
        digit = code % 10
        code //= 10

        if precompute is None:
            result = func_map[digit](rfid_seed)
        else:
            result = precompute[digit][rfid_seed]

        output += str(result)
    output = int(output)
    random.seed(output)
    output = str(random.randint(1000, 9999))
    final_output = 0
    for i in output:
        final_output = final_output * 10 + (int(i) % 5) + 1
    return final_output

def _debug_random_sample(sample_size, regenerate_rfids=False, seed=0):
    # Random sampling of codes, finds how frequent each digit is
    import time

    count = {}
    total = 0
    for i in range(0, 9):
        count[i] = 0
    cg = None
    rng = random.Random(seed)
    timer_begin = time.time()
    for i in range(0, sample_size):
        if regenerate_rfids or cg is None:
            rfids = [rng.randint(0, 999999999999999) for _ in range(0, 5)]
            cg = Codegen(rfids, rng.randint(0, 999999999999999))
        code = cg.generate_challenge().get_code()
        if i % (sample_size // 10) == 0:
            print(code)
        while code > 0:
            digit = code % 10
            code //= 10
            count[digit] += 1
            total += 1
    timer_end = time.time()
    for i in range(0, 9):
        count[i] /= total

    timer_dur = timer_end - timer_begin
    print('Took {} seconds total to generate {} code(s)'.format(timer_dur, sample_size))
    print('Took {} seconds avg. (mean) per code'.format(timer_dur / sample_size))
    if regenerate_rfids:
        print('!! Time also includes regenerating a new set of RFIDs for every code.')
    return count

def get_original_codes(rfids):
    '''
    Generates six identical codes that have no collisions in the solutions.
    '''
    gen = Codegen(rfids)
    challenge = gen.generate_challenge()
    code = challenge.get_code()
    solutions = [challenge.get_solution(rfid) for rfid in rfids]
    codes = [code for i in range(len(rfids))]
    return rfids, codes, solutions

def get_new_code(rfids, codes, index):
    '''
    Generates a new code for that index such that there are no collisions in the codes or solutions.

    >>> codes = [1, 1, 1, 1]
    >>> rfids = [123, 234, 345, 456]
    >>> _, _, _ = get_new_code(rfids, codes, 0)
    >>> _, _, _ = get_new_code(rfids, codes, 1)
    >>> _, _, _ = get_new_code(rfids, codes, 2)
    >>> _, _, _ = get_new_code(rfids, codes, 3)
    >>> len(set(staff_decode(codes[i], rfids[i]) for i in range(len(codes)))) == len(codes)
    True
    '''
    solutions = []
    for i in range(len(codes)):
        solutions += [staff_decode(codes[i], rfids[i])]
    while True:
        gen = Codegen([rfids[index]])
        challenge = gen.generate_challenge()
        new_code = challenge.get_code()
        new_solution = challenge.get_solution(rfids[index])
        if (not new_solution in solutions) and (not new_code in codes):
            codes[index], solutions[index] = new_code, new_solution
            break
    return rfids, codes, solutions

if __name__ == "__main__":
    import doctest
    print("Performing doctests...")
    print(doctest.testmod())
