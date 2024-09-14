import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import datetime


def OLHC(ob, mb, T):

    opens = mb['local_timestamp'][0]
    diff_timestamp = mb['local_timestamp'].iloc[-1] - mb['local_timestamp'][0]
    num_olhc = math.ceil(diff_timestamp / T)
    df_olhc = pd.DataFrame(columns=['open', 'low', 'high', 'close', 'avg_price', 'volume', 'local_timestamp'])
    for i in range(num_olhc):
        filtered_indices = (mb['local_timestamp'] >=  mb['local_timestamp'][0] + i * T) & (mb['local_timestamp'] <= mb['local_timestamp'][0] + (i + 1) * T)

        
        if not filtered_indices.empty:
            temp_df = mb[filtered_indices]
            min_price = temp_df['price'].min()
            max_price = temp_df['price'].max()
            vol = temp_df['amount'].sum()
            avg_price = (temp_df['price'] * temp_df['amount']).sum() / vol
            try:
                open_price = temp_df['price'].iloc[0]
            except IndexError:
                print(temp_df)
            close_price = temp_df['price'].iloc[-1]
            df_olhc.loc[len(df_olhc)] = [open_price, min_price, max_price, close_price, avg_price, vol, opens + T * (i + 0.5)]

           
        else:
            try:
                price = df_olhc['close'].iloc[-1]
                df_olhc.loc[len(df_olhc)] = [price, price, price, price, price, 0, opens + T * (i + 0.5)]
            except IndexError:
                price = mb['price'].iloc[0]
                df_olhc.loc[len(df_olhc)] = [price, price, price, price, price, 0, opens + T * (i + 0.5)]
    
    def convert_timestamp(microseconds):
        seconds = microseconds / 1_000_000  # Если временные метки в микросекундах
        return datetime.datetime.utcfromtimestamp(seconds)

    # Применяем функцию ко всему столбцу
    df_olhc['local_timestamp'] = df_olhc['local_timestamp'].apply(convert_timestamp)
    
    df_olhc.set_index('local_timestamp', inplace=True)

    return df_olhc


def olhc_plot(df, T):
    add_avg_price = mpf.make_addplot(df['avg_price'], color='blue', linestyle='-')    
    fig, axlist = mpf.plot(df, type='candle', style='binance', volume=True, returnfig=True, addplot=add_avg_price)
   
    return fig