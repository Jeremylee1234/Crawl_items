#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import configparser

'''
读取参数模块
'''

class Config(object):
    def __init__(self, config_file='config.ini'):
        self._path = os.path.join(os.getcwd(), config_file)
        if not os.path.exists(self._path):
            raise FileNotFoundError("No such file: config.ini")
        self._config = configparser.ConfigParser()
        self._config.read(self._path, encoding='utf-8-sig')
        self._configRaw = configparser.RawConfigParser()
        self._configRaw.read(self._path, encoding='utf-8-sig')

    def get(self, section, name):
        return self._config.get(section, name)

    def getRaw(self, section, name):
        return self._configRaw.get(section, name)

    def set(self, section, param, value):
        print(self._path)
        print(self._config.set(section, param, value))
        self._configRaw.set(section, param, value)
        self._configRaw.write(open(self._path,'w',encoding='utf-8-sig'))
        return 

global_config = Config()
