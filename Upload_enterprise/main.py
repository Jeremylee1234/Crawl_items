#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from utils import formate_data
from pipeline import pipeline
from excel import Excel

def main():
    folderpath = './files/'
    for filename in os.listdir(folderpath):
        filepath = folderpath + filename
        if 'tyc' in filepath:
            excel = Excel(filepath, 3, 'tyc')
        else:
            excel = Excel(filepath, 2, 'qcc')
        for item in excel.read_sheet():
            item = formate_data(item)
            pipe = pipeline(item,'；')
            if not pipe:
                print(item)
        

if __name__ == '__main__':
    main()