import requests
import yfinance as yf
import datetime
import pandas as pd


def get_stock_data(order_data):
    """
    order_data is input type of instrument: stocks or currency and ticker
    for stock https://api-invest.tinkoff.ru/trading/stocks/get?ticker=
    for currency api is https://api-invest.tinkoff.ru/trading/currency/get?ticker=USDRUB
    :return: stock_data
    """
    instrument = order_data[0]
    ticker = order_data[1]
    url = "https://api-invest.tinkoff.ru/trading/"+str(instrument)+"/get?ticker=" + str(ticker)

    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"}
    req = requests.get(url, headers=headers)
    resp = req.json()
    stock_data = resp["payload"]

    return stock_data


def get_ticker_price(order_data):
    """
    This function get data from https://api-invest.tinkoff.ru/trading/stocks/get?ticker api and return ticker price
    return current price of the ticker
    """
    stock_data = get_stock_data(order_data)
    key = 'code'
    if stock_data.get(key) is not None:
        if stock_data['code'] == 'TickerNotFound':
            code = "TickerNotFound"
            return code
    else:
        current_price_data = stock_data['price']
        current_price = current_price_data['value']

        return current_price


def get_ticker_lot_size(order_data):
    """
    This function get data from https://api-invest.tinkoff.ru/trading/stocks/get?ticker api
    return ticker lot

    """
    stock_data = get_stock_data(order_data)
    lot_size_data = stock_data['symbol']
    lot_size = lot_size_data['lotSize']

    return lot_size


def get_ticker_min_price_increment(order_data):
    """
    This function get data from https://api-invest.tinkoff.ru/trading/stocks/get?ticker api
    return minimum price increment

    """
    stock_data = get_stock_data(order_data)
    min_price_increment_data = stock_data['symbol']
    min_price_increment = min_price_increment_data['minPriceIncrement']

    return min_price_increment


def get_ticker_currency(order_data):
    """
    This function get data from https://api-invest.tinkoff.ru/trading/stocks/get?ticker api
    return ticker currency

    """

    stock_data = get_stock_data(order_data)
    key = 'code'
    if stock_data.get(key) is not None:
        if stock_data['code'] == 'TickerNotFound':
            code = "TickerNotFound"
            return code
    else:
        current_price_data = stock_data['price']
        ticker_currency = current_price_data['currency']

        return ticker_currency  # return current price of the ticker

def get_ticker_historical_data(order_data):

    """
        first_data = [{"order_type": order_query[0], "user_id": order_query[1], "ticker": order_query[2],
                   "order_price": order_query[3], "amount": order_query[4], "currency": order_query[5],
                   "order_price_total": order_query[6], "created_at": order_query[7],
                   "operation_id": order_query[8], "instrument": order_query[9], "order_status": order_query[10]}]
    ['Buy', 41388, 'NMTP', 7.5, 100, 'RUB', 75000.0, 1618309777.660006, 85103, 'stocks', False]
    """
    order_type = order_data["order_type"]
    ticker = order_data["ticker"]
    order_price = order_data["order_price"]
    currency = order_data["currency"]
    created_at = order_data["created_at"]
    instrument = order_data['instrument']

    start_time = pd.to_datetime(created_at) # receive data for all day

    if currency == "RUB" and instrument == "stocks":
        print("Try to get data for ", ticker, "instrument:", instrument, "created_at", created_at)
        data = yf.download(tickers=ticker + '.ME', start=start_time, prepost=True, progress=False, interval="1m")
        #print("data", data)
        if order_type == "Buy":
            df = pd.DataFrame(data['Low'])
            #print("df", df)
            filtered_by_time = (df[df.index >= created_at])
            if not filtered_by_time.empty:
                #print("filtered by time at market", filtered_by_time)
                # condition to buy order become True
                filtered_by_price = (filtered_by_time[filtered_by_time['Low'] <= order_price])
                if not filtered_by_price.empty:
                    print("first data: ", filtered_by_price.index[0])
                    print("filtered first price", filtered_by_price.iloc[0, 0])

                    time_to_convert = (filtered_by_price.index[0])
                    order_done_at = time_to_convert.tz_convert("Europe/Moscow")
                    flag = True
                    order_status = [flag, order_done_at]
                    return order_status

                elif filtered_by_price.empty:
                    order_done_at = created_at
                    flag = False
                    order_status = [flag, order_done_at]
                    return order_status

            elif filtered_by_time.empty:
                order_done_at = created_at
                flag = False
                order_status = [flag, order_done_at]
                return order_status
        # TODO need to complete
        elif order_type == "Sell":
            df = pd.DataFrame(data['High'])
            return df['High']

    elif currency == "RUB" and ticker == "USDRUB":
        print("elif RUB and USDRUB Try to get data for ", ticker, "instrument:", instrument)
        data = yf.download(tickers=ticker + '.ME', start=start_time, prepost=True, progress=False, interval="1m")
        if order_type == "Buy":
            df = pd.DataFrame(data['Low'])
            # print("df", df)
            filtered_by_time = (df[df.index >= created_at])
            if not filtered_by_time.empty:
                # print("filtered by time at market", filtered_by_time)
                # condition to buy order become True
                filtered_by_price = (filtered_by_time[filtered_by_time['Low'] <= order_price])
                if not filtered_by_price.empty:
                    print("first data: ", filtered_by_price.index[0])
                    print("filtered first price", filtered_by_price.iloc[0, 0])

                    time_to_convert = (filtered_by_price.index[0])
                    order_done_at = time_to_convert.tz_convert("Europe/Moscow")
                    flag = True
                    order_status = [flag, order_done_at]
                    return order_status

                elif filtered_by_price.empty:
                    order_done_at = created_at
                    flag = False
                    order_status = [flag, order_done_at]
                    return order_status

            elif filtered_by_time.empty:
                order_done_at = created_at
                flag = False
                order_status = [flag, order_done_at]
                return order_status

        elif order_type == "Sell":
            df = pd.DataFrame(data['High'])
            return df['High']


    elif currency == "USD" and instrument == "stocks":
        print("elif USD and stock Try to get data for ", ticker, "instrument:", instrument)
        data = yf.download(tickers=ticker, start=start_time, prepost=True, progress=False, interval="1m")
        if order_type == "Buy":
            df = pd.DataFrame(data['Low'])
            # print("df", df)
            filtered_by_time = (df[df.index >= created_at])
            if not filtered_by_time.empty:
                # print("filtered by time at market", filtered_by_time)
                # condition to buy order become True
                filtered_by_price = (filtered_by_time[filtered_by_time['Low'] <= order_price])
                if not filtered_by_price.empty:
                    print("first data: ", filtered_by_price.index[0])
                    print("filtered first price", filtered_by_price.iloc[0, 0])

                    time_to_convert = (filtered_by_price.index[0])
                    order_done_at = time_to_convert.tz_convert("Europe/Moscow")
                    flag = True
                    order_status = [flag, order_done_at]
                    return order_status

                elif filtered_by_price.empty:
                    order_done_at = created_at
                    flag = False
                    order_status = [flag, order_done_at]
                    return order_status

            elif filtered_by_time.empty:
                order_done_at = created_at
                flag = False
                order_status = [flag, order_done_at]
                return order_status

        elif order_type == "Sell":
            df = pd.DataFrame(data['High'])
            return df['High']

