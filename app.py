#!-*-coding:utf-8 -*-
#@TIME    : 2018/5/30/0030 15:18
#@Author  : linfeng
import math
import time
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

        self.symbol = 'ftusdt'
        self.order_id = None
        self.dic_balance = defaultdict(lambda: None)
        self.time_order = time.time()
        self.oldprice = self.digits(self.get_ticker(),6)

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

        ft = self.dic_balance['ft']

        usdt = self.dic_balance['usdt']
        print('usdt  has ....', usdt.available, 'ft has ...', ft.available)
        price = self.digits(self.get_ticker(),6)

        order_list = self.fcoin.list_orders(symbol=self.symbol,states='submitted')['data']

        print('order list',order_list)
        if not order_list or len(order_list) < 3:
            if usdt and abs(price/self.oldprice-1)<0.02:
                if price>self.oldprice:
                    amount = self.digits(usdt.available / price * 0.25, 2)
                    if amount > 5:
                        data = self.fcoin.buy(self.symbol, price, amount)
                        if data:
                            print('buy success',data)
                            self.order_id = data['data']
                            self.time_order = time.time()
                else:
                    if  float(ft.available) * 0.25 > 5:
                        amount = self.digits(ft.available * 0.25, 2)
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
        self.oldprice=price

    def loop(self):
        while True:
            try:
                self.process()
                print('succes')
            except:
                print('err')
            time.sleep(1)



if __name__ == '__main__':
    run = app()
    thread = Thread(target=run.loop)
    thread.start()
    thread.join()
    print('done')
