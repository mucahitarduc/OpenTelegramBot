import os
import json
import time
import requests
import logging
import opentelegrambot.constants as con


class CoinMarketCap(object):

    _url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    _datetime = 0
    _parameters = {
    'start':'1',
    'limit':'5000',
    'convert':'USD'
    }
    _headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c',
    }
    response = None
    res_json = None

    BEST = "BEST"
    WORST = "WORST"

    HOUR = "HOUR"
    DAY = "DAY"

    def __init__(self, url=None):
        if url:
            self._url = url
        token_path = os.path.join(con.CFG_DIR, con.TKN_FILE)

        try:
            if os.path.isfile(token_path):
                with open(token_path, 'r') as file:
                    CoinMarketCap._headers["X-CMC_PRO_API_KEY"] = json.load(file)["coinmarketcap"]
            else:
                logging.error(f"No token file '{con.TKN_FILE}' found at '{token_path}'")
        except KeyError as e:
            cls_name = f"Class: {type(self).__name__}"
            logging.error(f"{repr(e)} - {cls_name}")

    def get_movers(self, move, period=HOUR, entries=10, volume=None):
        # Current datetime in seconds
        now = int(time.time())

        # Check if last API call longer then 2 min ago
        if (now - 60) > CoinMarketCap._datetime:
            CoinMarketCap._datetime = now

            try:
                CoinMarketCap.response = requests.get(CoinMarketCap._url, params=CoinMarketCap._parameters, headers=CoinMarketCap._headers)
                CoinMarketCap.response.raise_for_status()
                res_json = json.loads(CoinMarketCap.response.content.decode('utf-8'))
                if res_json['status']['error_code'] == 0:
                    CoinMarketCap.res_json = list()
                    for data in res_json['data']:
                        data['quote']['USD']['Name'] = data['name']
                        data['quote']['USD']['Symbol'] = data['symbol']
                        CoinMarketCap.res_json.append(data['quote']['USD'])
            except Exception as e:
                CoinMarketCap._datetime = 0
                raise e

            if not CoinMarketCap.res_json:
                raise ValueError("No response data available")

            # Filter out 'null' values
            CoinMarketCap.res_json = [d for d in CoinMarketCap.res_json if all(d.values())]

        data = list()

        if volume:
            # Sort data by volume
            temp = sorted(
                CoinMarketCap.res_json,
                key=lambda k: float(k["Volume_24h"]), reverse=True)

            for entry in temp:
                if int(float(entry["Volume_24h"])) > volume:
                    data.append(entry)
                else:
                    break
        else:
            data = CoinMarketCap.res_json

        if period == self.HOUR:
            # Sort data period - 1 hour
            data = sorted(
                data,
                key=lambda k: float(k["percent_change_1h"]), reverse=True)
        elif period == self.DAY:
            # Sort data period - 1 day
            data = sorted(
                data,
                key=lambda k: float(k["percent_change_24h"]), reverse=True)
        else:
            return None

        result = list()

        count = 0
        if move == self.BEST:
            for entry in data:
                if count == entries:
                    break
                result.append(entry)
                count += 1
        elif move == self.WORST:
            for entry in reversed(data):
                if count == entries:
                    break
                result.append(entry)
                count += 1
        else:
            return None

        return result
