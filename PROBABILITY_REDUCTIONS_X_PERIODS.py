# -*- coding: utf-8 -*-
"""
CREACIÓN DE MAPA DE CALOR CON EL % DE PROBABILIDADES DE MOVIMIENTO INFERIOR A UN  -X % EN UN PERIODO DE TIEMPO DE X SESIONES
Se utilizan 3 métodos diferentes de cálculo:
    - Cálculo directo sobre los datos
    - Cálculo por distribución normal
    - Cálculo por distribución Johnson Su
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, johnsonsu

# Introducir valores para los cálculos
tickers = ['^SPX'] # '^STOXX50E', '^GDAXI', '^GSPC', '^IXIC', '^DJI',... SPY, AAPL, ...
start_date = '2000-01-01'
end_date = '2023-03-26'
periods = [1, 2] + list(range(5,41,5)) + list(range(60,221,20))
pct_below = list(range(-30,31,2))
pct_below.reverse()


# Calculo directo sobre datos
results = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
for ticker in tickers:
    df = pd.DataFrame(yf.download(ticker, start=start_date, end=end_date)['Close'])
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
for ticker in tickers:
    df = pd.DataFrame(yf.download(ticker, start=start_date, end=end_date)['Close'])
    for period in periods:
        # Calcula el cambio porcentual del cierre respecto al cierre anterior
        df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
        for pct in pct_below:
            # Calcula el porcentaje de días en que el precio estuvo por debajo del pct
            media = df[f'{period}d_pct_change'].mean()
            desviacion_estandar = df[f'{period}d_pct_change'].std()
            pct_days = norm.cdf(pct, loc=media, scale=desviacion_estandar) *100
            results_norm.loc[len(results_norm)] = [ticker, period, pct, pct_days]

# Calculo por Johnson Su
results_john = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating Johnson Su')
for ticker in tickers:
    df = pd.DataFrame(yf.download(ticker, start=start_date, end=end_date)['Close'])
    for period in periods:
        df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)
        for pct in pct_below:
            # Calcula los parámetros de la distribución Johnson Su
            params = johnsonsu.fit(df[f'{period}d_pct_change'].dropna())
            # Calcula la probabilidad utilizando la distribución Johnson Su
            pct_days = johnsonsu.cdf(pct, *params) * 100
            results_john.loc[len(results_john)] = [ticker, period, pct, pct_days]


  
# Crear un mapa de calor para cada ticker
for ticker in results['ticker'].unique():
    data = results[results['ticker'] == ticker]
    heatmap_data = pd.pivot_table(data, values='pct_days', index='pct_below', columns='period', sort = False)
    
    plt.figure(figsize=(14,8))
    sns.set_style('ticks')
    sns.heatmap(heatmap_data, cmap= 'YlGnBu', annot=True, fmt=".2f", annot_kws={"fontsize":8})
    
    plt.xlabel('Nº de sesiones', fontsize=20) 
    plt.ylabel('Probabilidad rendimiento inferior a\n\n %', fontsize=16)
    plt.title(f'{ticker} -  Datos históricos ente {start_date} y {end_date} - Direct calc\n', fontsize=24)
              
    plt.show()

# Crear un mapa de calor para cada ticker
for ticker in results_norm['ticker'].unique():
    data = results_norm[results_norm['ticker'] == ticker]
    heatmap_data = pd.pivot_table(data, values='pct_days', index='pct_below', columns='period', sort = False)
    
    plt.figure(figsize=(14,8))
    sns.set_style('ticks')
    sns.heatmap(heatmap_data, cmap= 'YlGnBu', annot=True, fmt=".2f", annot_kws={"fontsize":8})
    
    plt.xlabel('Nº de sesiones', fontsize=20) 
    plt.ylabel('Probabilidad rendimiento inferior a\n\n %', fontsize=16)
    plt.title(f'{ticker} -  Datos históricos ente {start_date} y {end_date} - Dist normal \n', fontsize=24)
              
    plt.show()

# Crear un mapa de calor para cada ticker
for ticker in results_john['ticker'].unique():
    data = results_john[results_john['ticker'] == ticker]
    heatmap_data = pd.pivot_table(data, values='pct_days', index='pct_below', columns='period', sort = False)
    
    plt.figure(figsize=(14,8))
    sns.set_style('ticks')
    sns.heatmap(heatmap_data, cmap= 'YlGnBu', annot=True, fmt=".2f", annot_kws={"fontsize":8})
    
    plt.xlabel('Nº de sesiones', fontsize=20) 
    plt.ylabel('Probabilidad rendimiento inferior a\n\n %', fontsize=16)
    plt.title(f'{ticker} -  Datos históricos ente {start_date} y {end_date} - Jonhson Su \n', fontsize=24)
              
    plt.show()
