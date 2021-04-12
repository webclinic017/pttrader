import pandas as pd

amount = 200
currency = "RUR"
new_data = {"currency": "RUR",
            "amount": 100}
old_data = {"currency": ["RUR", "USD"],
            "amount": [300, 200]
            }

wallet_current_data = pd.read_csv("files/wallet_" + str(63316) + ".csv")  # , index_col=["currency"])
wallet_new_data = pd.DataFrame(old_data)
print(wallet_current_data)
print(wallet_new_data)
