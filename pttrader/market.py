
import yfinance as yf
import broker
import pandas as pd
import datetime
import sys
import urllib
from urllib.request import urlopen
import json

# TODO get market data when market closed

def get_stock_data(order_data):
    """

    order_data is input type of instrument: stocks or currency and ticker
    for stock https://api-invest.tinkoff.ru/trading/stocks/get?ticker=
    for currency api is https://api-invest.tinkoff.ru/trading/currency/get?ticker=USDRUB
    :return: stock_data

    {'payload': {'instruments': [{'currency': 'RUB',
                              'figi': 'BBG004730N88',
                              'isin': 'RU0009029540',
                              'lot': 10,
                              'min_price_increment': 0.01,
                              'name': 'Сбер Банк',
                              'ticker': 'SBER',
                              'type': 'Stock'}],
             'total': 1.0},
 'status': 'Ok',
 'tracking_id': 'ad909d0e2e8b06cd'}
    """

    if type(order_data) is list:
        ticker = order_data[1]
    else:
        ticker = order_data

    if ticker == "USDRUB":
        ticker = "USD000UTSTOM"
    client = broker.tinkof_api_auth()
    stock_data = client.market.market_search_by_ticker_get(ticker)

    return stock_data


def get_ticker_price(order_data):
    """
    This function get data from api and return ticker price
    return current price of the ticker

    {'c': 288.21,
     'figi': 'BBG004730N88',
     'h': 288.21,
     'interval': '1min',
     'l': 288.12,
     'o': 288.18,
     'time': datetime.datetime(2021, 4, 21, 14, 40, tzinfo=tzutc()),
     'v': 3040}
    """
    stock_data = get_stock_data(order_data)
    figi = stock_data.payload.instruments[0].figi
    client = broker.tinkof_api_auth()

    now = datetime.datetime.utcnow()
    created_at = now - datetime.timedelta(minutes=2)
    current_time = now.isoformat("T", timespec="seconds") + "Z"
    minute_before = created_at.isoformat("T", timespec="seconds") + "Z"

    interval = "1min"

    candles_data = (client.market.market_candles_get(figi=figi, _from=minute_before, to=current_time, interval=interval))


    # need to get last minute close ticker price

    if len(candles_data.payload.candles) != 0:
        average_price = [True, round((candles_data.payload.candles[0].h + candles_data.payload.candles[0].l) / 2, 3)]

        return average_price
    else:
        return [False, 0]


def get_ticker_lot_size(order_data):
    """
    This function get data from  api
    return ticker lot

    """
    stock_data = get_stock_data(order_data)

    lot_size = stock_data.payload.instruments[0].lot
    if type(order_data) is list:
        ticker = order_data[1]
    else:
        ticker = order_data
    # TODO this is exception only for tinkoff broker, you can buy 1 lot at current price only
    # if limit order only lot 1000 available
    if ticker == "USDRUB":

        lot_size = 1


    return lot_size


def get_ticker_min_price_increment(order_data):
    """
    This function get data from https://api-invest.tinkoff.ru/trading/stocks/get?ticker api
    return minimum price increment

    """
    stock_data = get_stock_data(order_data)

    min_price_increment = stock_data.payload.instruments[0].min_price_increment

    return min_price_increment


