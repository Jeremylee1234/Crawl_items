from utils.logger import logger
import time

class Err_Retry(object):
	def __init__(self):
		self.err_times = 0
		self.correct_times = 0
	
	def _retry(job:str, times:int, sleep_time:int):
		"""
		重试装饰器
		job:所执行任务文字描述
		times:最大尝试次数
		sleep_time:每次尝试失败休息时长
		"""
		def wrapper(func):
			def track_func(self, *args, **kwargs):
				if self.err_times <= times:
					try:
						result = func(self, *args, **kwargs)
					except Exception as e:
						print(f'{job}第{self.err_times}次,出现异常:{e}')
						logger.info(f'{job}第{self.err_times}次出现异常:{e}')
						self.err_times += 1
						time.sleep(sleep_time)
						return track_func(self, *args, **kwargs)
					else:
						self.err_times = 0
						return result
				else:
					self.err_times = 0
					print(f'{job}放弃执行')
					logger.info(f'{job}放弃执行')
					return None
			return track_func
		return wrapper
	
	_retry = staticmethod(_retry)

