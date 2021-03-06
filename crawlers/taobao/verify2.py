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
    def slide_code_btn(self):
        watch_time = 0
        do_times = 0
        while True:
            watch_time += 1
            try:
                WebDriverWait(self.driver, 0.2).until(
                    EC.presence_of_element_located((By.ID, 'login-form'))
                )
                if watch_time >= 30:
                    self.driver.quit()
                    return 
                if do_times >= 3:
                    self.driver.quit()
                    return 
                if 'login' not in self.driver.current_url:
                    return 
                slider = pyautogui.locateOnScreen('./files/images/slider_pc_taobao.png')
                if slider:
                    x, y = pyautogui.center(slider)
                    self.lock.acquire()
                    utils.slide_btn(x, y, 300, 0)
                    self.lock.release()
                    do_times += 1
                else:
                    time.sleep(3)
                    continue
            except Exception as e:
                watch_time += 1
                print(e)
                return 

    @utils.my_async
    def click_taobao_login(self):
        watch_time = 0
        do_times = 0
        while True:
            watch_time += 1
            try:
                WebDriverWait(self.driver, 0.2).until(
                    EC.presence_of_element_located((By.ID, 'login-form'))
                )
                if watch_time >= 30:
                    self.driver.quit()
                    return 
                if do_times >= 3:
                    self.driver.quit()
                    return 
                if 'login' not in self.driver.current_url:
                    return 
            
                login_coord = pyautogui.locateOnScreen('./files/images/btn_pc_taobao.png')
                if login_coord:
                    x, y = pyautogui.center(login_coord)
                    self.lock.acquire()
                    utils.click_btn(x, y)
                    self.lock.release()
                    do_times += 1
                else:
                    time.sleep(3)
                    continue
            except Exception as e:
                print(e)
                watch_time += 1
                continue

    def login_by_code(self):
        if self.driver == None:
            return None
        elif self.err_times <= 5:
            try:
                if 'login.taobao.com/member/login.jhtml' in self.driver.current_url:
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
                    time.sleep(0.5)
                    input_username.clear()
                    input_password.clear()

                    for u in self.cookie.phone:
                        input_username.send_keys(u)
                        time.sleep(random.randint(10,70)/1000)
                    time.sleep(0.5)
                    self.slide_code_btn()
                    send_code_btn = self.driver.find_elements_by_xpath('//div[@class="send-btn"]/a')[0]
                    send_code_btn.click()
                    message = utils.get_code(msg_db.get_new_msg())
                    if message == None:
                        self.err_times += 10
                        self.driver.refresh()
                        return self.login_by_code()
                    for p in message:
                        input_password.send_keys(p)
                        time.sleep(random.randint(30,100)/1000)
                    time.sleep(0.7)
                    self.click_taobao_login()
                    check_times = 0
                    while len(self.driver.find_elements_by_xpath('//iframe[@id="baxia-dialog-content"]')) >= 1 and self.driver.find_elements_by_xpath('//iframe[@id="baxia-dialog-content"]')[0].is_diplayed() or 'login' in self.driver.current_url:
                        self.lock.acquire()
                        err_info = self.driver.find_elements_by_xpath('//iframe[@id="baxia-dialog-content"]')
                        if len(err_info) >= 1:
                            self.driver.switch_to.frame(err_info[0])
                            err_info = self.driver.find_elements_by_xpath('//div[@id="nocaptcha"]//a[@contains(id,"refresh")]')
                            if len(err_info) >= 1:
                                err_info = err_info[0]
                                err_info.click()
                                self.driver.switch_to.default_content()
                                self.lock.release()
                                self.err_times += 1
                                return self.login_taobao()
                            else:
                                self.lock.release()
                        else:
                            self.lock.release()
                        check_times += 1
                        time.sleep(3)
                        if check_times >= 30:
                            print('??????????????????,??????????????????')
                            self.err_times += 10
                            return self.login_world()
                    time.sleep(8)
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
    all_cookies = db.get_cookies(siteId=1, useful=False, phone=True)
    for cookie in all_cookies:
        try:
            driver = Driver('https://login.taobao.com/member/login.jhtml').create_driver(need_proxy=False,ua='pc')
            login = UpdateCookies(driver, cookie)
            cookies = login.login_by_code()
            login.update_cookie(cookies)
            del login
        except Exception as e:
            print(f'??????cookie?????????:{e}')
            continue
    os.system('taskkill /F /im chromedriver.exe')
    os.system('taskkill /F /im chrome.exe')