def get_ticker_currency(order_data):
    """

    This function get data from  api
    return ticker currency

    """

    stock_data = get_stock_data(order_data)

    ticker_currency = stock_data.payload.instruments[0].currency

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

    start_time = pd.to_datetime(created_at)  # receive data for all day

    if currency == "RUB" and instrument == "stocks":
        print("Try to get data for ", ticker, "instrument:", instrument, "created_at", created_at)
        data = yf.download(tickers=ticker + '.ME', start=start_time, prepost=True, progress=False, interval="1m")
        # print("data", data)
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
                    order_done_at = broker.get_current_time()
                    flag = False
                    order_status = [flag, order_done_at]
                    return order_status

            elif filtered_by_time.empty:
                order_done_at = broker.get_current_time()
                flag = False
                order_status = [flag, order_done_at]
                return order_status
        # TODO need to complete
        elif order_type == "Sell":
            df = pd.DataFrame(data['High'])
            # print("df", df)
            filtered_by_time = (df[df.index >= created_at])
            if not filtered_by_time.empty:
                print("filtered_by_time:\n", filtered_by_time)
                # condition to Sell order become True
                filtered_by_price = (filtered_by_time[filtered_by_time['High'] >= order_price])

                if not filtered_by_price.empty:
                    print("first data: ", filtered_by_price.index[0])
                    print("filtered first price", filtered_by_price.iloc[0, 0])

                    time_to_convert = (filtered_by_price.index[0])
                    order_done_at = time_to_convert.tz_convert("Europe/Moscow")
                    flag = True
                    order_status = [flag, order_done_at]
                    return order_status

                elif filtered_by_price.empty:
                    print("filtered_by_price.empty")
                    order_done_at = broker.get_current_time()
                    flag = False
                    order_status = [flag, order_done_at]
                    return order_status

            elif filtered_by_time.empty:
                print("filtered_by_time.empty")
                order_done_at = broker.get_current_time()
                flag = False
                order_status = [flag, order_done_at]
                return order_status


    # for currency
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
                    order_done_at = broker.get_current_time()
                    flag = False
                    order_status = [flag, order_done_at]
                    return order_status

            elif filtered_by_time.empty:
                order_done_at = broker.get_current_time()
                flag = False
                order_status = [flag, order_done_at]
                return order_status

        elif order_type == "Sell":
            df = pd.DataFrame(data['High'])
            return df['High']

    # for foreign stocks
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
                    order_done_at = broker.get_current_time()
                    flag = False
                    order_status = [flag, order_done_at]
                    return order_status

            elif filtered_by_time.empty:
                order_done_at = broker.get_current_time()
                flag = False
                order_status = [flag, order_done_at]
                return order_status

        elif order_type == "Sell":
            df = pd.DataFrame(data['High'])
            return df['High']


