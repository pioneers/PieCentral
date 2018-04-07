#!/usr/bin/env python3

"""
Script for setting up TP-Link TL-WR802N routers:
  * Changes SSID to "TeamNN", where "NN" is the team number.

Requires Python bindings for the Selenium browser automation framework, as well
as the Gecko webdriver. See "https://github.com/mozilla/geckodriver/releases"
for details.

Connect to the router before running this script.
"""

from argparse import ArgumentParser, ArgumentTypeError
import logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoSuchFrameException
from selenium.webdriver.common.keys import Keys
import sys
import time

ROUTER_ADMIN_URL = 'http://192.168.0.1'  # "tplinkwifi.net" is sometimes accessible


def valid_team_number(x, min_team_num=0, max_team_num=54) -> int:
    """ Parse and validate a given team number. """
    team_num = int(x)
    if not min_team_num <= team_num <= max_team_num:
        raise ValueError(f'team number must be between {min_team_num} and {max_team_num}')
    return team_num


def parse_args():
    parser = ArgumentParser(description="""
        Change the default SSID of a TP-Link router to the form "TeamNN", where
        "NN" is the team number. Connect to the router before running this script.
        Python bindings for the Selenium browser automation framework must be
        installed on your machine.
    """)
    parser.add_argument('team_number', help='team number', metavar='team-number',
                        type=valid_team_number)
    parser.add_argument('-u', '--username', help='router administrator username (default: admin)',
                        default='admin')
    parser.add_argument('-p', '--password', help='router administrator password (default: admin)',
                        default='admin')
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser.parse_args()


def login(driver, username: str, password: str) -> bool:
    """ Attempt to log in to the admin site, and return whether the request succeeded. """
    driver.get(ROUTER_ADMIN_URL)
    driver.find_element_by_id('userName').send_keys(username)
    driver.find_element_by_id('pcPassword').send_keys(password)
    driver.find_element_by_id('loginBtn').click()

    try:
        driver.find_element_by_id('loginBtn')
        return False
    except NoSuchElementException:
        return True


def change_ssid(driver, ssid: str):
    driver.switch_to_frame('bottomLeftFrame')
    driver.find_element_by_id('menu_wl').click()

    driver.switch_to_default_content()
    driver.switch_to_frame('mainFrame')
    ssid_element = driver.find_element_by_id('ssid')
    ssid_element.clear()
    ssid_element.send_keys(ssid)
    driver.find_element_by_class_name('T_save').click()


def setup_router(username: str, password: str, ssid: str):
    """ Execute all setup tasks. """
    logging.debug(f'Initializing webdriver ...')
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(desired_capabilities=options.to_capabilities())
    driver.implicitly_wait(10)

    logging.debug(f'Logging in as user "{username}" ...')
    if not login(driver, username, password):
        logging.error(f'Failed to log in.')
        return
    logging.debug('Login succeeded.')

    logging.debug(f'Changing SSID to {ssid} ...')
    change_ssid(driver, ssid)  # Perform this task last
    driver.quit()


def main():
    args = parse_args()
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format='[{asctime}]: {message}', style='{',
                        level=level, stream=sys.stdout)

    try:
        ssid = 'Team{}'.format(args.team_number)
        logging.info('Configuring router ...')
        setup_router(args.username, args.password, ssid)
        logging.info('Done.')
    except KeyboardInterrupt:
        logging.debug('Keyboard interrupt detected.')
    finally:
        logging.shutdown()


if __name__ == '__main__':
    main()
