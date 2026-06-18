import json
import math
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Union

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import requests
import scipy.optimize
from requests import Response

from model import OptionData, SymbolData
from utils import (
    calculate_ask_bid_volatility,
    create_option_data,
    get_list_of_call_and_put_data,
    get_list_of_symbols_data,
)


def volatility_curve(params, sigma_value: float, x_value: float) -> float:
    s, a, b, c, d, e = params
    y = x_value - s
    model_sigma = a + b * (1 - math.e ** (-c * y ** 2)) + d * math.atan(e * y) / e
    return sigma_value - model_sigma


def new_volatility_curve(params, x_value: float) -> float:
    s, a, b, c, d, e = params
    y = x_value - s
    return a + b * (1 - math.e ** (-c * y ** 2)) + d * math.atan(e * y) / e


if __name__ == '__main__':
    url = "https://deribit.com/api/v2/public/get_instruments"
    params: Dict[str, str] = {
        'currency': 'BTC',
        'kind': 'option',
    }

    res: Response = requests.get(url=url, params=params)
    result: List[Dict[str, Union[int, float, bool, str]]] = json.loads(res.text)['result']

    symbols_info: List[SymbolData] = get_list_of_symbols_data(result)

    symbols_data: Dict[str, Dict[str, Union[int, float, None]]] = defaultdict(dict)
    for symbol in result:
        series = symbol['instrument_name'][:-2]
        symbols_data[series]['creation_timestamp'] = symbol['creation_timestamp']
        symbols_data[series]['expiration_timestamp'] = symbol['expiration_timestamp']
        symbols_data[series]['strike'] = symbol['strike']

    url_option = 'https://deribit.com/api/v2/public/get_book_summary_by_currency'
    params_option: Dict[str, str] = {
        'currency': 'BTC',
        'kind': 'option',
    }

    opt_prices_request: Response = requests.get(url=url_option, params=params_option)
    options_prices: List[Dict[str, Union[int, float, bool, str]]] = json.loads(opt_prices_request.text)['result']

    options_call, options_put = get_list_of_call_and_put_data(options_prices=options_prices)

    options_info: Dict[str, List[OptionData]] = defaultdict(list)
    for call, put in zip(options_call, options_put):
        series = call['instrument_name'].split('-')[0] + '-' + call['instrument_name'].split('-')[1]
        option = create_option_data(call=call, put=put, symbols_data=symbols_data)
        if option is not None:
            options_info[series].append(option)

    current_time = datetime.now()
    folder_name = f'volatility_plots_{current_time}'
    os.mkdir(folder_name)

    red_patch = mpatches.Patch(color='red', label='ask')
    blue_patch = mpatches.Patch(color='blue', label='bid')
    green_patch = mpatches.Patch(color='green', label='mid')

    for series, option_items in options_info.items():
        ask_strikes: List[float] = []
        bid_strikes: List[float] = []
        mid_strikes: List[float] = []
        ask_volatility: List[float] = []
        bid_volatility: List[float] = []
        mid_volatility: List[float] = []
        s, a, b, c, d, e = 1, 1, 1, 1, 1, 1

        for item in sorted(option_items, key=lambda x: x.strike):
            mid = []
            item.ask_volatility, item.bid_volatility = calculate_ask_bid_volatility(item)

            if not np.isnan(item.ask_volatility):
                ask_strikes.append(item.strike)
                ask_volatility.append(item.ask_volatility)
                mid.append(item.ask_volatility)

            if not np.isnan(item.bid_volatility):
                bid_strikes.append(item.strike)
                bid_volatility.append(item.bid_volatility)
                mid.append(item.bid_volatility)

            if mid:
                mid_sigma = sum(mid) / len(mid)
                x_value = math.log(item.strike / item.underlying_price) / (item.maturity ** 0.5)

                mid_strikes.append(item.strike)
                mid_volatility.append(mid_sigma)

                result = scipy.optimize.minimize(
                    volatility_curve,
                    (s, a, b, c, d, e),
                    args=(mid_sigma, x_value),
                )
                s, a, b, c, d, e = result.x

        fig, ax = plt.subplots()
        ax.legend(handles=[red_patch, blue_patch, green_patch])
        plt.grid()

        plt.plot(ask_strikes, ask_volatility, 'ro', alpha=0.5, markersize=3)
        plt.plot(bid_strikes, bid_volatility, 'bo', alpha=0.5, markersize=3)
        plt.plot(mid_strikes, mid_volatility, 'go', alpha=0.5, markersize=3)
        plt.xlabel("Strike")
        plt.ylabel("Volatility")
        plt.title(series)
        plt.ylim(0, 2)
        plt.savefig(f'{folder_name}/{series}.png')
        plt.clf()
        print((s, a, b, c, d, e))
EOF

