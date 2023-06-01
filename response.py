import requests
import pandas as pd
from ta.momentum import rsi
def get_all_pairs_with_usdt():
    api_url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(api_url)
    data = response.json()

    return [
        symbol['symbol']
        for symbol in data['symbols']
        if 'USDT' in symbol['symbol']
    ]

def get_candlestick_data(symbol):
    api_url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1d",
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
    return candles[:-5]


def calculate_rsi_histo_param(close_prices, period=26, modify=1):
    # Преобразование в объект Series
    close_series = pd.Series(close_prices)

    rsi_values = rsi(close_series, window=period)
    rsi_main = (rsi_values - 50) * modify
    return rsi_main.iloc[-1] # Получение последнего значения



# Получение списка торговых пар
all_pairs = get_all_pairs_with_usdt()

# Выбор первой торговой пары и выгрузка свечей
if len(all_pairs) > 0:
    for symbol in all_pairs:#[1:2]:
        candlestick_data = get_candlestick_data(symbol)
        print(f"\nCandlestick data for {symbol}:")
        #print(candlestick_data)

        # Извлечение цен закрытия
        close_prices = [candle[3] for candle in candlestick_data]

        # Расчет значения параметра индикатора для последней свечи
        last_rsi_histo_param = calculate_rsi_histo_param(close_prices)
        print('RSI HistoAlert Strategy', last_rsi_histo_param)

