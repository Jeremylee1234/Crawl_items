
import requests
from utils.utils import Proxy
from utils.logger import logger
from utils.func_classes import Err_Retry


class Request(object):
	def __init__(self):
		self.err_times = 0

	def get(self, url, headers=None, payload=None, cookies=None, proxy=None):
		if self.err_times <= 5:
			if proxy:
				proxy = Proxy().get_proxy()
			try:
				response = requests.get(url, headers=headers, params=payload, cookies=cookies, proxies=proxy)
				if response.status_code not in [500,501,502,503,504,504]:
					return response
				else:
					self.err_times += 1
					return self.get(url, headers=headers, payload=payload, cookies=cookies, proxy=proxy)
			except Exception as e:
				logger.info(f'{url}请求时出错:{e}重试')
				self.err_times += 1
				return self.get(url, headers=headers, payload=payload, cookies=cookies, proxy=proxy)
		else:
			logger.error(f'{url}get请求失败')
			self.err_times = 0
			return None

	def post(self, url, headers=None, data=None, cookies=None, proxy=None):
		if self.err_times <= 5:
			if proxy:
				proxy = Proxy().get_proxy()
			if not headers:
				headers = {
					'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Mobile Safari/537.36',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
					'Connection': 'keep-alive'
				}
			try:
				response = requests.post(url, headers=headers, data=data, cookies=cookies, proxies=proxy)
				if response.status_code not in [500,501,502,503,504,504]:
					return response
				else:
					self.err_times += 1
					return self.post(url, headers=headers, data=data, cookies=cookies, proxy=proxy)
			except Exception as e:
				logger.info(f'{url}请求时出错:{e}重试')
				self.err_times += 1
				return self.post(url, headers=headers, data=data, cookies=cookies, proxy=proxy)
		else:
			logger.error(f'{url}post请求失败')
			self.err_times = 0
			return None


