# -*- coding: utf-8 -*-
"""
COMPARATIVA DE CALCULO DE PROBABILIDADES DE RENDIMIENTOS OBTENIDOS POR PERIODOS DE TIEMPO UTILIZANDO DIFERENTES DISTRIBUCIONES
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
import time


dist_list_stats = stats._continuous_distns._distn_names
dist_list_obj = [getattr(stats, dist) for dist in dist_list_stats]
# Lista de las distribuciones a calcular (los nombres de scipy.stats)
# distributions = [stats.norm, stats.johnsonsu, stats.lognorm, stats.t, stats.expon, stats.logistic, stats.pareto, stats.laplace, stats.cauchy]
distributions = dist_list_obj
dist_dict = dict(zip([dist.name for dist in distributions], distributions))

# Introducir valores para los cálculos
ticker = ['^NDX'] # '^GSPC' '^STOXX50E' '^GDAXI'  '^GSPC' '^IXIC'  '^DJI' ... 'SPY' 'AAPL' 'TSLA' ...
start_date = '2000-01-01'
end_date = '2023-03-26'

# Periodos a calcular (rango de sesiones)
periods = [1, 2, 3, 4] + list(range(5,41,5)) + list(range(60,221,20))
# Retornos a calcular (% variacion por periodos)
pct_below = list(range(-40,41,2))
pct_below.reverse()

# Descarga de datos
df = pd.DataFrame(yf.download(ticker, start=start_date, end=end_date)['Close'])
# df['Close'] = df['Adj Close'].copy()    ## Utilizar si se descarga 'Adj Close'
 
# Calcula el cambio porcentual del cierre respecto al cierre anterior de cada rango de periodos
for period in periods:
    df[f'{period}d_pct_change'] = df['Close'].pct_change(periods=period).mul(100)

# Dataframes de resultados vacios
results = {}
results['direct'] = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
for dist in dist_dict.keys():
     results[dist] = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])   
    
# Calculo directo sobre datos
print('Calculating direct calc')
for period in periods:
    for pct in pct_below:
        # Calcula el porcentaje de días en que el precio estuvo por debajo del pct
        pct_days = (df[f'{period}d_pct_change'] < pct).mean() * 100
        results['direct'].loc[len(results['direct'])] = [ticker, period, pct, pct_days]

# Calculo con las distribuciones
warnings.filterwarnings('error')
times = {}
params = {}
fails = []
for dist, dist_obj in dist_dict.items():
    print(f'Calculating {dist}')  
    start_time = time.time()
    params[f'p_{dist}'] = {}
    try:    
        for period in periods:
            # Ajuste de la distribución normal
            params[f'p_{dist}'][f'params_{period}d'] = dist_obj.fit(df[f'{period}d_pct_change'].dropna()) 
            for pct in pct_below:
                pct_days = dist_obj.cdf(pct, * params[f'p_{dist}'][f'params_{period}d']) * 100
                results[dist].loc[len(results[dist])] = [ticker, period, pct, pct_days]    
    except Exception as e:
            print(f"Error occurred for {dist}: {e}")
            fails.append(dist)
            del results[dist]
            continue   
    end_time= time.time()
    execution_time = end_time - start_time  # Duración de la iteración en segundos
    times[dist] = execution_time 
warnings.resetwarnings()
    
# Correlaciones de las distribuciones con los datos
correlations_df_global = pd.DataFrame(columns=['Distribution', 'Correlation', 'Execution_Time']) 
times['direct'] = 0
for dist in results.keys():
    correl = results['direct']['pct_days'].corr(results[dist]['pct_days'])
    correlations_df_global.loc[len(correlations_df_global)] = [dist, correl,times[dist]]

correlations_df_global = correlations_df_global.sort_values(by='Correlation', ascending=False)
correlations_df_global.reset_index(drop=True, inplace=True)
print(correlations_df_global)

#Correlaciones de las distribuciones de datos por periodos
columns = ['Distribution'] + [f'corr_{num}session' for num in periods]
correlations_df_periods = pd.DataFrame(columns=columns)
c = 0
for dist in results.keys():
    correlations_df_periods.loc[c, 'Distribution'] = dist
    for period in periods:
        a = results['direct'].loc[results['direct']['period'] == period, 'pct_days']
        b = results[dist].loc[results[dist]['period'] == period, 'pct_days']
        correl = a.corr(b)
        col = f'corr_{period}session'
        correlations_df_periods.loc[c, col] = correl  
    c = c+1
print(correlations_df_periods)

# HISTOGRAMAS CON DISTRIBUCIONES POR PERIODOS
for period in periods:
    period_graph = period
    variacion_diaria = df[f'{period_graph}d_pct_change'].dropna()
    # Figura en cada iteracion
    fig = plt.figure()
    # Crear el histograma
    plt.hist(variacion_diaria, bins=(max(pct_below)-min(pct_below)),density=True, alpha=0.5, label='Histograma')  # Ajusta el número de bins según tus preferencias
    # Generar curva de distribución normal
    x = np.linspace(min(variacion_diaria), max(variacion_diaria), 100)
    y = stats.norm.pdf(x,* params['p_norm'][f'params_{period_graph}d'])
    plt.plot(x, y, color='red', label='Distribución Normal')
    # Generar curva de distribución Johnsonsu
    y2 = stats.johnsonsu.pdf(x,* params['p_johnsonsu'][f'params_{period_graph}d'])
    plt.plot(x, y2, color='blue', label='Distribución Johnsonsu')
    # Personalizar el histograma
    plt.title(f'Histograma de Variación en {period_graph} sessiones')
    plt.xlabel('% de Variación en el periodo')
    plt.ylabel('Frecuencia')
    plt.legend()
    plt.show()









