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

    # 淘宝移动端登陆页面滑块功能，现已弃用
    @utils.my_async
    def slide_h5_btn(self):
        watch_time = 0
        success_time = 0
        while True:
            if watch_time >= 30:
                self.driver.quit()
                return 
            if success_time >= 2:
                time.sleep(10)
                self.driver.quit()
                return 
            watch_time += 1
            time.sleep(2)
            try:
                login_frame = self.driver.find_elements_by_xpath('//iframe[contains(@src,"login.m.taobao.com")]')
                if len(login_frame) >= 1 and login_frame[0].is_displayed():
                    time.sleep(1)
                    self.driver.switch_to.frame(login_frame[0])
                    time.sleep(2)
                    slide_rows = utils.find_all_sele_xpath(self.driver, '//div[@id="nc_2__scale_text"]', '//div[@id="nc_1__scale_text"]', '//div[@class="slider"]')
                    row_length = slide_rows[0].size['width']
                    slider = pyautogui.locateOnScreen('./files/images/slider.png')
                    slider_b = pyautogui.locateOnScreen('./files/images/slider-b.png')
                    if slider_b:
                        pyautogui.moveTo(pyautogui.center(slider_b))
                        time.sleep(random.randint(5,30)/100)
                        pyautogui.dragRel(random.randint(row_length,row_length+50), random.randint(-20,20), random.randint(70,150)/100, random.choice([pyautogui.easeInOutQuart, pyautogui.easeInQuad, pyautogui.easeInOutQuad, pyautogui.easeOutQuad, pyautogui.easeInQuart]))
                        time.sleep(1.5)
                        success_time += 1
                        login_coords = pyautogui.locateOnScreen('./files/images/h5_login.png')
                        if login_coords:
                            time.sleep(1)
                            pyautogui.leftClick(pyautogui.center(login_coords))
                        else:
                            continue
                    elif slider:
                        pyautogui.moveTo(pyautogui.center(slider))
                        time.sleep(random.randint(5,30)/100)
                        pyautogui.dragRel(random.randint(row_length,row_length+50), random.randint(-20,20), random.randint(70,150)/100, random.choice([pyautogui.easeInOutQuart, pyautogui.easeInQuad, pyautogui.easeInOutQuad, pyautogui.easeOutQuad, pyautogui.easeInQuart]))
                        time.sleep(1.5)
                        success_time += 1
                        login_coords = pyautogui.locateOnScreen('./files/images/h5_login.png')
                        if login_coords:
                            time.sleep(1)
                            pyautogui.leftClick(pyautogui.center(login_coords))
                        else:
                            continue
                    else:
                        continue
            except Exception as e:
                print(e)
                return 

    # 淘宝移动端登陆，现已弃用
    def login_h5(self):
        if self.driver == None:
            return None
        elif self.err_times <= 5:
            if '阿里拍卖' in self.driver.title and self.driver.current_url == 'https://h5.m.taobao.com/paimai/v3/index.html':
                self.driver.get('https://login.m.taobao.com/login.htm?redirectURL=https%3A%2F%2Fmarket.m.taobao.com%2Fapp%2Fpm%2Frax-tesla%2Fpages%2Fmy%3Fspm%3Da2129.12529781.tabbar.5')
                time.sleep(1)
                try:
                    self.driver.maximize_window()
                except Exception as e:
                    print(e)
                time.sleep(0.5)
                self.slide_h5_btn()
                try:
                    input_username = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.ID, 'fm-login-id'))
                    )
                    input_password = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.ID, 'fm-login-password'))
                    )
                    time.sleep(2)
                    input_username.clear()
                    input_password.clear()

                    for u in self.cookie.username:
                        input_username.send_keys(u)
                        time.sleep(0.05)
                    for p in self.cookie.password:
                        input_password.send_keys(p)
                        time.sleep(0.05)
                    time.sleep(3)
                    login_frame = self.driver.find_elements_by_xpath('//iframe[contains(@src,"login.m.taobao.com")]')
                    slider = pyautogui.locateOnScreen('./files/images/slider.png')
                    slider_b = pyautogui.locateOnScreen('./files/images/slider-b.png')
                    if len(login_frame) == 0 and not slider and not slider_b:
                        login_coords = pyautogui.locateOnScreen('./files/images/h5_login.png')
                        if login_coords:
                            time.sleep(1)
                            pyautogui.leftClick(pyautogui.center(login_coords))

                    url_check_times = 0
                    while 'market.m.taobao.com/app/pm/rax-tesla/pages/my' not in self.driver.current_url:
                        time.sleep(1)
                        url_check_times += 1
                        if url_check_times >= 45:
                            return self.login_h5()
                        else:
                            continue
                    time.sleep(0.5)
                    cookies = self.driver.get_cookies()
                    return cookies

                except Exception as e:
                    print(e)
                    self.err_times += 10
                    return self.login_h5()

            else:
                self.driver.get('https://h5.m.taobao.com/paimai/v3/index.html')
                time.sleep(5)
                self.err_times += 10
                return self.login_h5()
        else:
            print('failed!!!')
            return None

    @utils.my_async
    def slide_world_btn(self):
        watch_time = 0
        do_times = 0
        while True:
            watch_time += 1
            try:
                self.lock.acquire()
                WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, '//iframe[@id="J_Member"]'))
                )
                self.lock.release()
            except Exception as e:
                print(e)
                return 
            if watch_time >= 30:
                return 
            if do_times >= 2:
                return 
            if 'login' not in self.driver.current_url:
                return 

            slider = pyautogui.locateOnScreen('./files/images/slider_world.png')
            if slider:
                x, y = pyautogui.center(slider)
                self.lock.acquire()
                utils.slide_btn(x, y, 300, 0)
                self.lock.release()
                do_times += 1
            else:
                continue

    @utils.my_async
    def click_world_login(self):
        watch_time = 0
        do_times = 0
        while True:
            watch_time += 1
            try:
                self.lock.acquire()
                WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, '//iframe[@id="J_Member"]'))
                )
                self.lock.release()
            except Exception as e:
                print(e)
                return 
            if watch_time >= 20:
                return 
            if do_times >= 2:
                return 
            if 'login' not in self.driver.current_url:
                return 
            
            login_coord = pyautogui.locateOnScreen('./files/images/world_login.png')
            if login_coord:
                x, y = pyautogui.center(login_coord)
                self.lock.acquire()
                utils.click_btn(x, y)
                self.lock.release()
                do_times += 1
            else:
                time.sleep(4.5)
                continue

    # 登录国际PC端淘宝网页
    def login_world(self):
        if self.driver == None:
            return None
        elif self.err_times <= 3:
            try:
                if self.driver.current_url == 'https://world.taobao.com/wow/z/oversea/SEO-SEM/ovs-pc-login':
                    time.sleep(0.5)
                    login_frame = self.driver.find_elements_by_xpath('//iframe[@id="J_Member"]')
                    if len(login_frame) >= 1:
                        login_frame = login_frame[0]
                        self.driver.switch_to.frame(login_frame)
            
                        # try:
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
                        self.driver.switch_to.default_content()
                        time.sleep(0.7)
                        self.click_world_login()
                        self.slide_world_btn()
                        
                        check_times = 0
                        while 'login' in self.driver.current_url:
                            self.lock.acquire()
                            self.driver.switch_to.frame(login_frame)
                            failed_info = self.driver.find_elements_by_xpath('//*[@id="baxia-dialog-content"]')
                            if len(failed_info) >= 1 and failed_info[0].is_displayed():
                                failed_info = failed_info[0]
                                self.driver.switch_to.frame(failed_info)
                                failed_info = self.driver.find_elements_by_xpath('//a[@id="nc_1_refresh1"]')
                                if len(failed_info) >= 1 and failed_info[0].is_displayed():
                                    self.driver.switch_to.default_content()
                                    self.err_times += 2
                                    try:
                                        self.driver.refresh()
                                    except TimeoutException:
                                        self.driver.execute_script('window.stop()')
                                    time.sleep(5)
                                    self.lock.release()
                                    return self.login_world()
                            self.driver.switch_to.default_content()
                            self.lock.release()
                            check_times += 1
                            time.sleep(3)
                            if check_times >= 20:
                                print('最大尝试次数,判断登陆失败')
                                self.err_times += 2
                                return self.login_world()
                        time.sleep(2)
                        WebDriverWait(self.driver, 15).until(
                            EC.presence_of_element_located((By.ID, 'search-box'))
                        )
                        cookies = self.driver.get_cookies()
                        self.driver.quit()
                        return cookies
                    else:
                        self.driver.get('https://world.taobao.com/wow/z/oversea/SEO-SEM/ovs-pc-login')
                        time.sleep(2)
                        self.err_times += 2
                        return self.login_world()
                else:
                    self.driver.get('https://world.taobao.com/wow/z/oversea/SEO-SEM/ovs-pc-login')
                    time.sleep(1)
                    self.err_times += 2
                    return self.login_world()
            except Exception as e:
                logger.info(1,'verify1重试',e,self.cookie.username)
                self.driver.get('https://world.taobao.com/wow/z/oversea/SEO-SEM/ovs-pc-login')
                time.sleep(1)
                self.err_times += 2
                return self.login_world()
        else:
            logger.error(1,'verify1放弃',None,self.cookie.username)
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
            driver = Driver('https://world.taobao.com/wow/z/oversea/SEO-SEM/ovs-pc-login').create_driver(need_proxy=False,ua='pc')
            login = UpdateCookies(driver, cookie)
            cookie = login.login_world()
            login.update_cookie(cookie)
            del login
        except Exception as e:
            logger.error(1,'更新cookie时错误',e,cookie['cookie'].username)
            continue
    os.system('taskkill /F /im chromedriver.exe')
    os.system('taskkill /F /im chrome.exe')
