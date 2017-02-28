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
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import argparse

parser = argparse.ArgumentParser(description=
                                 """Sets up team routers by changing ssid to be Team{teamNum}.
                                 Connect to the router, then run the script.
                                 If there is a missing driver error, download the latest for
                                 your system from
                                 https://github.com/mozilla/geckodriver/releases and
                                 place it into a path directory""")
parser.add_argument("teamNum", help="team number")

args = parser.parse_args()
teamNum = args.teamNum

wd = webdriver.Firefox()
wd.get("http://tplinkwifi.net")

uname = wd.find_element_by_id("userName")
pwd = wd.find_element_by_id("pcPassword")
login = wd.find_element_by_id("loginBtn")

uname.send_keys("admin")
pwd.send_keys("admin")
login.click()

time.sleep(.5)

wd.switch_to_frame("bottomLeftFrame")
time.sleep(.2)
wireless = wd.find_element_by_id("a8")
wireless.click()

wd.switch_to_default_content()

wd.switch_to_frame("mainFrame")
time.sleep(.2)
ssid = wd.find_element_by_id("ssid1")
ssid.send_keys(Keys.BACKSPACE * 50)
ssid.send_keys("Team" + teamNum)

save = wd.find_element_by_id("Save")
save.click()
time.sleep(.5)

wd.quit()

