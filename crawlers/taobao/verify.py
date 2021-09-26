import os
import time
import json
import random
import pyautogui
import alchemy as db
from utils import utils
from threading import Lock
from utils.create_driver import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class UpdateCookies(object):

    def __init__(self, driver, cookie):
        self.err_times = 0
        self.driver = driver
        self.lock = Lock()
        self.cookie = cookie['cookie']

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

    @utils.my_async
    def slide_world_btn(self):
        watch_time = 0
        while True:
            watch_time += 1
            try:
                if watch_time >= 20:
                    self.driver.quit()
                    return 
                if self.driver.current_url == 'https://world.taobao.com/':
                    return 
                self.lock.acquire()
                login_frame = self.driver.find_elements_by_xpath('//iframe[@id="J_Member"]')[0]
                self.driver.switch_to.frame(login_frame)
                failed_info = self.driver.find_elements_by_xpath('//*[@class="errloading"]')
                self.driver.switch_to.default_content()
                self.lock.release()
                if len(failed_info) >= 1:
                    return 
                
                time.sleep(2)
                slider = pyautogui.locateOnScreen('./files/images/slider_world.png')
                choose_slide = random.randint(0,100) # 随机选择拖拽方式
                if slider:
                    if choose_slide >= 30:
                        # 鼠标点击同拖拽分离
                        pyautogui.moveTo(x=random.randint(10,1000),y=random.randint(10,1000),duration=0.5,tween=pyautogui.easeInOutQuad)
                        x, y = pyautogui.center(slider)
                        pyautogui.moveTo(x=random.randint(x-10,x+10),y=random.randint(y-10,y+10),duration=0.5,tween=pyautogui.easeInOutQuart)
                        time.sleep(random.randint(5,30)/100)
                        pyautogui.mouseDown()
                        pyautogui.moveRel(random.randint(90,180), random.randint(-15,15), random.randint(10,40)/100, utils.random_gradient())
                        pyautogui.moveRel(random.randint(165,330), random.randint(-40,40), random.randint(30,80)/100, utils.random_gradient())
                        pyautogui.moveRel(random.randint(45,90), random.randint(-15,15), random.randint(12,55)/100, utils.random_gradient())
                        time.sleep(0.01)
                        pyautogui.mouseUp()
                        time.sleep(1.5)
                    else:
                        # 鼠标点击同拖拽合并为drag
                        pyautogui.moveTo(x=random.randint(100,1000),y=random.randint(100,1000),duration=0.5,tween=pyautogui.easeInOutQuad)
                        x, y = pyautogui.center(slider)
                        pyautogui.moveTo(x=random.randint(x-10,x+10),y=random.randint(y-10,y+10),duration=0.5,tween=pyautogui.easeInOutQuart)
                        time.sleep(random.randint(5,30)/100)
                        pyautogui.dragRel(random.randint(301,550), random.randint(-40,40), random.randint(40,150)/100, utils.random_gradient())
                        time.sleep(1.5)
                else:
                    continue
            except Exception as e:
                watch_time += 1
                print(e)
                return 

    @utils.my_async
    def click_world_login(self):
        watch_time = 0
        while True:
            watch_time += 1
            try:
                if watch_time >= 10:
                    self.driver.quit()
                    return 
                if self.driver.current_url == 'https://world.taobao.com/':
                    return 
            
                self.lock.acquire()
                login_frame = self.driver.find_elements_by_xpath('//iframe[@id="J_Member"]')[0]
                self.driver.switch_to.frame(login_frame)
                failed_info = self.driver.find_elements_by_xpath('//*[@class="errloading"]')
                self.driver.switch_to.default_content()
                self.lock.release()

                if len(failed_info) >= 1:
                    return 
                time.sleep(1)
            
                login_coord = pyautogui.locateOnScreen('./files/images/world_login.png')
                if login_coord:
                    time.sleep(1)
                    x, y = pyautogui.center(login_coord)
                    pyautogui.moveTo(x=random.randint(x-10,x+10),y=random.randint(y-10,y+10),duration=0.5,tween=pyautogui.easeInOutQuart)
                    time.sleep(0.2)
                    pyautogui.leftClick()
                    return 
                else:
                    continue
            except Exception as e:
                print(e)
                watch_time += 1
                continue
    
    # 登陆移动端淘宝网页
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

    # 登录国际PC端淘宝网页
    def login_world(self):
        if self.driver == None:
            return None
        elif self.err_times <= 5:
            try:
                if self.driver.current_url == 'https://world.taobao.com/wow/z/oversea/SEO-SEM/ovs-pc-login':
                    try:
                        self.driver.maximize_window()
                    except Exception as e:
                        print(e)
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
                        time.sleep(2)
                        input_username.clear()
                        input_password.clear()

                        for u in self.cookie.username:
                            input_username.send_keys(u)
                            time.sleep(random.randint(10,70)/1000)
                        for p in self.cookie.password:
                            input_password.send_keys(p)
                            time.sleep(random.randint(10,70)/1000)
                        self.driver.switch_to.default_content()
                        time.sleep(2)
                        self.slide_world_btn()
                        self.click_world_login()
                        check_times = 0
                        while 'login' in self.driver.current_url:
                            print(self.driver.current_url)
                            # lock.acquire()
                            # self.driver.switch_to.frame(login_frame)
                            # failed_info = self.driver.find_elements_by_xpath('//*[@id="baxia-dialog-content"]')
                            # self.driver.switch_to.default_content()
                            # lock.release()
                            # if len(failed_info) >= 1 and failed_info[0].is_displayed():
                            #     time.sleep(3)
                            #     self.err_times += 1
                            #     self.driver.refresh()
                            #     return self.login_world()
                            check_times += 1
                            time.sleep(3)
                            if check_times >= 100:
                                print('最大尝试次数,判断登陆失败')
                                self.err_times += 10
                                return self.login_world()
                        time.sleep(7)
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
                    time.sleep(2)
                    self.err_times += 2
                    return self.login_world()
            except Exception as e:
                print(e)
                self.err_times += 2
                return self.login_world()
        else:
            print('failed!!!')
            return None

    def login_china(self):
        pass

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
            driver = Driver('https://world.taobao.com/wow/z/oversea/SEO-SEM/ovs-pc-login').create_driver(need_proxy=True,ua='pc')
            login = UpdateCookies(driver, cookie)
            cookies = login.login_world()
            login.update_cookie(cookies)
            del login
        except Exception as e:
            print(f'更新cookie时出错:{e}')
            continue
    os.system('taskkill /F /im chromedriver.exe')
    os.system('taskkill /F /im chrome.exe')
