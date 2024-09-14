import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import math
import numpy as np
from graphs import OLHC, olhc_plot
from stats import trades


def update_chart():
    # Получаем выбранные значения
    selected_stock = stock_var.get()
    selected_candle_length = int(candle_length_var.get())
    selected_strategy = strategy_var.get()
    selected_price = price_var.get()
    
    # Преобразуем данные (предполагаем, что book_data и trade_data загружены)
    if selected_stock == 'PEPE/USDT':
        olhc_data = OLHC(ob_pepe, mb_pepe, selected_candle_length)
    else:
        olhc_data = OLHC(ob_doge, mb_doge, selected_candle_length)

    
    # Построим график свечей
    fig = olhc_plot(olhc_data, selected_candle_length)
    
    # Отображаем график в tkinter
    for widget in chart_frame.winfo_children():
        widget.destroy()
    
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Рассчитываем прибыль и коэффициенты
    if selected_stock == 'PEPE/USDT':
        pnl, vol, zero_crossing, time_avg, cum_pnl, sortino, sharpe = trades(selected_stock, ob_pepe, mb_pepe, olhc_data, selected_strategy, selected_price, selected_candle_length)
    else:
        pnl, vol, zero_crossing, time_avg, cum_pnl, sortino, sharpe = trades(selected_stock, ob_doge, mb_doge, olhc_data, selected_strategy, selected_price, selected_candle_length)
    
    # Обновляем текст с результатами
    profit_label.config(text=f"Прибыль: {pnl}")
    sortino_label.config(text=f"Коэффициент Сортино: {sortino}")
    sharpe_label.config(text=f"Коэффициент Шарпа: {sharpe}")
    volume_label.config(text=f"Проторгованный объем: {vol}")
    max_drawdown_label.config(text=f"Максимальная просадка: {cum_pnl}")
    average_holding_time_label.config(text=f"Среднее время в позиции: {time_avg}")
    number_of_positions_flip_label.config(text=f"Количество переходов позиции через 0: {zero_crossing}")



ob_pepe = pd.read_csv('bbo_1000pepeusdt.csv')
mb_pepe = pd.read_csv('trades_1000pepeusdt.csv')
ob_doge = pd.read_csv('bbo_dogeusdt.csv')
mb_doge = pd.read_csv('trades_dogeusdt.csv')


# Инициализация tkinter
root = tk.Tk()
root.title("Торговый симулятор")

# Переменные для хранения значений
stock_var = tk.StringVar()
candle_length_var = tk.StringVar()
strategy_var = tk.StringVar()
price_var = tk.StringVar()

# Пример данных (замените на реальные акции, стратегии)
stock_list = ['PEPE/USDT', 'DOGE/USDT']
strategies = ['Случайная стратегия', 'Стратегия, знающая будущее']
prices = ['Средняя', 'Цена закрытия']

# Выбор акции
ttk.Label(root, text="Выберите акцию").grid(column=0, row=0)
stock_menu = ttk.Combobox(root, textvariable=stock_var, values=stock_list)
stock_menu.grid(column=1, row=0)
stock_menu.current(0)

# Выбор длины свечи
ttk.Label(root, text="Длина свечи").grid(column=0, row=1)
candle_length_var = ttk.Entry()
candle_length_var.grid(column=1, row=1)

# Выбор стратегии
ttk.Label(root, text="Выберите стратегию").grid(column=0, row=2)
strategy_menu = ttk.Combobox(root, textvariable=strategy_var, values=strategies)
strategy_menu.grid(column=1, row=2)
strategy_menu.current(0)

ttk.Label(root, text="Выберите цену покупки").grid(column=0, row=3)
stock_menu = ttk.Combobox(root, textvariable=price_var, values=prices)
stock_menu.grid(column=1, row=3)
stock_menu.current(0)

# Кнопка обновления
update_button = ttk.Button(root, text="Обновить", command=update_chart)
update_button.grid(column=1, row=4)

# Фрейм для графика
chart_frame = tk.Frame(root)
chart_frame.grid(column=0, row=5, columnspan=2)

# Метки для прибыли и коэффициентов

volume_label = ttk.Label(root, text="Проторгованный объем: 0")
volume_label.grid(column=0, row=6)

sortino_label = ttk.Label(root, text="Коэффициент Сортино: 0")
sortino_label.grid(column=0, row=7)

sharpe_label = ttk.Label(root, text="Коэффициент Шарпа: 0")
sharpe_label.grid(column=0, row=8)

max_drawdown_label = ttk.Label(root, text="Максимальная просадка: 0")
max_drawdown_label.grid(column=0, row=9)

average_holding_time_label = ttk.Label(root, text="Среднее время в позиции: 0")
average_holding_time_label.grid(column=0, row=10)

number_of_positions_flip_label = ttk.Label(root, text="Количество переходов позиции через 0: 0")
number_of_positions_flip_label.grid(column=0, row=11)

profit_label = ttk.Label(root, text="Прибыль: 0")
profit_label.grid(column=0, row=12)

# Запуск приложения
root.mainloop()