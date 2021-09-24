from selenium.common.exceptions import TimeoutException
from crawlers.taobao.verify import update_all_cookies
from pipeline import process_item,upload_item
from utils.func_classes import Err_Retry
from utils.create_driver import Driver
from utils.config import global_config
from urllib.request import quote
from utils.logger import logger
from data_formate import Item
from utils import utils
from lxml import etree
import alchemy as db
import consts
import random
import time
import os
import re

CHANGE_ACCOUNT_LEVEL = int(global_config.get('config','change_account_level'))
DISABLE_ACCOUNT_LEVEL = int(global_config.get('config','disable_account_levle'))
SITE_ID = 1

class Get_urls(object):
    def __init__(self, repeat_set) -> None:
        self.err_times = 0
        self.repeat_set = repeat_set

    def access_page(self, province, category, page, driver=None):
        """
        创建浏览器窗口并尝试访问执行一级页面,
        返回值:
        None:创建失败,请后续处理跳过None
        driver:创建成功
        """
        if not driver:
            driver = Driver('https://sf.taobao.com/').create_driver() # 此后需要修改为need_proxy及css禁用
        if self.err_times <= 5:
            if driver == None:
                # 判断在多次尝试创建浏览器窗口后失败
                self.err_times = 0
                return None
            url = 'https://sf.taobao.com/item_list.htm?category=' + category[2] + '&auction_source=0&province=' + quote(province[0], encoding='gbk') + '&st_param=4&auction_start_seg=-1&page=' + str(page)
            try:
                if url != driver.current_url:
                    driver.get(url)
                if '阿里拍卖' in driver.title:
                    # 判断跳转到正常一级页面
                    return driver
                elif '我喜欢' in driver.title:
                    # 判断跳转到登陆界面
                    self.err_times += 1
                    driver.quit()
                    return self.access_page(province, category, page)
                elif not utils.isElementExist(driver, '//div'):
                    # 判断网络问题页面加载失败
                    self.err_times += 1
                    return self.access_page(province, category, page, driver)
                else:
                    # 其他未知错误
                    self.err_times += 1
                    driver.quit()
                    return self.access_page(province, category, page)
            except TimeoutException:
                # 判断浏览器加载超时,作正常页面处理
                if '阿里拍卖' in driver.title:
                    # 判断跳转到正常一级页面
                    return driver
                elif '我喜欢' in driver.title:
                    # 判断跳转到登陆界面
                    self.err_times += 1
                    driver.quit()
                    return self.access_page(province, category, page)
                elif not utils.isElementExist(driver, '//div'):
                    # 判断网络问题页面加载失败
                    self.err_times += 1
                    return self.access_page(province, category, page, driver)
                else:
                    # 其他未知错误
                    self.err_times += 1
                    driver.quit()
                    return self.access_page(province, category, page)
            except Exception as e:
                # 其他错误,处理错误
                logger.info(SITE_ID,'尝试访问ali-sf二级页面失败,重试',e,url)
                self.err_times += 1
                return None

    def parse_urls(self, province, category, driver):
        try:
            if driver == None:
                return []
            else:
                pattern_sf = re.compile(r'^.*sf-item.taobao.com/sf_item/([0-9]+).htm/?.*?$')
                results = []
                datas = driver.find_elements_by_xpath('//div[@class="sf-item-list"]/ul[1]/li/a')
                for data in datas:
                    try:
                        item = Item(str(re.match(pattern_sf, data.get_attribute('href')).group(1)), SITE_ID)
                        item.url = data.get_attribute('href')
                        item.title = utils.clean(data.find_element_by_xpath('./div[contains(@class,"header-section")]/p').get_attribute('textContent'))
                        item.category = category[0]
                        item.categoryId = category[3]
                        item.province = province[0]
                        item.provinceId = province[1]
                        if not item.repeat in self.repeat_set:
                            self.repeat_set.append(item.repeat)
                            results.append(item)
                    except Exception as e:
                        logger.error(SITE_ID,f'解析ali-sf一级页面某项时出错',e)
                        continue
                return results
        except Exception as e:
            logger.error(SITE_ID,f'解析ali-sf一级页面整个页面时出错',e)
            return []

