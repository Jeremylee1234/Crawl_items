import os
import time
import json
import random
import pyautogui
import alchemy as db
from utils import utils
from threading import Lock
from utils.logger import logger
from utils.create_driver import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

class UpdateCookies(object):
    def __init__(self, driver, cookie):
        self.err_times = 0
        self.driver = driver
        self.lock = Lock()
        self.cookie = cookie['cookie']

    @utils.my_async
    def slide_taobao_btn(self):
        watch_time = 0
        do_times = 0
        while True:
            watch_time += 1
            if watch_time >= 30:
                return 
            if do_times >= 1:
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

    @utils.my_async
    def click_taobao_login(self):
        watch_time = 0
        do_times = 0
        while True:
            watch_time += 1
            if watch_time >= 20:
                return 
            if do_times >= 1:
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
                time.sleep(4.5)
                continue

    # ??????PC???????????????
    def login_taobao(self):
        if self.driver == None:
            return None
        elif self.err_times <= 3:
            try:
                if 'login.taobao.com/member/login.jhtml' in self.driver.current_url:
                    time.sleep(0.5)
                    input_username = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.ID, 'fm-login-id'))
                    )
                    input_password = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.ID, 'fm-login-password'))
                    )
                    time.sleep(0.5)
                    input_username.clear()
                    input_password.clear()

                    for u in self.cookie.username:
                        input_username.send_keys(u)
                        time.sleep(random.randint(10,70)/1000)
                    for p in self.cookie.password:
                        input_password.send_keys(p)
                        time.sleep(random.randint(10,70)/1000)
                    time.sleep(0.7)
                    self.click_taobao_login()
                    self.slide_taobao_btn()

                    check_times = 0
                    while 'login' in self.driver.current_url:
                        err_info = self.driver.find_elements_by_xpath('//iframe[@id="baxia-dialog-content"]')
                        if len(err_info) >= 1:
                            self.lock.acquire()
                            self.driver.switch_to.frame(err_info[0])
                            failed_info = self.driver.find_elements_by_xpath('//div[@id="nocaptcha"]//a[contains(@id,"refresh")]')
                            if len(failed_info) >= 1 and failed_info[0].is_displayed():
                                self.driver.switch_to.default_content()
                                self.err_times += 2
                                try:
                                    self.driver.refresh()
                                except TimeoutException:
                                    self.driver.execute_script('window.stop()')
                                time.sleep(5)
                                self.lock.release()
                                return self.login_taobao()
                            self.driver.switch_to.default_content()
                            self.lock.release()

                        check_times += 1
                        time.sleep(3)
                        if check_times >= 20:
                            print('??????????????????,??????????????????')
                            self.err_times += 2
                            return self.login_taobao()
                    time.sleep(2)
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.ID, 'J_Col_Main'))
                    )
                    cookies = self.driver.get_cookies()
                    self.driver.quit()
                    return cookies
                else:
                    self.driver.get('https://login.taobao.com/member/login.jhtml')
                    time.sleep(1)
                    self.err_times += 2
                    return self.login_taobao()
            except Exception as e:
                logger.info(1,'verify3??????',e,self.cookie.username)
                self.driver.get('https://login.taobao.com/member/login.jhtml')
                time.sleep(1)
                self.err_times += 2
                return self.login_taobao()
        else:
            logger.error(1,'verify3??????',None,self.cookie.username)
            self.driver.quit()
            return None

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
            driver = Driver('https://login.taobao.com/member/login.jhtml').create_driver(need_proxy=False,ua='pc')
            login = UpdateCookies(driver, cookie)
            cookies = login.login_taobao()
            login.update_cookie(cookies)
            del login
        except Exception as e:
            logger.error(1,'??????cookie?????????',e,cookie['cookie'].username)
            continue
    os.system('taskkill /F /im chromedriver.exe')
    os.system('taskkill /F /im chrome.exe')
