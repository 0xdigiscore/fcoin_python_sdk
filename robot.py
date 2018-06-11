# coding=utf-8
# from fcoin import Fcoin
# if python3 use fcoin3
from fcoin3 import Fcoin
import threading
import time
from config import api_key
from config import api_secret
from utils import trunc

import datetime
import schedule
import random
# 初始化
fcoin = Fcoin()


# 查询账户余额
def get_balance_action(this_symbol):
    balance_info = fcoin.get_balance()
    if not balance_info:
        return
    if this_symbol == 'btc':
        balance = balance_info['data'][2]
        label = 'BTC'
    elif this_symbol == 'eth':
        balance = balance_info['data'][4]
        label = 'ETH'
    elif this_symbol == 'usdt':
        balance = balance_info['data'][7]
        label = 'USDT' 

# 获取订单列表
def get_order_list(this_symbol, this_states):
    print('开始获取订单')
    order_list = fcoin.list_orders(symbol=this_symbol, states=this_states)
    print('获取订单失败')
    if this_states == filled:
        print('已成交订单列表：')
    elif this_states == submitted:
        print('未成交订单列表：')
    for order in order_list['data']:
        print('订单ID', order['id'], '挂单价格', order['price'], '挂单数量', order['amount'], '方向', order['side'])
        if this_states == submitted:
            print('开始取消订单')
            cancel_order_action(order['id'])


# 获取订单列表第一个订单
def get_order_list_first(this_symbol, this_states):
    order_list = fcoin.list_orders(symbol=this_symbol, states=this_states)
    
    if order_list is not None and len(order_list['data']):
        order_item = order_list['data'][0]
        if order_item and this_states == submitted:
            print('发现未成交订单')
            cancel_order_action(order_item['id'])
        elif order_item and this_states == filled:
            if order_item['side'] == 'buy':
                print('开始卖出')
                order_price = float(order_item['price'])
                now_price = get_ticker(symbol)
                amount = get_avaliable_amount(now_price,'buy')
                if amount != 0:
                    if now_price > order_price:
                        sell_action(symbol, now_price, amount,order_item)
                    else:
                        buy_action(symbol, now_price, amount,order_item)    
            elif order_item['side'] == 'sell':
                print('开始买入')
                order_price = float(order_item['price'])
                now_price = get_ticker(symbol)
                amount = get_avaliable_amount(now_price,'buy')
                # 直接买入，不判断价格了
                if amount != 0:
                    if now_price < order_price or True:
                        buy_action(symbol, now_price, amount,order_item)
                    else:
                        sell_action(symbol, now_price, amount,order_item)    
    else:
        get_order_list_first(this_symbol, filled)


# 查询订单
def check_order_state(this_order_id):
    check_info = fcoin.get_order(this_order_id)
    return check_info['data']


# 买操作
def buy_action(this_symbol, this_price, this_amount,order_item):
    buy_result = fcoin.buy(this_symbol, this_price, this_amount)
    print(buy_result)
    if not buy_result:
        return None
    buy_order_id = buy_result['data']
    if buy_order_id:
        print('买单', this_price, '价格成功委托', '订单ID', buy_order_id)

    # 输出订单信息
    # print(fcoin.get_order(buy_order_id))
    return buy_order_id


# 卖操作
def sell_action(this_symbol, this_price, this_amount,order_item):
    sell_result = fcoin.sell(this_symbol, this_price, this_amount)
    if not sell_result:
        return None
    sell_order_id = sell_result['data']
    if sell_order_id:
        print('卖单', this_price, '价格成功委托', '订单ID', sell_order_id)

    print(fcoin.get_order(sell_order_id))
    return sell_order_id

    
def get_avaliable_amount(this_price,type='buy') :
    ft_num = float(fcoin.get_coin_balance('ft'))
    usdt_num = float(fcoin.get_coin_balance('usdt'))

    if ft_num < 2  or usdt_num < 2:
        avalibal_amount = 0  
    else:
        avalibal_amount = 2       
    if type == 'buy':
        
        if avalibal_amount == 0:
            sell_action('ftusdt',this_price,trunc(ft_num * 0.6,2),0)
        avalibal_amount = trunc(usdt_num / this_price,0)
        print('可提的最大数量',avalibal_amount)
    else:
        if avalibal_amount == 0:
            buy_action('ftusdt',this_price,trunc(usdt_num * 0.6,2),0)
        avalibal_amount = trunc(ft_num * this_price,0 )
        print('可卖的最大数量',avalibal_amount)
    return avalibal_amount


# 撤销订单
def cancel_order_action(this_order_id):
    cancel_info = fcoin.cancel_order(this_order_id)
    print('order_id',this_order_id,'取消信息',cancel_info)
    if cancel_info is None:
        print('撤销失败', this_order_id)
    else:
        print('成功',this_order_id)

# 获取行情
def get_ticker(this_symbol):
    ticker = fcoin.get_market_ticker(symbol)
    now_price = ticker['data']['ticker'][0]
    print('最新成交价', now_price )
    return now_price


# 授权
api_key = api_key
api_secret = api_secret
fcoin.auth(api_key, api_secret)

print('开始买卖')
# 交易类型
symbol = 'ftusdt'
# 金额
amount = 200
# 已成交
filled = 'filled'
# 未成交
submitted = 'submitted'


def buyTask():
    # 获取委托订单列表
    get_order_list_first(symbol, submitted)

def run():
    schedule.every(3).seconds.do(buyTask)
    while True:
        schedule.run_pending()
        time.sleep(3)

# 守护进程
if __name__ == '__main__':
    run()
