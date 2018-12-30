r"""
Runtime structured logging.

Example:
    The command-line tool ingests records from standard input to pretty-print
    them::

        $ echo '{
        >   "name": "runtime.journal",
        >   "level": 30,
        >   "pid": 460,
        >   "time": "Mon Apr 10 20:26:26 2017",
        >   "message": "Logging OK",
        >   "readings": [1.1, 1.2, 1.3],
        >   "context": {
        >     "mapping": {
        >       "083940": 129384
        >     }
        >   }
        > }' | tr '\n' ' ' | python -m runtime.journal

    This gives the following output::

        [Mon Apr 10 20:26:26 2017] WARN runtime.journal: Logging OK (pid=460)
          {
            "readings": [
              1.1,
              1.2,
              1.3
            ],
            "mappings": {
              "083940": 129384
            }
          }
"""

__all__ = ['initialize', 'make_logger', 'shutdown', 'make_colorizer', 'format_record']


from enum import IntEnum
import functools
import logging
import json
import platform
import sys
from typing import Callable, Tuple
import click

def wrap_log_method(name: str) -> Callable:
    """ Make a decorator that will wrap a logging method. """
    def wrapper(cls):
        @functools.wraps(getattr(cls, name))
        def log(self, *args, **context):
            method = getattr(super(cls, self), name)
            return method(*args, extra={'context': json.dumps(context)})
        setattr(cls, name, log)
        return cls
    return wrapper

@wrap_log_method('debug')
@wrap_log_method('info')
@wrap_log_method('warning')
@wrap_log_method('error')
@wrap_log_method('critical')
@wrap_log_method('exception')
@wrap_log_method('log')
class RuntimeLogger(logging.getLoggerClass()):
    """
    A logger that supports keyword arguments providing context.
    """


class RuntimeFormatter(logging.Formatter):
    REQUIRED_ATTRS = frozenset({'time', 'level', 'name', 'message', 'context'})
    DEFAULT_ATTRS = REQUIRED_ATTRS | frozenset({'pid', 'tid', 'host'})
    TEMPLATE = {'name': '"%(name)s"', 'time': '"%(asctime)s"',
                'host': f'"{platform.node()}"', 'message': '"%(message)s"',
                'level': '%(levelno)s', 'level_name': '"%(levelname)s"',
                'pid': '%(process)d', 'process_name': '"%(processName)s"',
                'tid': '%(thread)d', 'thread_name': '"%(threadName)s"',
                'module': '"%(module)s"', 'func': '"%(funcName)s"',
                'path': '"%(pathname)s"', 'lineno': '%(lineno)d',
                'context': '%(context)s'}

    def __init__(self, attrs: frozenset = None):
        self.attrs = (attrs or self.DEFAULT_ATTRS) | self.REQUIRED_ATTRS
        pairs = (f'"{attr}": {value}' for attr, value in self.TEMPLATE.items()
                 if attr in self.attrs)
        fmt = '{' + ', '.join(pairs) + '}'
        super().__init__(fmt)

    def formatException(self, exc_info):
        return ''  # TODO

    def format(self, record):
        record.msg = str(record.msg).replace('"', r'\"').replace('\n', '').replace(r'\x', r'\\x')
        if not hasattr(record, 'context'):
            record.context = {}
        return super().format(record)


def initialize(level: str):
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RuntimeFormatter())
    root_logger.addHandler(handler)
    root_logger.debug('Initialized root logger handler.')


def make_logger(name: str) -> RuntimeLogger:
    if logging.getLoggerClass() is not RuntimeLogger:
        logging.setLoggerClass(RuntimeLogger)
    logger = logging.getLogger(name)
    logger.propagate = True
    logger.debug('Initialized logger.')
    return logger


def terminate():
    logging.shutdown()


ESCAPE = '\x1b['

class ConsoleCode(IntEnum):
    """
    See `man console_codes` for more information.
    """
    RESET = 0
    BOLD, HALF, NORMAL = 1, 2, 22  # Intensity
    UNDERLINE_ON, UNDERLINE_OFF = 4, 24
    BLINK_ON, BLINK_OFF = 5, 25
    BLACK_FG, BLACK_BG = 30, 40
    RED_FG, RED_BG = 31, 41
    GREEN_FG, GREEN_BG = 32, 42
    BROWN_FG, BROWN_BG = 33, 43
    BLUE_FG, BLUE_BG = 34, 44
    MAGENTA_FG, MAGENTA_BG = 35, 45
    CYAN_FG, CYAN_BG = 36, 46
    WHITE_FG, WHITE_BG = 37, 47


def make_console_codes(*codes: ConsoleCode) -> str:
    return f'{ESCAPE}{";".join(str(code.value) for code in codes)}m'


