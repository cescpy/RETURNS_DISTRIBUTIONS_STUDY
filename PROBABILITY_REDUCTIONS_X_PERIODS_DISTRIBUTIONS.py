# -*- coding: utf-8 -*-
"""
COMPARATIVA DE CALCULO DE PROBABILIDADES DE RENDIMIENTOS OPBTENIDOS POR PERIODOS DE TIEMPO UTILIZANDO DIFERENTES DISTRIBUCIONES
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
ticker = ['^GSPC'] # '^GSPC' '^STOXX50E' '^GDAXI'  '^GSPC' '^IXIC'  '^DJI' ... 'SPY' 'AAPL' 'TSLA' ...
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
correlations = {}
print('\nCorrelaciones con los datos originales:')
for dist in results.keys():
    correlations[dist] = results['direct']['pct_days'].corr(results[dist]['pct_days'])
    print(f'Distribución {dist} =  {correlations[dist]}')

correlations_df = pd.DataFrame(columns=['Distribution', 'Correlation', 'Execution_Time']) 
times['direct'] = 0
for dist in results.keys():
    correl = results['direct']['pct_days'].corr(results[dist]['pct_days'])
    correlations_df.loc[len(correlations_df)] = [dist, correl,times[dist]]

correlations_df = correlations_df.sort_values(by='Correlation', ascending=False)
correlations_df.reset_index(drop=True, inplace=True)
print(correlations_df)


# HISTOGRAMA BASICO
period_graph = 160

variacion_diaria = df[f'{period_graph}d_pct_change'].dropna()
# Crear el histograma
plt.hist(variacion_diaria, bins=(max(pct_below)-min(pct_below)),density=True, alpha=0.5, label='Histograma')  # Ajusta el número de bins según tus preferencias
# Generar curva de distribución normal
x = np.linspace(min(variacion_diaria), max(variacion_diaria), 100)
y = stats.norm.pdf(x,* params['p_norm'][f'params_{period_graph}d'])
plt.plot(x, y, color='red', label='Distribución Normal')
# Generar curva de distribución Johnsonsu
x2 = np.linspace(min(variacion_diaria), max(variacion_diaria), 100)
y2 = stats.johnsonsu.pdf(x,* params['p_johnsonsu'][f'params_{period_graph}d'])
plt.plot(x2, y2, color='blue', label='Distribución Johnsonsu')
# Personalizar el histograma
plt.title(f'Histograma de Variación en {period_graph} sessiones')
plt.xlabel('% de Variación en el periodo')
plt.ylabel('Frecuencia')
plt.legend()
plt.show()



'''
# Lista de colores para las distribuciones
colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive']

# Crear el gráfico
for i, period in enumerate(periods):
    # Obtener los datos de 'pct_days' y 'pct_below' para el período actual
    data = results[results['period'] == period]
    x = data['pct_below']
    y = data['pct_days']

    # Crear la figura y los ejes
    fig, ax = plt.subplots()

    # Histograma de los datos de 'pct_days' obtenidos con el cálculo directo
    ax.hist(y, bins=20, density=True, alpha=0.5, color='lightblue', label='Cálculo directo')

    # Curvas de las distribuciones calculadas
    for j, dist_name in enumerate(['norm', 'john', 'lognorm', 'student', 'exp', 'logistic', 'pareto', 'laplace', 'cauchy']):
        dist_results = eval('results_' + dist_name)
        dist_data = dist_results[dist_results['period'] == period]
        dist_pct_days = dist_data['pct_days']
        ax.plot(x, dist_pct_days, color=colors[j], label=dist_name.capitalize())

    # Configuraciones adicionales del gráfico
    ax.set_title(f'Period: {period} days')
    ax.set_xlabel('Percentage Below')
    ax.set_ylabel('Percentage of Days')
    ax.legend()

    # Mostrar el gráfico
    plt.show()
'''






