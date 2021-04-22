import trader

portfolio_all_data = trader.portfolio_show_current(435859)
portfolio_data = (portfolio_all_data[portfolio_all_data["ticker"] == "USDRUB"])
if not portfolio_data.empty:
    # get data about USDRUB from current portfolio
    print("portfolio data:\n", portfolio_data)
    # calculate average price for new order: sum of orders order_price_total / sum of amounts
    print("order_price_total:\n", (portfolio_data["order_price_total"]).values[0])
    print("amount:\n", portfolio_data["amount"].values[0])
    print("commission:\n", portfolio_data["commission"].index.values[0])
    # average_price = portfolio_data["order_price_total"] + order_data["order_price_total"]/


