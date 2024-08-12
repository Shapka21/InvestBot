import yfinance as yf
import datetime

from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices


stocks = ['LKOH.ME', 'GMKN.ME', 'DSKY.ME', 'NKNC.ME', 'MTSS.ME', 'IRAO.ME', 'SBER.ME', 'AFLT.ME', 'FEES.ME', 'GAZP.ME',
          'NVTK.ME', 'ROSN.ME', 'VTBR.ME', 'RTKM.ME', 'YNDX.ME', 'FIVE.ME', 'BELU.ME', 'IRKT.ME', 'TCSG.ME', 'UPRO.ME']


def min_volantily(stocks, money):
    current_date = datetime.date.today().isoformat()
    data = yf.download(stocks, '2022-01-1', current_date) 

    mu = expected_returns.mean_historical_return(data['Adj Close'])
    Sigma = risk_models.sample_cov(data['Adj Close'])

    ef1 = EfficientFrontier(mu, Sigma, weight_bounds=(0, 1))
    ef1.min_volatility()
    minvol_pwt = ef1.clean_weights()

    latest_prices = get_latest_prices(data['Adj Close']) * 10
    allocation_minv, rem_minv = DiscreteAllocation(minvol_pwt, latest_prices,
                                                   total_portfolio_value=money).greedy_portfolio()
    return allocation_minv, rem_minv


def max_sharp(stocks, money):
    current_date = datetime.date.today().isoformat()
    data = yf.download(stocks, '2022-01-1', current_date)

    mu = expected_returns.mean_historical_return(data['Adj Close'])
    Sigma = risk_models.sample_cov(data['Adj Close'])

    ef = EfficientFrontier(mu, Sigma, weight_bounds=(0, 1))
    ef.max_sharpe()
    sharpe_pwt = ef.clean_weights()

    latest_prices = get_latest_prices(data['Adj Close']) * 10
    allocation_shp, rem_shp = DiscreteAllocation(sharpe_pwt, latest_prices,
                                                 total_portfolio_value=money).greedy_portfolio()

    return allocation_shp, rem_shp


def info_stock(stock):
    current_date = datetime.date.today().isoformat()

    if len(stock)>7 or len(stock)<3:
        return 0, 0, 0, False

    data = yf.download(stock.upper(), '2022-01-1', current_date)
    if len(data) != 0:
        mu = expected_returns.mean_historical_return(data['Adj Close'])
        Sigma = risk_models.sample_cov(data['Adj Close'])
        last_prise = data['Adj Close'][-1]
        return mu['Adj Close'] * 100, Sigma['Adj Close']['Adj Close'], last_prise, True

    stock += '.ME'
    data = yf.download(stock.upper(), '2022-01-1', current_date)
    if len(data) != 0:
        mu = expected_returns.mean_historical_return(data['Adj Close'])
        Sigma = risk_models.sample_cov(data['Adj Close'])
        last_prise = data['Adj Close'][-1]
        return mu['Adj Close'] * 100, Sigma['Adj Close']['Adj Close'], last_prise, True
    else:
        return 0, 0, 0, False
