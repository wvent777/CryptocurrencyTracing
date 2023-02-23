import pandas as pd
from requests import get
import datetime as dt

API_KEY ='W9M2I8E2YTWRRIY4CNNHQH9YXKWHQIJBRG'
BASE_URL = 'https://api.etherscan.io/api'
ETHER_VALUE = 10 ** 18

'''https://api.etherscan.io/api
   ?module=account
   &action=balance
   &address=0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae
   &tag=latest
   &apikey=YourApiKeyToken
   
   https://api.etherscan.io/api
   ?module=logs
   &action=getLogs
   &address=0xbd3531da5cf5857e7cfaa92426877b022e612cf8
   &fromBlock=12878196
   &toBlock=12878196
   &page=1
   &offset=1000
   &apikey=YourApiKeyToken'''


def make_api_url(module, action, address, **kwargs):
    url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={API_KEY}"

    for key, value in kwargs.items():
        url += f"&{key}={value}"

    return url

def get_balance(address):
    get_balance_url = make_api_url('account', 'balance', address, tag='latest')
    response = get(get_balance_url)
    data = response.json()
    balance = int(data["result"])/ETHER_VALUE
    return balance

# Pro API only
def make_block_url(module, action, start_date, end_date):
    url = BASE_URL + f"?module={module}&action={action}&startdate={start_date}&enddate={end_date}" \
                     f"&sort=asc&apikey={API_KEY}"
    return url

def get_blocks(module, action, start_date, end_date):
    blocks_url = make_block_url(module, action, start_date, end_date)
    response = get(blocks_url)
    data = response.json()
    return data

'''https://api.etherscan.io/api
   ?module=account
   &action=txlist
   &address=0xc5102fE9359FD9a28f877a67E36B0F050d81a3CC
   &startblock=0
   &endblock=99999999
   &page=1
   &offset=10
   &sort=asc
   &apikey=YourApiKeyToken'''


def get_account_transactions(address, start_block, end_block, verbose=False):
    transactions_url = make_api_url('account', 'txlist', address, startBlock=start_block,
                                endBlock=end_block, page=1, offset=10000, sort='asc')
    internal_txn_url = make_api_url('account', 'txlistinternal', address, startBlock=start_block,
                                endBlock=end_block, page=1, offset=10000, sort='asc')
    # Get normal Transactions
    response = get(transactions_url)
    data_json = response.json()   # read in json format
    data = data_json["result"]    # filter to results


    # Get internal transactions
    response_2 = get(internal_txn_url)
    data_2 = response_2.json()["result"]
    data.extend(data_2)
    data.sort(key=lambda x: x['timeStamp'])
    df = pd.json_normalize(data)  # convert to dataframe
    if verbose:
        current_balance = 0
        balances = []
        times = []
        print(transactions_url)
        for tx in data[0:5]:
            to = tx["to"]
            from_addr = tx["from"]
            value = int(tx['value'])/ETHER_VALUE
            if "gasPrice" in tx:
                gas = int(tx['gasUsed'])*int(tx["gasPrice"]) / ETHER_VALUE
            else:
                gas = int(tx['gasUsed'])/ETHER_VALUE
            time = dt.datetime.fromtimestamp(int(tx['timeStamp']))
            money_in = to.lower() == address.lower()
            print('------------------')
            print('To:', to)
            print('From:', from_addr)
            print('Value:', value)
            print('Gas Used:', gas)
            print('Time:', time)
            if money_in:
                current_balance += value
            else:
                current_balance -= value + gas
            balances.append(current_balance)
            times.append(time)
    return df

def clean_df(df):
    df["timeStamp"] = pd.to_datetime(df["timeStamp"], unit='s')
    df["value"] = df["value"].astype(float)
    df["value"] = df["value"] / ETHER_VALUE
    # get USD conversion rates
    conversion_rates = get('https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=BTC,USD,EUR')
    df['value_usd'] = df["value"] * conversion_rates.json()["USD"]
    return df

