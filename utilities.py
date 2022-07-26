from config import *

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import os
from time import sleep
import pickle

try:
    current_path = os.path.dirname(os.path.abspath(__file__))
except:
    current_path = '.'
    
    
def init_driver(gecko_driver='', user_agent='', load_images=True, is_headless=False):
    firefox_profile = webdriver.FirefoxProfile()
    
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
    firefox_profile.set_preference("media.volume_scale", "0.0")
    firefox_profile.set_preference("dom.webnotifications.enabled", False)
    if user_agent != '':
        firefox_profile.set_preference("general.useragent.override", user_agent)
    if not load_images:
        firefox_profile.set_preference('permissions.default.image', 2)

    options = Options()
    options.headless = is_headless
    
    driver = webdriver.Firefox(options=options,
                               executable_path=f'{current_path}/{gecko_driver}',
                               firefox_profile=firefox_profile)
    
    return driver
  
def quora_login(driver, username, user_pwd):

    driver.get(quora_login_page)
    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        
        driver.get(quora_url)
        sleep(3)
    except:
        # email = form.find_element_by_name("email")
        email = driver.find_element("name", "email")
        email.send_keys(username)

        # password = form.find_element_by_name("password")
        password = driver.find_element("name", 'password')
        password.send_keys(user_pwd)
        password.send_keys(Keys.RETURN)
        sleep(3)
        pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
        
    