def make_colorizer(use_color: bool) -> Callable[[str, ConsoleCode, bool], str]:
    if use_color:
        def colorize(message, color, bold=True):
            codes = ((color,) if color else ())
            codes += ((ConsoleCode.BOLD,) if bold else ())
            return (f'{make_console_codes(*codes)}{message}'
                    f'{make_console_codes(ConsoleCode.RESET)}')
        return colorize
    return lambda message, color, bold=True: message


def separate_optional_attrs(record: dict) -> Tuple[dict, dict]:
    primitives, objs = {}, {}
    for attr, value in record.items():
        if attr not in RuntimeFormatter.REQUIRED_ATTRS:
            if isinstance(value, (dict, list)):
                objs[attr] = record[attr]
            else:
                primitives[attr] = record[attr]
    return primitives, objs


def format_primitives(primitives: dict) -> str:
    """
    Example:

        >>> print(format_primitives({"a": "b"}))
        a='b'
        >>> print(format_primitives({"a": 1.2}))
        a=1.2
    """
    return ', '.join(f'{key}={repr(value)}' for key, value in primitives.items())


def format_objs(objs: dict, indent: int) -> str:
    """
    Example:

        >>> print(format_objs({"mapping": {"123": 456}}, 2))
          {
            "mapping": {
              "123": 456
            }
          }
    """
    lines = json.dumps(objs, indent=indent).split('\n')
    return '\n'.join(indent*' ' + line for line in lines)


def format_record(record: dict, options: dict, colorize: Callable) -> str:
    formatted_levels = {
        logging.DEBUG: colorize('DEBUG', ConsoleCode.WHITE_FG),
        logging.INFO: colorize('INFO', ConsoleCode.CYAN_FG, bold=False),
        logging.WARNING: colorize('WARN', ConsoleCode.MAGENTA_FG, bold=False),
        logging.ERROR: colorize('ERROR', ConsoleCode.BROWN_FG),
        logging.CRITICAL: colorize('CRIT', ConsoleCode.RED_FG),
    }

    level = record['level']
    components = [
        '[' + record['time'] + ']',
        formatted_levels.get(level, '{:>5}'.format(level)),
        record['name'] + ':',
        colorize(record['message'], ConsoleCode.CYAN_FG, bold=False),
    ]

    record.update(record['context'])
    primitives, objs = separate_optional_attrs(record)
    if primitives:
        components.append('(' + format_primitives(primitives) + ')')
    message = ' '.join(components)
    if objs:
        message += '\n' + format_objs(objs, options.get('indent', 2))
    return message
    

################################## command-line tool for filtering logs ##########################

def skip_literal(cmd_str: str, i: int) -> int:
    """
    Skips a string literal that ends at index i
    in the command string. Return the index of
    the front of the string literal
    
    Doctests:
    >>> skip_literal('\"name\"', 4)
    0
    >>> skip_literal('name == \"runtime.journal\"', 23)
    8
    """
    while cmd_str[i - 1] != '\"':
        i -= 1
    return i - 1
    

def replace_field_name(cmd_str: str, i: int) -> (str, int):
    """
    Takes a command string and an index of the command string i
    which contains the end of a field name in the command string
    and replaces it with record['<field_name>']. Takes care of
    referring to record['<field_name1>']['<field_name2>'] as
    field_name1.field_name2 in command string.
    
    Doctests:
    >>> replace_field_name("name", 3)
    ("record['name']", -1)
    >>> replace_field_name("pid", 2)
    ("record['pid']", -1)
    >>> replace_field_name("context.mapping", 14)
    ("record['context']['mapping']", -1)
    >>> replace_field_name("False", 4)
    ('False', -1)
    """
    
    specials = ["True", "False", "None"] # these are not field names
    done = False # flag that holds if we're finished processing this field name
    while not done:
        field_name = ""
        start_ix = i
        while i >= 0 and cmd_str[i].isalpha():
            field_name += cmd_str[i]
            i -= 1
        field_name = field_name[::-1] # flip the string around
        if field_name not in specials:
            if cmd_str[i] == '.':
                cmd_str = cmd_str[:i] + "[\'" + field_name + "\']" + cmd_str[start_ix + 1:]
                i -= 1
            else:
                cmd_str = cmd_str[:i + 1] + "record[\'" + field_name + "\']" + cmd_str[start_ix + 1:]
                done = True
        else:
            done = True
    
    return cmd_str, i


