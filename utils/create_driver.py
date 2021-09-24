#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from func_timeout import func_set_timeout
from selenium.common.exceptions import TimeoutException
from utils.del_js import get_js_code
from selenium import webdriver
from utils.utils import Proxy
from utils.func_classes import Err_Retry
import time
import json

class Driver(Err_Retry):
    """
    控制创建selenium浏览器窗口的类
    """

    def __init__(self, site):
        super().__init__()
        self.site = site

    @Err_Retry._retry('创建浏览器窗口',3,5)
    @func_set_timeout(60)  #此处修改了库文件以实现超时异常则关闭driver
    def create_driver(self, need_proxy=False, cookie=False, ua='pc', css=False):
        """
        创建浏览器窗口
        need_proxy:是否需要设置代理
        cookie:是否需要设置cookie
        ua:使用什么平台的代理,'pc'或'mobile'
        css:是否禁用浏览器css
        """
        if css:
            prefs = {
                "webrtc.ip_handling_policy": "disable_non_proxied_udp",
                "webrtc.multiple_routes_enabled": False,
                "webrtc.nonproxied_udp_enabled": False
            }
        else:
            prefs = {
                'profile.default_content_setting_values': {
                    'images': 2,
                    'stylesheet': 2       #2即为禁用的意思
                },
                "webrtc.ip_handling_policy": "disable_non_proxied_udp",
                "webrtc.multiple_routes_enabled": False,
                "webrtc.nonproxied_udp_enabled": False
            }
        if ua == 'pc':
            ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64'
        elif ua == 'mobile':
            ua = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36 Edg/91.0.864.64'
        else:
            ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64'

        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument("--log-level=OFF")  #修改debug信息等级
        options.add_argument('disable-infobars')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-extensions")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument(f'user-agent={ ua }')
        options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        # options.add_argument("disable-blink-features=AutomationControlled")
        options.add_experimental_option('prefs', prefs)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        if need_proxy:
            ip, proxy = Proxy().get_proxy()
            options.add_argument(f'--proxy-server=http://{ ip }') #设置chromedriver代理,或需要省略

        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": get_js_code()})
        driver.set_page_load_timeout(15)

        try:
            driver.get(self.site)
            time.sleep(1)
            if cookie:
                for c in json.loads(cookie.cookie):
                    driver.add_cookie(c)

            return driver
        except TimeoutException:
            print('timeout to stop homepage javascript')
            driver.execute_script('window.stop()')
            time.sleep(1)
            if cookie:
                for c in json.loads(cookie.cookie):
                    driver.add_cookie(c)
            return driver
        except Exception as e:
            print(e)
            driver.quit()
            return 

if __name__ == "__main__":
    driver = Driver('https://www.baidu.com')
    dr = driver.create_driver()
    print(dr)