class Parse_detail(object):
	def __init__(self) -> None:
		self.err_times = 0
		self.correct_count = 0
		self.useful_cookies = db.get_cookies(SITE_ID,True)

		if len(self.useful_cookies) >= 1:
			self.cookie_obj = random.choice(self.useful_cookies)
			self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie, '.taobao.com')
			self.session = utils.get_session(consts.sf_pc_detail_headers, self.cookie)
		else:
			update_all_cookies()
			self.useful_cookies = db.get_cookies(SITE_ID,True)
			self.cookie_obj = random.choice(self.useful_cookies)
			self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie, '.taobao.com')
			self.session = utils.get_session(consts.sf_pc_detail_headers, self.cookie)

	def parse_detail(self, item:Item):
		if self.err_times <= 1:
			response = self.session.get(url=item.url)
			if response.status_code == 200:
				try:
					selector = etree.HTML(response.text)
					item.phase = utils.get_phase(utils.clean(utils.outFirst(selector.xpath('//span[@class="item-status"]/text()'))))
					item.images = str(['https:' + url for url in selector.xpath('//ul[@id="J_UlThumb"]//img/@src')])
					item.current_price = utils.get_money(utils.outFirst(selector.xpath('//span[contains(@class,"current-price")]/em/text()')))
					item.people_contacter = utils.clean(utils.list_to_str(selector.xpath('//div[contains(@class,"contact-unit")]//text()')))
					item.location = utils.clean(utils.list_to_str(selector.xpath('//div[contains(@class,"item-address")]//text()')))
					item.lng, item.lat = utils.parse_coordinate(utils.outFirst(selector.xpath('//input[@id="J_Coordinate"]/@value')))
					item.start_time = utils.formate_timestamp(utils.outFirst(selector.xpath('//li[@id="sf-countdown"]/@data-start')))
					item.end_time = utils.formate_timestamp(utils.outFirst(selector.xpath('//li[@id="sf-countdown"]/@data-end')))
					item.status = 123
					infos = selector.xpath('//tbody[@id="J_HoverShow"]//td')
					for info in infos:
						if '保证金' in info:
							item.margin = utils.get_money(info)
						if '程序' in info:
							item.phase = utils.get_phase(info)
						if '评估价' in info or '市场价' in info:
							item.appraisal_price = utils.get_money(info)
						if '起拍价' in info or '变卖价' in info or '起始价' in info:
							item.starting_price = utils.get_money(info)
						if not item.current_price and '变卖预缴款' in info:
							item.current_price = utils.get_money(info)
						if '竞价周期' in info or '变卖周期' in info:
							item.bidding_period = info.replace('竞价周期:','')
						if '延时周期' in info:
							item.delay_period = info.replace('延时周期:','')
						if '优先购买权人' in info:
							item.privileged_people = info.replace('优先购买权人:','')
						if '加价幅度' in info:
							item['markup'] = info.replace('加价幅度:','')
					
					url1 = utils.outFirst(selector.xpath('//div[@id="J_desc"]/@data-from'))
					if isinstance(url1, str):
						if 'http' not in url1:
							url1 = 'https:' + url1
						response = self.session.get(url1)
						text = utils.clean(utils.list_to_str(utils.clean_tags(response.text)))
						if '\\u' in text:
							text = text.encode('utf-8').decode('unicode_escape')
						item['intro'] += text

					url2 = utils.outFirst(selector.xpath('//div[@id="J_NoticeDetail"]/@data-from'))
					if isinstance(url2, str):
						if 'http' not in url2:
							url2 = 'https:' + url2
						response = self.session.get(url2)
						text = utils.clean(utils.list_to_str(utils.clean_tags(response.text)))
						if '\\u' in text:
							text = text.encode('utf-8').decode('unicode_escape')
						item['intro'] += text

					url3 = utils.outFirst(selector.xpath('//div[@id="J_ItemNotice"]/@data-from'))
					if isinstance(url3, str):
						if 'http' not in url3:
							url3 = 'https:' + url3
						response = self.session.get(url3)
						text = text.clean(text.list_to_str(text.clean_tags(response.text)))
						if '\\u' in text:
							text = text.encode('utf-8').decode('unicode_escape')
						item['intro'] += text

					if url1 == None and url2 == None and url3 == None:
						# 判定当前页面请求失败,cookie错误次数+1
						self.cookie_obj['err_times'] += 1
						self.err_times = 0
						time.sleep(15)
						return 0, item
					else:
						# 判定详情页请求成功,cookiejiji及类的错误次数归零
						self.cookie_obj['err_times'] = 0
						self.err_times = 0
						return 1, item
				except Exception as e:
					logger.info(SITE_ID,'获取详情页时出错',e,item.url)
					self.err_times += 1
					return self.parse_detail(item)
			else:
				self.cookie_obj['err_times'] += 1
				self.err_times += 1
				return 0, item
		else:
			logger.info(SITE_ID,'放弃获取详情页',None,item.url)
			self.err_times += 1
			return 0, item

	def update_item(self, item:Item):
		if self.err_times <= 1:
			response = self.session.get(url=item.url)
			if response.status_code == 200:
				try:
					selector = etree.HTML(response.text)
					item.status = 123
				except:
					pass

	def expand_items(self, items:list):
		while len(items) > 0:
			item = items.pop()
			if len(self.useful_cookies) <= 1:
				update_all_cookies()
				self.__init__()

			if self.cookie_obj['err_times'] >= DISABLE_ACCOUNT_LEVEL:
				self.useful_cookies.remove(self.cookie_obj)
				db.disable_cookie(self.cookie_obj)
				self.cookie_obj = random.choice(self.useful_cookies)
				self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie, '.taobao.com')
				self.session = utils.get_session(consts.sf_pc_detail_headers, self.cookie)

			if self.correct_count >= CHANGE_ACCOUNT_LEVEL:
				self.correct_count = 0
				self.cookie_obj = random.choice(self.useful_cookies)
				self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie, '.taobao.com')
				self.session = utils.get_session(consts.sf_pc_detail_headers, self.cookie)
			
			if self.err_times <= 4:
				status_code, item = self.parse_detail(item)
				if status_code == 0:
					items.append(item)
					continue
				elif status_code == 1:
					self.correct_count += 1
					yield item
			else:
				self.err_times = 0
				logger.info(SITE_ID,'ali-sf的详情页最终放弃请求',None,item.url)
				continue

class Ali_sf(Err_Retry):
	def __init__(self):
		super().__init__()

	def _run_(self):
		# all_province, all_city, all_county = db.get_citys()
		# 新项目的爬取
		for province in consts.sf_province:
			# os.system('taskkill /F /im chromedriver.exe')
			# os.system('taskkill /F /im chrome.exe')
			repeat_set = db.get_items_repeat(1, province[1])
			get_urls = Get_urls(repeat_set)
			for category in consts.sf_category:
				parser = Parse_detail()
				for page in range(1,category[1]+1): # 爬取每个种类指定页数的内容
					driver = get_urls.access_page(province, category, page)
					items = get_urls.parse_urls(province, category, driver)
					for item in parser.expand_items(items):
						item = process_item(item)
						upload_item(item)
