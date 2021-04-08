import requests
import pprint
class Assets:
    """
    Class contain assets (stock, currency, bond and etc)  information from market and operation
    """

    # for example get info from tinkoff https://api-invest.tinkoff.ru/trading/stocks/get?ticker=UWGN
    pass


def get_stock_data(ticker):
    stock_name = ticker
    url = "https://api-invest.tinkoff.ru/trading/stocks/get?ticker="+str(stock_name)

    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"}
    req = requests.get(url, headers=headers)
    resp = req.json()

    stock_data= resp["payload"]
    stock_price_data = stock_data['price']
    print(stock_price_data['value'])
    #pprint.pprint(resp)