def get_ticker_historical_data_from_tinkoff_api(order_data):
    """
        first_data = [{"order_type": order_query[0], "user_id": order_query[1], "ticker": order_query[2],
                   "order_price": order_query[3], "amount": order_query[4], "currency": order_query[5],
                   "order_price_total": order_query[6], "created_at": order_query[7],
                   "operation_id": order_query[8], "instrument": order_query[9], "order_status": order_query[10]}]
    ['Buy', 41388, 'NMTP', 7.5, 100, 'RUB', 75000.0, 1618309777.660006, 85103, 'stocks', False]

    resp from api
    {'c': 288.21,
     'figi': 'BBG004730N88',
     'h': 288.21,
     'interval': '1min',
     'l': 288.12,
     'o': 288.18,
     'time': datetime.datetime(2021, 4, 21, 14, 40, tzinfo=tzutc()),
     'v': 3040}

    """
    order_type = order_data["order_type"]
    ticker = order_data["ticker"]
    order_price = order_data["order_price"]
    currency = order_data["currency"]
    created_at_raw = order_data["created_at"]
    instrument = order_data['instrument']
    client = broker.tinkof_api_auth()

    created_at = created_at_raw.split(sep="+")[0]
    created_at += "Z"
    now = broker.get_current_time()
    # TODO change interval if order was created yesterday and more than 1 day ago
    #interval = "1min"  # valid intervals ("1min","2min","3min","5min","10min","15min",
    # "30min","hour","2hour","4hour","day","week","month")
    time_to_check = created_at_raw.split(sep="T")[0]


    time_to_compare = now.split(sep="T")[0]

    # print("created_at", created_at)
    # print("now", now)
    interval = ""
    if time_to_check == time_to_compare:
        interval += "1min"

    elif time_to_check != time_to_compare:
        interval += "day"

    # for russian stocks
    if currency == "RUB" and instrument == "stocks":  # russian stocks
        print("Try to get data from tinkoff for ", ticker, "instrument:", instrument, "created_at", created_at)

        get_figi = client.market.market_search_by_ticker_get(ticker)
        figi = get_figi.payload.instruments[0].figi


        try:
            candles_data = (client.market.market_candles_get(figi=figi, _from=created_at, to=now, interval=interval))
        except Exception as e:
            print("no data",e)
            order_done_at = broker.get_current_time()
            flag = False
            order_status = [flag, order_done_at]
            return order_status
        # print(candles_data.payload.candles[0])
        # print("data", data)
        if order_type == "Buy":

            for candle in candles_data.payload.candles:

                price_open = candle.o
                price_high = candle.h
                price_low = candle.l
                price_close = candle.c
                time_data = candle.time
                volume = candle.v
                # condition to buy
                if order_price >= price_low:
                    order_done_at = time_data
                    flag = True
                    order_status = [flag, order_done_at]
                    return order_status
            # if all price data not meet condition to buy
            order_done_at = broker.get_current_time()
            flag = False
            order_status = [flag, order_done_at]
            return order_status

        elif order_type == "Sell":

            for candle in candles_data.payload.candles:

                price_open = candle.o
                price_high = candle.h
                price_low = candle.l
                price_close = candle.c
                time_data = candle.time
                volume = candle.v
                # condition to sell
                if order_price <= price_high:
                    order_done_at = time_data
                    flag = True
                    order_status = [flag, order_done_at]
                    return order_status

            # if all price data not meet condition to sell
            order_done_at = broker.get_current_time()
            flag = False
            order_status = [flag, order_done_at]
            return order_status

    # for currency
    elif currency == "RUB" and ticker == "USDRUB":

        print("elif RUB and USDRUB Try to get data for ", ticker, "instrument:", instrument)
        ticker = "USD000UTSTOM"
        get_figi = client.market.market_search_by_ticker_get(ticker)
        figi = get_figi.payload.instruments[0].figi


        try:
            candles_data = (client.market.market_candles_get(figi=figi, _from=created_at, to=now, interval=interval))
        except Exception as e:
            print("no data",e)
            order_done_at = broker.get_current_time()
            flag = False
            order_status = [flag, order_done_at]
            return order_status

        if order_type == "Buy":
            for candle in candles_data.payload.candles:

                price_open = candle.o
                price_high = candle.h
                price_low = candle.l
                price_close = candle.c
                time_data = candle.time
                volume = candle.v
                # condition to buy
                if order_price >= price_low:
                    order_done_at = time_data
                    flag = True
                    order_status = [flag, order_done_at]
                    return order_status
            # if all price data not meet condition to buy
            order_done_at = broker.get_current_time()
            flag = False
            order_status = [flag, order_done_at]
            return order_status


        elif order_type == "Sell":

            for candle in candles_data.payload.candles:

                price_open = candle.o
                price_high = candle.h
                price_low = candle.l
                price_close = candle.c
                time_data = candle.time
                volume = candle.v
                # condition to sell
                if order_price <= price_high:
                    order_done_at = time_data
                    flag = True
                    order_status = [flag, order_done_at]
                    return order_status

            # if all price data not meet condition to sell
            order_done_at = broker.get_current_time()
            flag = False
            order_status = [flag, order_done_at]
            return order_status

    # for foreign stocks
    elif currency == "USD" and instrument == "stocks":
        print("elif USD and stock Try to get data for ", ticker, "instrument:", instrument)
        get_figi = client.market.market_search_by_ticker_get(ticker)

        figi = get_figi.payload.instruments[0].figi

        try:
            candles_data = (client.market.market_candles_get(figi=figi, _from=created_at, to=now, interval=interval))

        except Exception as e:
            print("no data",e)
            order_done_at = broker.get_current_time()
            flag = False
            order_status = [flag, order_done_at]
            return order_status


        if order_type == "Buy":

            for candle in candles_data.payload.candles:

                price_open = candle.o
                price_high = candle.h
                price_low = candle.l
                price_close = candle.c
                time_data = candle.time
                volume = candle.v
                # condition to buy
                if order_price >= price_low:
                    order_done_at = time_data
                    flag = True
                    order_status = [flag, order_done_at]
                    return order_status
            # if all price data not meet condition to buy
            order_done_at = broker.get_current_time()
            flag = False
            order_status = [flag, order_done_at]
            return order_status

        elif order_type == "Sell":

            for candle in candles_data.payload.candles:

                price_open = candle.o
                price_high = candle.h
                price_low = candle.l
                price_close = candle.c
                time_data = candle.time
                volume = candle.v
                # condition to sell
                if order_price <= price_high:
                    order_done_at = time_data
                    flag = True
                    order_status = [flag, order_done_at]
                    return order_status

            # if all price data not meet condition to sell
            order_done_at = broker.get_current_time()
            flag = False
            order_status = [flag, order_done_at]
            return order_status

    else:
        print("Something goes wrong, check function", sys._getframe().f_code.co_name)
        return False


def get_ticker_by(figi) -> str:
    client = broker.tinkof_api_auth()

    figi_data = client.market.market_search_by_figi_get(figi)  # get ticker by figi
    ticker = figi_data.payload.ticker

    return ticker


def get_sector_by_ticker(ticker) -> str:

    sector = str()
    try:
        dataLink = 'https://api-invest.tinkoff.ru/trading/stocks/get?ticker=' + ticker
        data = urllib.request.urlopen(dataLink)
        data = data.read().decode("utf-8")
        data = json.loads(data)

        data2 = data['payload']

        data3 = data2["symbol"]
        sector += data3["sector"]

        return sector

    except Exception as e:


        print("Exception in get sector by ticker",ticker , e)
        return sector