def make_eval_string(cmd_str: str) -> str:
    """
    Takes the user-entered string from the command line and returns a
    Python-executable string suitable for running in screen_record().
    """
    i = len(cmd_str)
    
    while i >= 0:
        i -= 1
        # skip over string literals
        if cmd_str[i] == '\"':
            i = skip_literal(cmd_str, i)
        
        # replace field names with record['<field name>']
        if cmd_str[i].isalpha():
            cmd_str, i = replace_field_name(cmd_str, i)
        
        # replace '~=' with 'in'
        if cmd_str[i] == '~' and cmd_str[i + 1] == '=':
            cmd_str = cmd_str[:i].rstrip() + " in " + cmd_str[i + 2:].lstrip()
    
    return cmd_str
    
    
def get_op_ix(condition: str) -> int:
    """
    Given supplied condition string, identify the first 
    logical operator ('!', '&', or '|') not enclosed in
    parentheses. Return the index of the logical 
    operator, or -1 if no logical operator.
    
    Doctests:
    >>> get_op_ix("name")
    -1
    >>> get_op_ix("~(pid == 460)")
    0
    >>> get_op_ix("pid == 460 & x == 5")
    11
    """
    
    ops = ['~', '&', '|'] # logical operators
    open_parens = 0
    i = 0
    # break loop if running over end of string, or if we found desired operator
    while i < len(condition) and (condition[i] not in ops or open_parens != 0):
        if condition[i] == '(':
            open_parens += 1
        elif condition[i] == ')':
            open_parens -= 1
        i += 1
    
    if i == len(condition):
        return -1
    return i


def custom_eval(record: dict, clauses: list) -> bool:
    """
    Given the possibly nested list of clauses, evaluate the expression
    using recursive calls, catching TypeErrors and KeyErrors from
    records that don't have the required fields and returning False.
    """
    result = False
    # base case: only one element in list
    if len(clauses) == 1:
        try:
            result = eval(clauses[0])
        except (KeyError, TypeError): # don't fail if records don't have required fields
            result = False
    elif len(clauses) == 2 and clauses[0] == '~': # it's a not
        result = not custom_eval(record, clauses[1])
    elif len(clauses) == 3 and clauses[0] == '&': # it's an and
        result = custom_eval(record, clauses[1]) and custom_eval(record, clauses[2])
    elif len(clauses) == 3 and clauses[0] == '|': # it's an or
        result = custom_eval(record, clauses[1]) or custom_eval(record, clauses[2])
    else:
        print("Screen did not evaluate properly")
        result = False
    return result
    

def parse_string(condition: str) -> list:
    """
    Given supplied condition string representing the screen, return
    a possibly nested list of the logical clauses in the condition.
    
    Doctests:
    >>> parse_string("x == 5")
    ['x == 5']
    >>> parse_string("~(x == 5)")
    ['~', ['x == 5']]
    >>> parse_string("x == 5 & y == 4")
    ['&', ['x == 5], ['y == 4']]
    >>> parse_string("x == 5)
    """
    
    # if string surrounded by parens, remove parens
    if len(condition) != 0 and condition[0] == '(' and condition[len(condition) - 1] == ')':
        condition = condition[1:len(condition) - 1]
    
    op_ix = get_op_ix(condition) # get the index of the operator
    if op_ix == -1: # if no logical operator found
        return [condition]
    
    left = parse_string(condition[:op_ix].rstrip())
    right = parse_string(condition[op_ix + 1:].lstrip())
    
    # if we have a not operation, only the right side is going to be a non-empty string
    if condition[op_ix] == '~':
        return [condition[op_ix], right]
    else:
        return [condition[op_ix], left, right]
    

def screen_record(record: dict, clauses: list, condition) -> bool:
    """
    Given the supplied record and screening nested list, return True
    if it satisfies the screen entered by the user, and False otherwise.
    """
    # if no condition entered by user
    if (len(condition) == 0): 
        return True
    
    # call custom_eval to evaluate each clause separately and catch KeyError and TypeError
    return custom_eval(record, clauses)
    

##################################################################################################


@click.command()
@click.option('--color/--no-color', default=True, help='Print with colors.')
@click.option('--indent', default=2, help='Indentation level (spaces).',
              show_default=True)
@click.option('--screen', default="", type=str, help='Expression for screening records')
def cli(**options):
    """ TODO """
    colorize = make_colorizer(options['color']) # make machinery that colors the printed records
    condition = make_eval_string(options['screen']) # turn user input into Python-executable string
    clauses = parse_string(condition) # turn condition into possibly nested list of clauses
    # print("Filter expression: " + options['screen'])
    # print("Python expression: " + condition)
    # print("Nested clauses: " + str(clauses))
    
    # for each line in input, load the next record, screen it, and print if wanted
    for line in sys.stdin:
        line = line.strip()
        try:
            record = json.loads(line)
            if screen_record(record, clauses, condition):
                print(format_record(record, options, colorize))
        except (json.JSONDecodeError, KeyError):
            print(f'Fatal: "{line}" is not a valid log record.', file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    cli()
