import requests
import pprint


def get_stock_data(ticker):
    stock_name = ticker
    url = "https://api-invest.tinkoff.ru/trading/stocks/get?ticker=" + str(stock_name)

    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"}
    req = requests.get(url, headers=headers)
    resp = req.json()

    stock_data = resp["payload"]


    #pprint.pprint(resp)
    return stock_data


def get_ticker_price(ticker):
    """
    This function get data from https://api-invest.tinkoff.ru/trading/stocks/get?ticker api and return ticker price
    return current price of the ticker
    """
    stock_data = get_stock_data(ticker)
    current_price_data = stock_data['price']
    current_price = current_price_data['value']

    return current_price


def get_ticker_lot_size(ticker):
    """
    This function get data from https://api-invest.tinkoff.ru/trading/stocks/get?ticker api
    return ticker lot

    """
    stock_data = get_stock_data(ticker)
    lot_size_data = stock_data['symbol']
    lot_size = lot_size_data['lotSize']

    return lot_size


def get_ticker_min_price_increment(ticker):
    """
    This function get data from https://api-invest.tinkoff.ru/trading/stocks/get?ticker api
    return minimum price increment

    """
    stock_data = get_stock_data(ticker)
    min_price_increment_data = stock_data['symbol']
    min_price_increment = min_price_increment_data['minPriceIncrement']

    return min_price_increment


def get_ticker_currency(ticker):
    """
    This function get data from https://api-invest.tinkoff.ru/trading/stocks/get?ticker api
    return ticker currency

    """
    stock_data = get_stock_data(ticker)
    current_price_data = stock_data['price']
    ticker_currency = current_price_data['currency']

    return ticker_currency  # return current price of the ticker
