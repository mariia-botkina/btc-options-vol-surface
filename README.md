# btc-options-vol-surface

A Python tool for fetching live BTC options data from the [Deribit](https://deribit.com) exchange API and building **implied volatility curves** across all active expiry series.

 

## What It Does

1. Fetches all active BTC options instruments via the [Deribit public API v2](https://docs.deribit.com/)
2. Retrieves live order book summaries (ask/bid prices) for each instrument
3. Pairs call and put options by strike and expiry series
4. Computes **implied volatility** for ask, bid, and mid prices using the Black-Scholes model
5. Fits a **parametric volatility smile** to each expiry series using a 6-parameter curve:

```
σ(x) = a + b·(1 − e^(−c·(x−s)²)) + d·arctan(e·(x−s)) / e
```

where `x = ln(K / S) / √T` is the log-moneyness scaled by time to expiry.

6. Saves per-series volatility smile plots (ask, bid, mid) as PNG files.

## Output

Each plot shows implied volatility against strike price for a given BTC expiry series — ask (red), bid (blue), and mid (green) points.

Output files are saved to `volatility_plots_<timestamp>/BTC-DDMMMYY.png`.

## Project Structure

```
deribit_exploring/
├── main.py                  # Entry point: API calls, vol fitting, plotting
├── model.py                 # Dataclasses: SymbolData, OptionData
├── utils.py                 # Data parsing, option pairing, IV calculation
├── optimize.py              # Volatility curve objective functions
├── getting_attributes.py    # Instrument attribute extraction helpers
├── request_attributes.txt   # Reference: Deribit API response field names
└── requirements.txt
```

## Usage

```bash
pip install -r requirements.txt
python main.py
```

No API key required — uses Deribit's public endpoints only.

## How Implied Volatility Is Computed

For each option pair (call + put at the same strike), implied volatility is estimated numerically by inverting the Black-Scholes pricing formula. The smile is then fitted per expiry using `scipy.optimize.minimize` on the parametric curve above.

## Dependencies

| Library | Purpose |
|---------|---------|
| `requests` | Deribit API calls |
| `numpy` | Numerical operations |
| `scipy` | Curve fitting (`minimize`) |
| `matplotlib` | Volatility smile plots |
| `seaborn` | Plot styling |

## Notes

- Data is fetched at runtime — no historical data is stored in this repository.
- The curve parametrization is inspired by SVI (Stochastic Volatility Inspired) smile models used in quantitative finance.
- Built as an exploration of options market microstructure and volatility surface modeling.
