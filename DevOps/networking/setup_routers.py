#!/usr/bin/env python3

"""
Script for setting up TP-Link TL-WR802N routers
Changes SSID to Team{teamnum}

Requires the gecko webdriver to be placed into /usr/bin/ or other path location
as per OS, download
the one relevant to your system at
https://github.com/mozilla/geckodriver/releases

Occasionally script will error if it tries to find an element
before the page has loaded, in this case just rerun the script.
USAGE:
connect to router over wifi
run script with team number
"""

from argparse import ArgumentParser, ArgumentTypeError
import logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoSuchFrameException
from selenium.webdriver.common.keys import Keys
import sys
import time

ROUTER_ADMIN_URL = 'http://tplinkwifi.net'


def positive_int(x) -> int:
    y = int(x)
    if y <= 0:
        raise ArgumentTypeError('not a positive integer')
    return y


def parse_args():
    parser = ArgumentParser(description="""
    Change the default SSID of a TPLINK router to the form "Team##".
    Connect to the router before running this script.
    `selenium` must be installed on your machine.
    """)
    parser.add_argument('team_number', help='team number', metavar='team-number',
                        type=positive_int)
    parser.add_argument('-u', '--username', help='router administrator username',
                        default='admin')
    parser.add_argument('-p', '--password', help='router administrator password',
                        default='admin')
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser.parse_args()


def login(username: str, password: str, driver) -> bool:
    driver.get(ROUTER_ADMIN_URL)
    driver.find_element_by_id('userName').send_keys(username)
    driver.find_element_by_id('pcPassword').send_keys(password)
    driver.find_element_by_id('loginBtn').click()

    try:
        driver.find_element_by_id('tip')
        logging.error('Failed to log in (invalid credentials)')
    except NoSuchElementException:
        return True


def change_ssid(username: str, password: str, ssid: str):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(desired_capabilities=options.to_capabilities())
    driver.implicitly_wait(10)

    try:
        logging.debug('Logging in as user "{username}" ...'.format(username=username))
        if not login(username, password, driver):
            return

        driver.switch_to_frame('bottomLeftFrame')  # Left panel
        driver.find_element_by_id('a8').click()
    except (NoSuchElementException, NoSuchFrameException):
        logging.error('Not connected to the router')
        return

    driver.switch_to_default_content()
    driver.switch_to_frame('mainFrame')
    ssid_element = driver.find_element_by_id('ssid1')
    ssid_element.clear()
    ssid_element.send_keys(ssid)
    driver.find_element_by_id('Save').click()

    driver.quit()


def main():
    args = parse_args()
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format='[{asctime}]: {message}', style='{',
                        level=level, stream=sys.stdout)

    ssid = 'Team{:0>2}'.format(args.team_number)
    logging.debug('Changing SSID to "{ssid}" ...'.format(ssid=ssid))
    change_ssid(args.username, args.password, ssid)
    logging.debug('Done.')
    logging.shutdown()


if __name__ == '__main__':
    main()
