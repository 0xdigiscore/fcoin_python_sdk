
#!-*-coding:utf-8 -*-
#@TIME    : 2018/5/30/0030 15:18
#@Author  : linfeng
import math
import time
import numpy as np
from fcoin3 import Fcoin
from collections import defaultdict
import config
from threading import Thread
from balance import balance
import json

class app():
    def __init__(self):
        self.fcoin = Fcoin()
        self.fcoin.auth(config.api_key, config.api_secret)
      
        self.symbol = 'ethusdt'
        self.order_id = None
        self.dic_balance = defaultdict(lambda: None)
        self.time_order = time.time()

    def digits(self, num, digit):
        site = pow(10, digit)
        tmp = num * site
        tmp = math.floor(tmp) / site
        return tmp

    def get_ticker(self):
        ticker = self.fcoin.get_market_ticker(self.symbol)
        now_price = ticker['data']['ticker'][0]
        print('最新成交价', now_price)
        return now_price

    def get_blance(self):
        dic_blance = defaultdict(lambda: None)
        data = self.fcoin.get_balance()
        print(data)
        if data:
            for item in data['data']:
                dic_blance[item['currency']] = balance(float(item['available']), float(item['frozen']),float(item['balance']))
        return dic_blance    

    def process(self):
        self.dic_balance = self.get_blance()
 
        eth = self.dic_balance['eth']
    
        usdt = self.dic_balance['usdt']
        print('usdt  has ....', usdt.available, 'eth has ...', eth.available)
        price = self.digits(self.get_ticker(),2)
       
        order_list = self.fcoin.list_orders(symbol=self.symbol,states='submitted')['data']

        print('order list',order_list)
        if not order_list or len(order_list) < 3:
            if usdt:
                amount = self.digits(usdt.available / price * 0.2, 4)
                if amount > 0.01:
                    data = self.fcoin.buy(self.symbol, price, amount)
                    if data:
                        print('buy success',data)
                        self.order_id = data['data']
                        self.time_order = time.time()
                if  float(eth.available) * 0.2 > 0.01:
                    amount = self.digits(eth.available * 0.2, 4)
                    data = self.fcoin.sell(self.symbol, price, amount)  
                    if data:
                        self.time_order = time.time()
                        self.order_id = data['data']
                        print('sell success')
            else:
                print('error')
        else:
            print('system busy')
            order_list = self.fcoin.list_orders(symbol=self.symbol,states='submitted')['data']
            if len(order_list) >= 1:
                self.fcoin.cancel_order(order_list[0]['id'])

    def loop(self):
        while True:
            try:
                self.process()
            except:
                print('err')  
            time.sleep(5)  
           


if __name__ == '__main__':
    run = app()
    thread = Thread(target=run.loop)
    thread.start()
    thread.join()
    print('done')


        
            

        
    


