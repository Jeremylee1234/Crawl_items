import alchemy as db
import datetime
'''
日志模块
'''
class Logger(object):
    """
    日志类
    """
    def __init__(self):
        pass

    def info(self, siteid, job=None, exception=None, info=None):
        """
        创建info类日志,err_level=0
        """
        new_log = db.Crawl_Log(
            job = job,
            info = info,
            exception = exception,
            err_level = 0,
            occur_time = datetime.datetime.now(),
            siteId = siteid
        )
        db.db_session.add(new_log)
        db.db_session.commit()
    
    def debug(self, siteid, job=None, exception=None, info=None):
        """
        创建debug类日志,err_level=1
        """
        new_log = db.Crawl_Log(
            job = job,
            info = info,
            exception = exception,
            err_level = 1,
            occur_time = datetime.datetime.now(),
            siteId = siteid
        )
        db.db_session.add(new_log)
        db.db_session.commit()
    
    def error(self, siteid, job=None, exception=None, info=None):
        """
        创建error类日志,err_level=2
        """
        new_log = db.Crawl_Log(
            job = job,
            info = info,
            exception = exception,
            err_level = 2,
            occur_time = datetime.datetime.now(),
            siteId = siteid
        )
        db.db_session.add(new_log)
        db.db_session.commit()

logger = Logger()
