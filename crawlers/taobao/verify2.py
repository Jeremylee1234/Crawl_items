import os
import time
import json
import random
import datetime
import pyautogui
import alchemy as db
from utils import utils
from threading import Lock
from utils.create_driver import Driver
from selenium.webdriver.common.by import By
from crawlers.taobao import msg_alchemy as msg_db
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class UpdateCookies(object):

    def __init__(self, driver, cookie):
        self.err_times = 0
        self.driver = driver
        self.lock = Lock()
        self.cookie = cookie['cookie']

    @utils.my_async
    def track_refresh(self):
        pass

    @utils.my_async
    def slide_btn(self):
        pass

    def login_by_code(self):
        if self.driver == None:
            return None
        elif self.err_times <= 5:
            try:
                if self.driver.current_url == 'https://login.taobao.com/member/login.jhtml':
                    time.sleep(0.5)
                    switch_sms = self.driver.find_elements_by_xpath('//div[@class="login-password"]/div[1]/a[2]')[0]
                    switch_sms.click()
                    time.sleep(1)
                    input_username = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.ID, 'fm-sms-login-id'))
                    )
                    input_password = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.ID, 'fm-smscode'))
                    )
                    time.sleep(1)
                    input_username.clear()
                    input_password.clear()

                    for u in self.cookie.phone:
                        input_username.send_keys(u)
                        time.sleep(random.randint(10,70)/1000)
                    time.sleep(0.5)
                    send_code_btn = self.driver.find_elements_by_xpath('//div[@class="send-btn"]/a')[0]
                    send_code_btn.click()
                    self.slide_btn()
                    message = utils.get_code(msg_db.get_new_msg())
                    if message == None:
                        self.err_times += 10
                        self.driver.refresh()
                        return self.login_by_code()
                    for u in message:
                        input_password.send_keys(u)
                        time.sleep(random.randint(10,70)/1000)
                    time.sleep(0.5)
                    login_coord = pyautogui.locateOnScreen('/files/images/taobao-pc-login-btn.png')
                    if login_coord:
                        x, y = pyautogui.center(login_coord)
                        pyautogui.moveTo(x=random.randint(x-10,x+10),y=random.randint(y-10,y+10),duration=0.5,tween=pyautogui.easeInOutQuart)
                        time.sleep(0.2)
                        pyautogui.leftClick()
                        time.sleep(0.5)
                        pyautogui.moveTo(100,500)
                    else:
                        self.err_times += 5
                        return self.login_by_code()
                    check_times = 0
                    while 'login' in self.driver.current_url:
                        check_times += 1
                        time.sleep(3)
                        if check_times >= 10:
                            self.err_times += 10
                            return self.login_by_code()
                    time.sleep(7)
                    cookies = self.driver.get_cookies()
                    self.driver.quit()
                    return cookies
                else:
                    self.driver.get('https://login.taobao.com/member/login.jhtml')        
                    time.sleep(1)
                    self.err_times += 1
                    return self.login_by_code()
            except Exception as e:
                print(e)
                self.err_times += 1
                return self.login_by_code()

    def update_cookie(self, cookies):
        if cookies:
            self.cookie.cookie = json.dumps(cookies)
            self.cookie.useful = True
            db.db_session.commit()
            return True
        else:
            return None

def update_all_cookies():
    all_cookies = db.get_cookies(1, False)
    for cookie in all_cookies:
        try:
            driver = Driver('https://world.taobao.com/wow/z/oversea/SEO-SEM/ovs-pc-login').create_driver(need_proxy=False,ua='mobile')
            login = UpdateCookies(driver, cookie)
            cookies = login.login_by_code()
            login.update_cookie(cookies)
            del login
        except Exception as e:
            print(f'更新cookie时出错:{e}')
            continue
    os.system('taskkill /F /im chromedriver.exe')
    os.system('taskkill /F /im chrome.exe')
