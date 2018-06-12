import math
import time
import talib
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

    # 精度控制，直接抹除多余位数，非四舍五入
    def digits(self, num, digit):
        site = pow(10, digit)
        tmp = num * site
        tmp = math.floor(tmp) / site
        return tmp

    # 获取行情
    def get_ticker(self):
        ticker = self.fcoin.get_market_ticker(self.symbol)
        now_price = ticker['data']['ticker'][0]
        print('最新成交价', now_price)
        return now_price

    #获取余额
    def get_blance(self):
        dic_blance = defaultdict(lambda: None)
        data = self.fcoin.get_balance()
        if data:
            for item in data['data']:
                dic_blance[item['currency']] = balance(float(item['available']), float(item['frozen']),float(item['balance']))
        return dic_blance    

    # 开始刷单
    def process(self):
        self.dic_balance = self.get_blance()
        '''
            判断大饼持仓量，到设定值停止买入。
        '''
        eth = self.dic_balance['eth']
        '''
           usdt持仓量
        '''
        usdt = self.dic_balance['usdt']
        print('usdt余额为....', usdt.available, 'eth余额为...', eth.available)
        price = self.digits(self.get_ticker(),2)
        print('最新价格为: ',price)
        order_list = self.fcoin.list_orders(symbol=self.symbol,states='submitted')['data']
        # 如果usdt持仓量比较足，那就买
        if order_list and len(order_list) < 3:
            if usdt:
                amount = self.digits(usdt.available / price * 0.2, 4)
                if amount > 0.01:
                    data = self.fcoin.buy(self.symbol, price, amount)
                    if data:
                        print('挂买单成功',data)
                        self.order_id = data['data']
                        self.time_order = time.time()
                if  float(eth.available) * 0.2 > 0.01:
                    amount = self.digits(eth.available * 0.2, 4)
                    data = self.fcoin.sell(self.symbol, price, amount)  
                    if data:
                        self.time_order = time.time()
                        self.order_id = data['data']
                        print('卖单卖委托成功')
            else:
                print('查询余额错误')
        else:
           if time.time() - self.time_order >= 5:
                print('如果时间大于5秒，则判断交易超时，超时取消订单')
                print('order list为',order_list)
                self.fcoin.cancel_order(order_list[0])

    def loop(self):
        while True:
            self.process()


if __name__ == '__main__':
    run = app()
    thread = Thread(target=run.loop)
    thread.start()
    thread.join()
    print('done')


        
            

        
    


