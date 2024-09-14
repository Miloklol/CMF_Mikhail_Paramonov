import pandas as pd
import math
import numpy as np



def trades(stock, ob, mb, olhc, strategy_name, price_type, T):

    pnl = 0
    pos = []

    adjusted_ob = ob.copy()
    diff_timestamp = mb['local_timestamp'].iloc[-1] - mb['local_timestamp'][0]

    ob_timestamps = adjusted_ob['local_timestamp'].values
    ask_amounts = adjusted_ob['ask_amount'].values
    bid_amounts = adjusted_ob['bid_amount'].values
    
    trade_timestamps = mb['local_timestamp'].values
    trade_sides = mb['side'].values
    trade_amounts = mb['amount'].values
    
    trade_index = 0
    num_trades = len(trade_timestamps)
    
    if strategy_name == 'Случайная стратегия':
        strategy = np.random.normal(loc=0, scale=100, size=math.ceil(diff_timestamp / T))
    elif stock == 'PEPE/USDT':
        strategy = [0] * (math.ceil(diff_timestamp / T))
        strategy[round(100 / 604 * len(strategy))] = 10000
        strategy[round(200 / 604 * len(strategy))] = -20000
        strategy[round(400 / 604 * len(strategy)) - 1] = 30000
        strategy[round(500 / 604 * len(strategy)) - 1] = 5000
        strategy[round(580 / 604 * len(strategy)) - 1] = -15000
    else:
        strategy = [0] * (math.ceil(diff_timestamp / T))
        strategy[round(100 / 604 * len(strategy))] = 30000
        strategy[round(200 / 604 * len(strategy))] = -40000
        strategy[round(270 / 604 * len(strategy)) - 1] = 30000
        strategy[round(500 / 604 * len(strategy)) - 1] = -15000

    for i in range(len(ob_timestamps)):
        while trade_index < num_trades and trade_timestamps[trade_index] < ob_timestamps[i]:
            if trade_sides[trade_index] == 'buy':
                ask_amounts[i] -= trade_amounts[trade_index]
            elif trade_sides[trade_index] == 'sell':
                bid_amounts[i] -= trade_amounts[trade_index]
            trade_index += 1

        if i == len(ob_timestamps) - 1:
            while trade_index < num_trades:
                if trade_sides[trade_index] == 'buy':
                    ask_amounts[i] -= trade_amounts[trade_index]
                elif trade_sides[trade_index] == 'sell':
                    bid_amounts[i] -= trade_amounts[trade_index]
                trade_index += 1

    adjusted_ob['ask_amount'] = ask_amounts
    adjusted_ob['bid_amount'] = bid_amounts
    adjusted_ob['ask_amount'][adjusted_ob['ask_amount'] < 0] = 0
    adjusted_ob['bid_amount'][adjusted_ob['bid_amount'] < 0] = 0
    
            
    diff_timestamp = mb['local_timestamp'].iloc[-1] - mb['local_timestamp'][0]

    num_olhc = math.ceil(diff_timestamp / T)
    for i in range(num_olhc):
        if pos == []:
            pos  = [[0, 0]]
        else:
            pos.append([0, pos[-1][1]])
        filtered_indices = (adjusted_ob['local_timestamp'] >=  adjusted_ob['local_timestamp'][0] + i * T) & (adjusted_ob['local_timestamp'] <= adjusted_ob['local_timestamp'][0] + (i + 1) * T)
        
        if price_type == 'Среднее':
            price = olhc['avg_price'].iloc[i]
        else:
            price = olhc['close'].iloc[i]
        
        pos[-1][1] = price
        
        if strategy[i] > 0:
            for index, row in adjusted_ob[filtered_indices].iterrows():
                if row['ask_price'] <= price:
                    pos[-1][0] += min(strategy[i] - pos[-1][0], row['ask_amount'])
                if strategy[i] == pos[-1][0]:
                    break
        elif strategy[i] < 0:
            for index, row in adjusted_ob[filtered_indices].iterrows():
                if row['bid_price'] >= price:
                    #print(row)
                    pos[-1][0] -= min(abs(strategy[i] - pos[-1][0]), row['bid_amount'])
                if strategy[i] == pos[-1][0]:
                    break
       
    for el in pos:
        pnl += el[0] * el[1]
    pnl -= sum(number[0] for number in pos) * olhc['close'].iloc[-1]

    vol = sum(abs(number[0]) for number in pos)


    zero_crossing = 0
    vol_temp = 0
    for el in pos:
        zero_crossing += (vol_temp > 0 and vol_temp + el[0] < 0) or (vol_temp < 0 and vol_temp + el[0] > 0)
        vol_temp += el[0]
        
    total_time_in_position = 0
    
    position_count = 0
    
    current_position = 0
    entry_time = None
    
    for i in range(len(pos)):
        contracts, timestamp = pos[i][0], i
        
        if current_position == 0:
            current_position = contracts
            entry_time = timestamp
        
        else:
            if (current_position > 0 and contracts < 0) or (current_position < 0 and contracts > 0):
                time_in_position = timestamp - entry_time
                total_time_in_position += time_in_position
                position_count += 1
                
                current_position += contracts
                
                if current_position == 0:
                    entry_time = None
            else:
                current_position += contracts

    if position_count > 0:
        average_time_in_position = total_time_in_position / position_count
    else:
        average_time_in_position = 0

    time_avg = average_time_in_position
    
    #Max drawdown
    new_ob = ob.copy()
    new_ob['candle_time'] = (new_ob['local_timestamp'] // T) * T
    
    grouped = new_ob.groupby('candle_time').agg({
        'bid_price': 'min',  
        'ask_price': 'max'   
    }).reset_index()

    cum_pnl = 0
    paid = 0
    cur_pos = 0
    l = []
    paid_max = 0
    paid_min = math.inf
    for j in range(len(pos)):
        cur_pos += pos[j][0]
        paid += pos[j][0] * pos[j][1]
        paid_max = max(paid_max, paid)
        paid_min = min(paid_min, paid)
        if cur_pos > 0:
            cum_pnl = min(cum_pnl, paid - cur_pos * grouped['bid_price'].iloc[j])
        elif cur_pos < 0:
            cum_pnl = min(cum_pnl, cur_pos * grouped['ask_price'].iloc[j] - paid)    

    returns = olhc['open'].pct_change().dropna()
    
    downside_returns = np.minimum(returns, 0)
    squared_downside_returns = downside_returns ** 2
    downside_variance = squared_downside_returns.mean()
    downside_volatility = np.std(squared_downside_returns) * math.sqrt((math.ceil(diff_timestamp / T)))
    std_dev = np.std(returns) * math.sqrt((math.ceil(diff_timestamp / T)))
    paid_max = max(paid_max, abs(paid_min))
    re = pnl / paid_max
    sortino = (re - 0.04) / downside_volatility
    sharpe = (re - 0.04) / std_dev
    print(std_dev, downside_volatility, re, paid_max)


    return pnl, vol, zero_crossing, time_avg, cum_pnl, sortino, sharpe
