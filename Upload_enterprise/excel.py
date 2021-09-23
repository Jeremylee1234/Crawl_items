#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xlrd

class Excel(object):
  """
  excel文件操作类
  """
  def __init__(self, path:str, startrow=1, source=''):
    """
    path:excel文件路径
    sheetname:表名,默认为第一个表
    startrow:标题行所在行数,默认为1
    source:来源标记
    """
    self.wb = xlrd.open_workbook(path)
    self.ws = self.wb.sheet_by_index(0)
    self.startrow = startrow
    self.source = source

  def read_sheet(self):
    """
    读取sheet并返回内容
    """
    nrows = self.ws.nrows
    titles = self.ws.row_values(self.startrow - 1)
    ncolumns = len(titles)
    for i in range(self.startrow, nrows):
      row = self.ws.row_values(i)
      if len(row) >= ncolumns:
        item = { 'source': self.source }
        for j in range(ncolumns):
          item[titles[j]] = row[j]
        yield item

if __name__ == '__main__':
  path = './tyc-批发和零售业-四川省+山东省+甘肃省+海南省+河北省+河南省+内蒙古自治区+新疆维吾尔自治区+福建省+湖北省+吉林省+黑龙江省+安徽省+重庆市+山西省+贵州省+-30000-万-有邮箱-4087-max-20210915164143-.xls'
  excel = Excel(path,3)
  for i in excel.read_sheet():
    print(i)