sed -n '1,240p' ~/output/deribit_main_clean.py
import json
import math
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Union

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import requests
import scipy.optimize
from requests import Response

from model import OptionData, SymbolData
from utils import (
    calculate_ask_bid_volatility,
    create_option_data,
    get_list_of_call_and_put_data,
    get_list_of_symbols_data,
)


def volatility_curve(params, sigma_value: float, x_value: float) -> float:
    s, a, b, c, d, e = params
    y = x_value - s
    model_sigma = a + b * (1 - math.e ** (-c * y ** 2)) + d * math.atan(e * y) / e
    return sigma_value - model_sigma


def new_volatility_curve(params, x_value: float) -> float:
    s, a, b, c, d, e = params
    y = x_value - s
    return a + b * (1 - math.e ** (-c * y ** 2)) + d * math.atan(e * y) / e


if __name__ == '__main__':
    url = "https://deribit.com/api/v2/public/get_instruments"
    params: Dict[str, str] = {
        'currency': 'BTC',
        'kind': 'option',
    }

    res: Response = requests.get(url=url, params=params)
    result: List[Dict[str, Union[int, float, bool, str]]] = json.loads(res.text)['result']

    symbols_info: List[SymbolData] = get_list_of_symbols_data(result)

    symbols_data: Dict[str, Dict[str, Union[int, float, None]]] = defaultdict(dict)
    for symbol in result:
        series = symbol['instrument_name'][:-2]
        symbols_data[series]['creation_timestamp'] = symbol['creation_timestamp']
        symbols_data[series]['expiration_timestamp'] = symbol['expiration_timestamp']
        symbols_data[series]['strike'] = symbol['strike']

    url_option = 'https://deribit.com/api/v2/public/get_book_summary_by_currency'
    params_option: Dict[str, str] = {
        'currency': 'BTC',
        'kind': 'option',
    }

    opt_prices_request: Response = requests.get(url=url_option, params=params_option)
    options_prices: List[Dict[str, Union[int, float, bool, str]]] = json.loads(opt_prices_request.text)['result']

    options_call, options_put = get_list_of_call_and_put_data(options_prices=options_prices)

    options_info: Dict[str, List[OptionData]] = defaultdict(list)
    for call, put in zip(options_call, options_put):
        series = call['instrument_name'].split('-')[0] + '-' + call['instrument_name'].split('-')[1]
        option = create_option_data(call=call, put=put, symbols_data=symbols_data)
        if option is not None:
            options_info[series].append(option)

    current_time = datetime.now()
    folder_name = f'volatility_plots_{current_time}'
    os.mkdir(folder_name)

    red_patch = mpatches.Patch(color='red', label='ask')
    blue_patch = mpatches.Patch(color='blue', label='bid')
    green_patch = mpatches.Patch(color='green', label='mid')

    for series, option_items in options_info.items():
        ask_strikes: List[float] = []
        bid_strikes: List[float] = []
        mid_strikes: List[float] = []
        ask_volatility: List[float] = []
        bid_volatility: List[float] = []
        mid_volatility: List[float] = []
        s, a, b, c, d, e = 1, 1, 1, 1, 1, 1

        for item in sorted(option_items, key=lambda x: x.strike):
            mid = []
            item.ask_volatility, item.bid_volatility = calculate_ask_bid_volatility(item)

            if not np.isnan(item.ask_volatility):
                ask_strikes.append(item.strike)
                ask_volatility.append(item.ask_volatility)
                mid.append(item.ask_volatility)

            if not np.isnan(item.bid_volatility):
                bid_strikes.append(item.strike)
                bid_volatility.append(item.bid_volatility)
                mid.append(item.bid_volatility)

            if mid:
                mid_sigma = sum(mid) / len(mid)
                x_value = math.log(item.strike / item.underlying_price) / (item.maturity ** 0.5)

                mid_strikes.append(item.strike)
                mid_volatility.append(mid_sigma)

                result = scipy.optimize.minimize(
                    volatility_curve,
                    (s, a, b, c, d, e),
                    args=(mid_sigma, x_value),
                )
                s, a, b, c, d, e = result.x

        fig, ax = plt.subplots()
        ax.legend(handles=[red_patch, blue_patch, green_patch])
        plt.grid()

        plt.plot(ask_strikes, ask_volatility, 'ro', alpha=0.5, markersize=3)
        plt.plot(bid_strikes, bid_volatility, 'bo', alpha=0.5, markersize=3)
        plt.plot(mid_strikes, mid_volatility, 'go', alpha=0.5, markersize=3)
        plt.xlabel("Strike")
        plt.ylabel("Volatility")
        plt.title(series)
        plt.ylim(0, 2)
        plt.savefig(f'{folder_name}/{series}.png')
        plt.clf()
        print((s, a, b, c, d, e))
