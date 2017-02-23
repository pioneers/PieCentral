from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
import time

teamNum = sys.argv[1]

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
wireless = wd.find_element_by_id("a8")
wireless.click()

wd.switch_to_default_content()

wd.switch_to_frame("mainFrame")
ssid = wd.find_element_by_id("ssid1")
ssid.send_keys(Keys.BACKSPACE * 50)
ssid.send_keys("Team" + teamNum)

save = wd.find_element_by_id("Save")
save.click()
