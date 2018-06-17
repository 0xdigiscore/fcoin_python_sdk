#!-*-coding:utf-8 -*-
#@TIME    : 2018/5/30/0030 15:18
#@Author  : linfeng

import math
import time
from fcoin3 import Fcoin
from collections import defaultdict
import config


class FtGet:
    def __init__(self):
        self.fcoin = Fcoin()
        self.fcoin.auth(config.api_key, config.api_secret)
        self.symbol = 'ftusdt'
        self.now_balance = None
        self.buy_balance = None

    ## 获取最新成交价
    def get_ticker(self):
        ticker = self.fcoin.get_market_ticker(self.symbol)
        now_price = ticker['data']['ticker'][0]
        print('最新成交价', now_price)
        return now_price

    def process(self):
        pass
        
    
    def loop(self):
        while True:
            try:
                self.process()
            except:
                print('err')  
            time.sleep(5)
        
