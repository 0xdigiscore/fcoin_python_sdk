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
        self.symbol = config.socket+config.blc
        self.order_id = None
        self.dic_balance = defaultdict(lambda: None)
        self.time_order = time.time()
        self.oldprice = self.get_prices()
        self.socket_sxf=0.0
        self.blc_sxf=0.0
        self.begin_balance=self.get_blance()

    def get_prices(self):
        i=2
        prices=[]
        while i>0:
           prices.append(self.digits(self.get_ticker(),6))
           i-=1
           time.sleep(1)
        return prices

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
        if data:
            for item in data['data']:
                dic_blance[item['currency']] = balance(float(item['available']), float(item['frozen']),float(item['balance']))
        return dic_blance

    def process(self):
        price = self.digits(self.get_ticker(),6)

        self.oldprice.append(price)

        p1=self.oldprice[len(self.oldprice)-2]
        p2=self.oldprice[len(self.oldprice)-3]

        self.dic_balance = self.get_blance()

        socket = self.dic_balance[config.socket]

        blc = self.dic_balance[config.blc]

        print(config.blc+'_now  has ....', blc.balance, config.socket+'_now has ...', socket.balance)
        print(config.blc+'_sxf  has ....', self.blc_sxf, config.socket+'_sxf has ...', self.socket_sxf)
        print(config.blc+'_begin  has ....', self.begin_balance[config.blc].balance, config.socket+'_begin has ...', self.begin_balance[config.socket].balance)
        print(config.blc+'_all_now  has ....', blc.balance+self.blc_sxf, config.socket+'_all_now has ...', socket.balance+self.socket_sxf)

        order_list = self.fcoin.list_orders(symbol=self.symbol,states='submitted')['data']

        if not order_list or len(order_list) < 2:
            if blc and abs(price/self.oldprice[len(self.oldprice)-2]-1)<0.02:
                if price*2>p1+p2:
                    amount = self.digits(blc.available / price * 0.25, 2)
                    if amount > 0:
                        data = self.fcoin.buy(self.symbol, price, amount)
                        if data:
                            print('buy success',data)
                            self.socket_sxf += amount*0.001
                            self.order_id = data['data']
                            self.time_order = time.time()
                else:
                    if  float(socket.available) * 0.25 > 0:
                        amount = self.digits(socket.available * 0.25, 2)
                        data = self.fcoin.sell(self.symbol, price, amount)
                        if data:
                            self.blc_sxf += amount*price*0.001
                            self.time_order = time.time()
                            self.order_id = data['data']
                            print('sell success')
            else:
                print('error')
        else:
            print('system busy')
            if len(order_list) >= 1:
                data=self.fcoin.cancel_order(order_list[len(order_list)-1]['id'])
                print(order_list[len(order_list)-1])
                if data:
                    if order_list[len(order_list)-1]['side'] == 'buy' and order_list[len(order_list)-1]['symbol'] == self.symbol:
                        self.socket._sxf -= float(order_list[len(order_list)-1]['amount'])*0.001
                    elif order_list[len(order_list)-1]['side'] == 'sell' and order_list[len(order_list)-1]['symbol'] == self.symbol:
                        self.blc_sxf -= float(order_list[len(order_list)-1]['amount'])*float(order_list[len(order_list)-1]['price'])*0.001



    def loop(self):
        while True:
            try:
                self.process()
                print('succes')
            except:
                print('err')
            time.sleep(2)



if __name__ == '__main__':
    run = app()
    thread = Thread(target=run.loop)
    thread.start()
    thread.join()
    print('done')
