import yfinance as yf
import datetime
from dateutil import tz
import pandas as pd

iter()

tickers_list = "USDRUB"
ticker_usd = "FOLD"

# 1618307337.30397

timestamp = 1618474670.14237
dt_object = datetime.datetime.fromtimestamp(timestamp)

new_time = datetime.datetime.isoformat(datetime.datetime.utcnow(),sep=' ', timespec='seconds')

London_tz = tz.gettz("Europe/London")
Moscow_tz = tz.gettz("Europe/Moscow")
now = datetime.datetime.now(tz=Moscow_tz)
now_1 = pd.to_datetime(now)
created_at = pd.to_datetime("2021-04-19 18:45:04.097569+03:00")
start_time = pd.to_datetime(created_at)

print(now)

print("now_1", now_1)
print(type(now_1))


data = yf.download(tickers=tickers_list + '.ME', start=now, prepost=True, progress=False, interval="1m")
data_usd = yf.download(tickers=ticker_usd , start=now, prepost=True, progress=False, interval="1m")

# print(type(data))
df = pd.DataFrame(data_usd['Low'])
# print(data['Low'])
print("df",df)
print(type((df['Low'].index[0])))


print("More that createdtime")

filtered_by_time = df[df.index >= created_at] # filter by start time
if not filtered_by_time.empty:

    print("filtered by time:", filtered_by_time)
    print("filtered_by_time['Low']", filtered_by_time['Low'])

    order_price = 9.89
    print("Checking condition:", order_price)

    filtered_by_price = (filtered_by_time[filtered_by_time['Low'] <= order_price])
    if not filtered_by_price.empty:

        print("filtered by price:", filtered_by_price)

        print("first data: ", filtered_by_price.index[0])

        print("filtered first price",filtered_by_price.iloc[ 0 , 0])

        tupe_tz = (filtered_by_price.index[0])

        print(tupe_tz.tz_convert("Europe/Moscow"))
    elif filtered_by_price.empty:
        print("filtered by price is empty")

elif filtered_by_time.empty:
    print("filtered by time is empty")

def check_data():

    for items in filtered_by_time:
        low_price = items #(round(items, ndigits=3))
        print("items",low_price)

        #print("Low price is: ", low_price)
        if order_price >= low_price:
            print("Is price to check: ", order_price, ">=", low_price)
            print("filtered df index", filtered_by_time.index[0])
            print(df['Low'].index[0])
            print(items)

            return True



