# -*- coding: utf-8 -*-
"""
CREACIÓN DE MAPA DE CALOR CON EL % DE PROBABILIDADES DE UNA CAÍDA SUPERIOR A UN  -X % EN UN PERIODO DE TIEMPO DE X SESIONES
Se utilizan 3 métodos diferentes de cálculo:
    - Cálculo directo sobre los datos
    - Cálculo por distribución normal
    - Cálculo por distribución Johnson Su
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, johnsonsu, lognorm, t, expon, exponweib, logistic, pareto, laplace, cauchy


# Introducir valores para los cálculos
ticker = ['^GSPC'] # '^GSPC', '^STOXX50E', '^GDAXI', '^GSPC', '^IXIC', '^DJI',... SPY, AAPL, ...
start_date = '2000-01-01'
end_date = '2023-03-26'
periods = [1, 2, 3, 4] + list(range(5,41,5)) + list(range(60,221,20))
pct_below = list(range(-40,41,1))
pct_below.reverse()

df = pd.DataFrame(yf.download(ticker, start=start_date, end=end_date)['Close'])
# df['Close'] = df['Adj Close'].copy()    ## Utilizar si se descarga 'Adj Close'
 
# Calculo directo sobre datos
results = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
for period in periods:
    # Calcula el cambio porcentual del cierre respecto al cierre anterior en cada periodo
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
    for pct in pct_below:
        # Calcula el porcentaje de días en que el precio estuvo por debajo del pct
        pct_days = (df[f'{period}d_pct_change'] < pct).mean() * 100
        results.loc[len(results)] = [ticker, period, pct, pct_days]

# Calculo por distribución normal
results_norm = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating normal')
for period in periods:
    # Calcula el cambio porcentual del cierre respecto al cierre anterior
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
    for pct in pct_below:
        # Calcula el porcentaje de días en que el precio estuvo por debajo del pct
        # media = df[f'{period}d_pct_change'].mean()
        # desviacion_estandar = df[f'{period}d_pct_change'].std()
        # pct_days = norm.cdf(+pct, loc=media, scale=desviacion_estandar) *100
        # Ajuste de la distribución normal
        mu, std = norm.fit(df[f'{period}d_pct_change'].dropna())
        pct_days = norm.cdf(pct, mu, std) * 100
        results_norm.loc[len(results_norm)] = [ticker, period, pct, pct_days]
 
# Calculo por Johnson Su
results_john = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating Johnson Su')
for period in periods:
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
    for pct in pct_below:
        # Calcula los parámetros de la distribución Johnson Su
        params = johnsonsu.fit(df[f'{period}d_pct_change'].dropna())
        # Calcula la probabilidad utilizando la distribución Johnson Su
        pct_days = johnsonsu.cdf(pct, *params) * 100
        results_john.loc[len(results_john)] = [ticker, period, pct, pct_days]


# Calculo por distribución lognormal
results_lognorm = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating lognormal')
for period in periods:
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
    for pct in pct_below:
        # Ajuste de la distribución lognormal
        sigma, loc, scale = lognorm.fit(df[f'{period}d_pct_change'].dropna())
        pct_days = lognorm.cdf(pct, sigma, loc, scale) * 100
        results_lognorm.loc[len(results_lognorm)] = [ticker, period, pct, pct_days]

# Calculo por distribución de cola gruesa (t de Student)
results_student = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating Student')
for period in periods:
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
    for pct in pct_below:
        # Ajuste de la distribución t de Student
        df_clean = df[f'{period}d_pct_change'].dropna()
        df_clean = (df_clean - df_clean.mean()) / df_clean.std()  # Normalización
        df_clean = df_clean[df_clean.abs() <= 3]  # Filtrado de outliers
        dof, loc, scale = t.fit(df_clean)
        pct_days = t.cdf(pct, dof, loc, scale) * 100
        results_student.loc[len(results_student)] = [ticker, period, pct, pct_days]

# Calculo por distribución exponencial
results_exp = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating exponencial')
for period in periods:
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
    for pct in pct_below:
        # Ajuste de la distribución exponencial
        loc, scale = expon.fit(df[f'{period}d_pct_change'].dropna())
        pct_days = expon.cdf(pct, loc, scale) * 100
        results_exp.loc[len(results_exp)] = [ticker, period, pct, pct_days]

# Calculo por distribución logística
results_logistic = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating logística')
for period in periods:
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
    for pct in pct_below:
        # Ajuste de la distribución logística
        loc, scale = logistic.fit(df[f'{period}d_pct_change'].dropna())
        pct_days = logistic.cdf(pct, loc, scale) * 100
        results_logistic.loc[len(results_logistic)] = [ticker, period, pct, pct_days]

# Calculo por distribución de Pareto
results_pareto = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating Pareto')
for period in periods:
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
    for pct in pct_below:
        # Ajuste de la distribución de Pareto
        shape, loc, scale = pareto.fit(df[f'{period}d_pct_change'].dropna())
        pct_days = pareto.cdf(pct, shape, loc, scale) * 100
        results_pareto.loc[len(results_pareto)] = [ticker, period, pct, pct_days]

# Calculo por distribución de Laplace
results_laplace = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating Laplace')
for period in periods:
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
    for pct in pct_below:
        # Ajuste de la distribución de Laplace
        loc, scale = laplace.fit(df[f'{period}d_pct_change'].dropna())
        pct_days = laplace.cdf(pct, loc, scale) * 100
        results_laplace.loc[len(results_laplace)] = [ticker, period, pct, pct_days]

# Calculo por distribución de Cauchy
results_cauchy = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating Cauchy')
for period in periods:
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
    for pct in pct_below:
        # Ajuste de la distribución de Cauchy
        loc, scale = cauchy.fit(df[f'{period}d_pct_change'].dropna())
        pct_days = cauchy.cdf(pct, loc, scale) * 100
        results_cauchy.loc[len(results_cauchy)] = [ticker, period, pct, pct_days]            
          
# Correlaciones de las distribuciones con los datos
corr_norm = results['pct_days'].corr(results_norm['pct_days'])
corr_john = results['pct_days'].corr(results_john['pct_days'])
corr_lognorm = results['pct_days'].corr(results_lognorm['pct_days'])
corr_student = results['pct_days'].corr(results_student['pct_days'])
corr_exp = results['pct_days'].corr(results_exp['pct_days'])
corr_logistic = results['pct_days'].corr(results_logistic['pct_days'])
corr_pareto = results['pct_days'].corr(results_pareto['pct_days'])
corr_laplace = results['pct_days'].corr(results_laplace['pct_days'])
corr_cauchy = results['pct_days'].corr(results_cauchy['pct_days'])

print(f'Correlaciones con los datos originales:\n'
      f'Dist. Normal = {corr_norm}\n'
      f'Dist. Johnson Su = {corr_john}\n'
      f'Dist. Lognormal = {corr_lognorm}\n'
      f'Dist. t de Student = {corr_student}\n'
      f'Dist. Exponencial = {corr_exp}\n'
      f'Dist. Logística = {corr_logistic}\n'
      f'Dist. Pareto = {corr_pareto}\n'
      f'Dist. Laplace = {corr_laplace}\n'
      f'Dist. Cauchy = {corr_cauchy}')









