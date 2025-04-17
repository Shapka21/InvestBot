import yfinance as yf
import datetime

from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from pypfopt import EfficientFrontier, DiscreteAllocation
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from statsmodels.tsa.arima.model import ARIMA
from scipy.optimize import minimize


stocks = ['LKOH.ME', 'GMKN.ME', 'NKNC.ME', 'MTSS.ME', 'IRAO.ME', 'SBER.ME', 'AFLT.ME', 'FEES.ME', 'GAZP.ME',
          'NVTK.ME', 'ROSN.ME', 'VTBR.ME', 'RTKM.ME', 'BELU.ME', 'IRKT.ME', 'TCSG.ME', 'UPRO.ME']


# Шаг 1: Сбор данных
def download_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    return data


# Шаг 2: Предобработка данных
def preprocess_data(data, look_back=60):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data.values.reshape(-1, 1))

    X, y = [], []
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i - look_back:i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, y, scaler


# Шаг 3: Создание и обучение модели LSTM
def build_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


# Шаг 4: Прогнозирование будущих цен
def predict_future_prices(model, last_sequence, scaler, days=30):
    future_predictions = []
    current_sequence = last_sequence

    for _ in range(days):
        # Предсказываем следующее значение
        prediction = model.predict(current_sequence)

        # Сохраняем предсказанное значение
        future_predictions.append(prediction[0, 0])

        # Обновляем текущую последовательность, добавляя новое предсказание
        # Убедимся, что prediction имеет правильную форму
        prediction = np.reshape(prediction, (1, 1, 1))  # Форма: (1, 1, 1)
        current_sequence = np.append(current_sequence[:, 1:, :], prediction, axis=1)

    # Инвертируем масштабирование для получения реальных значений
    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
    return future_predictions.flatten()


# Шаг 5: Оптимизация портфеля
def optimize_portfolio(expected_returns, covariance_matrix, total_investment):
    num_assets = len(expected_returns)

    def objective(weights):
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        # Минимизируем риск (волатильность) при фиксированной доходности
        return portfolio_volatility

    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
    bounds = [(0, 1) for _ in range(num_assets)]
    initial_weights = [1 / num_assets] * num_assets

    result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    optimal_weights = result.x
    allocation = optimal_weights * total_investment
    return allocation, optimal_weights


# Основная функция
def create_investment_portfolio(tickers, investment_amount, forecast_days=5):
    # Скачиваем данные
    data = download_data(tickers, '2022-01-01', '2025-01-01')

    predictions = {}
    for ticker in tickers:
        ticker_data = data[ticker].dropna()

        # Предобработка данных
        X, y, scaler = preprocess_data(ticker_data)
        model = build_lstm_model((X.shape[1], 1))

        # Обучение модели
        model.fit(X, y, batch_size=32, epochs=10, verbose=0)

        # Прогнозирование будущих цен
        last_sequence = X[-1].reshape(1, -1, 1)
        future_prices = predict_future_prices(model, last_sequence, scaler, days=forecast_days)
        predictions[ticker] = future_prices[-1]  # Берем последнюю прогнозную цену

    # Вычисляем ожидаемую доходность и ковариационную матрицу
    returns = pd.DataFrame({ticker: data[ticker].pct_change().dropna() for ticker in tickers})
    expected_returns = returns.mean().values
    covariance_matrix = returns.cov().values

    # Оптимизация портфеля
    allocation, weights = optimize_portfolio(expected_returns, covariance_matrix, investment_amount)

    # Вывод результатов
    portfolio = {tickers[i]: {'allocation': allocation[i], 'weight': weights[i]} for i in range(len(tickers))}
    return portfolio
