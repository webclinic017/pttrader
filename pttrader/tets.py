import yfinance as yf
import datetime
import pandas as pd

tickers_list = "NMTP"

# 1618307337.30397

timestamp = 1618307337.30397
dt_object = datetime.datetime.fromtimestamp(timestamp)
start_time = "2021-04-12"
data = yf.download(tickers=tickers_list + '.ME', start=dt_object, prepost=True, progress=False)

# print(type(data))
df = pd.DataFrame(data['Low'])
# print(data['Low'])
print(data)

# s = df[df <= 7.62]
print(len(df))
print(df['Low'])

price_to_check = 7.8
def check_data():

    for items in df['Low']:
        low_price = items #(round(items, ndigits=3))
        print("Low price is: ", low_price)
        if price_to_check >= low_price:
            print("Is price to check: ", price_to_check, ">=", low_price)
            print(df['Low'].index[0])
            return True
check_data()

