import datetime as dt


# input data may be primary from trader: buy_request, sell_request
def create_order_query(operation_type):
    """
    Get input parameters from trader:
    operation type: Buy or Sell from main cycle
    ticker
    buy_order_price
    sell_order_price
    amount
    created_at
    :return: order query
    """

    print("Enter ticker name:")
    ticker = str(input(">>"))
    if operation_type == "Buy":
        print("Enter price for Buy operation:")
        buy_order_price = float(input(">>"))
        print("Enter amount in lot's:")
        amount = int(input())
        created_at = dt.datetime.utcnow()
        order_query = [operation_type, ticker, buy_order_price, amount, created_at]
        print("You create buy order: ", order_query)
        return order_query

    elif operation_type == "Sell":
        print("Enter price for Sell operation:")
        sell_order_price = float(input(">>"))
        print("Enter amount in lot's:")
        amount = int(input(">>"))
        created_at = dt.datetime.utcnow()
        order_query = [operation_type, ticker, sell_order_price, amount, created_at]
        print("You create sell order query: ", order_query)
        return order_query

    else:
        print("You do something wrong")


def commission():
    pass
