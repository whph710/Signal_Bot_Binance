
def get_all_pairs_with_usdt():
    api_url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(api_url)
    data = response.json()

    return [
        symbol['symbol']
        for symbol in data['symbols']
        if 'USDT' in symbol['symbol']
    ]
#####################################################################################################################
def get_candlestick_data(symbol):
    api_url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "4h",
        "limit": 70
    }
    response = requests.get(api_url, params=params)
    data = response.json()

    candles = []
    for item in data:
        open_price = float(item[1])
        high_price = float(item[2])
        low_price = float(item[3])
        close_price = float(item[4])
        volume = float(item[5])
        candle = [open_price, high_price, low_price, close_price, volume]
        candles.append(candle)
    return candles[:-1]
# края от 15 до 40
###################################################################################################################
def calculate_rsi_histo_param(close_prices, period=26, modify=1):
    # Преобразование в объект Series
    close_series = pd.Series(close_prices)

    rsi_values = rsi(close_series, window=period)
    rsi_main = (rsi_values - 50) * modify
    return rsi_main.iloc[-1] # Получение последнего значения

#####################################################################################################################
import requests
import pandas as pd
import numpy as np
from ta.momentum import rsi



def connors_rsi(close_prices, len_rsi=6, len_updown=2, len_roc=100):
    # Преобразование в объект Series
    close_series = pd.Series(close_prices)

    # Расчет RSI
    rsi_values = rsi(close_series, window=len_rsi)

    # Расчет updownrsi
    updown_series = close_series.diff().apply(lambda x: 1 if x > 0 else -1)
    updown_rsi_values = rsi(updown_series, window=len_updown)

    # Расчет percentrank
    roc_values = close_series.pct_change()
    percentrank_values = roc_values.rolling(window=len_roc, min_periods=1).apply(lambda x: sum(x > 0) / len(x))

    # Расчет CRSI
    crsi_values = np.mean([rsi_values, updown_rsi_values, percentrank_values], axis=0)

    return crsi_values[-1]
###################################################################################################################
import pandas as pd
import ta

def calculate_cvd_ma(candlestick_data, ma_len=52):
    cvd = []
    for data in candlestick_data:
        open_price, high_price, low_price, close_price, volume = data
        if open_price < close_price:
            cvd.append(volume)
        else:
            cvd.append(-volume)
    cvd = pd.Series(cvd)
    ma = cvd.rolling(window=ma_len).mean()
    return cvd.iloc[-1], ma.iloc[-1]
###################################################################################################################
# Получение списка торговых пар
all_pairs = get_all_pairs_with_usdt()

# Выбор первой торговой пары и выгрузка свечей
if len(all_pairs) > 0:
    for symbol in all_pairs[1:]:
        candlestick_data = get_candlestick_data(symbol)
        print(f"\nCandlestick data for {symbol}:")
        print(candlestick_data)

        # Извлечение цен закрытия
        close_prices = [candle[3] for candle in candlestick_data]

        # Расчет значения параметра индикатора для последней свечи
        last_rsi_histo_param = calculate_rsi_histo_param(close_prices)
        print('RSI HistoAlert Strategy', last_rsi_histo_param)
        print('RSI Connors Strategy', connors_rsi(close_prices))
        print('CVD MA Strategy', calculate_cvd_ma(candlestick_data))

