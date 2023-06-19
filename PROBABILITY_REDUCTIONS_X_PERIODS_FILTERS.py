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
ticker = '^SPX'
start_date = '2000-01-01'
end_date = '2023-06-15'
# periods = [1, 2] + list(range(5,41,5)) + list(range(60,221,20))
periods = [1, 2, 3, 4, 5, 10, 15]
# pct_below = list(range(-20,21,1))
pct_below_t = list(range(-30,22,1))
pct_below = [value / 5 for value in pct_below_t]
pct_below.reverse()
filtro_VIX = (25, 35)

df = pd.DataFrame(yf.download([ticker, '^VIX'], start=start_date, end=end_date)['Close'])

# Calcula el cambio porcentual del cierre respecto al cierre anterior en cada periodo
for period in periods:
    df[f'{period}d_pct_change'] = df[ticker].pct_change(periods=period).mul(100)


df_filter = df[(df['^VIX'].shift(1) > filtro_VIX[0]) & (df['^VIX'].shift(1) < filtro_VIX[1])]

# Calculo directo sobre datos
results = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating direct calc')
for period in periods:
    for pct in pct_below:
        # Calcula el porcentaje de días en que el precio estuvo por debajo del pct
        pct_days = (df_filter[f'{period}d_pct_change'] < pct).mean() * 100
        results.loc[len(results)] = [ticker, period, pct, pct_days]

# Calculo por distribución normal
results_norm = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating normal')
for period in periods:
    media = df[f'{period}d_pct_change'].mean()
    desviacion_estandar = df_filter[f'{period}d_pct_change'].std()        
    for pct in pct_below:
        # Calcula el porcentaje de días en que el precio estuvo por debajo del pct
        pct_days = norm.cdf(pct, loc=media, scale=desviacion_estandar) *100
        results_norm.loc[len(results_norm)] = [ticker, period, pct, pct_days]

# Calculo por Johnson Su
results_john = pd.DataFrame(columns=['ticker', 'period', 'pct_below', 'pct_days'])
print('Calculating Johnson Su')
for period in periods:
    # Calcula los parámetros de la distribución Johnson Su
    params = johnsonsu.fit(df_filter[f'{period}d_pct_change'].dropna())
    for pct in pct_below:
        # Calcula la probabilidad utilizando la distribución Johnson Su
        pct_days = johnsonsu.cdf(pct, *params) * 100
        results_john.loc[len(results_john)] = [ticker, period, pct, pct_days]

  
# Crear un mapa de calor para cada ticker. Calculo directo
heatmap_data = pd.pivot_table(results, values='pct_days', index='pct_below', columns='period', sort = False)

plt.figure(figsize=(14,8))
sns.set_style('ticks')
sns.heatmap(heatmap_data, cmap= 'YlGnBu', annot=True, fmt=".2f", annot_kws={"fontsize":8})

plt.xlabel('Nº de sesiones', fontsize=20) 
plt.ylabel('Probabilidad rendimiento inferior a\n\n %', fontsize=16)
plt.title(f'{ticker} -  Datos históricos ente {start_date} y {end_date} - Direct calc\n Filtro VIX entre {filtro_VIX[0]} y {filtro_VIX[1]}', fontsize=24)
          
plt.show()

# Crear un mapa de calor para cada ticker. Calculo Distribucion Normal
heatmap_data = pd.pivot_table(results, values='pct_days', index='pct_below', columns='period', sort = False)

plt.figure(figsize=(14,8))
sns.set_style('ticks')
sns.heatmap(heatmap_data, cmap= 'YlGnBu', annot=True, fmt=".2f", annot_kws={"fontsize":8})

plt.xlabel('Nº de sesiones', fontsize=20) 
plt.ylabel('Probabilidad rendimiento inferior a\n\n %', fontsize=16)
plt.title(f'{ticker} -  Datos históricos ente {start_date} y {end_date} - Dist normal \n', fontsize=24)
          
plt.show()

# Crear un mapa de calor para cada ticker. Calculo Distribucion Johnson Su
heatmap_data = pd.pivot_table(results, values='pct_days', index='pct_below', columns='period', sort = False)

plt.figure(figsize=(14,8))
sns.set_style('ticks')
sns.heatmap(heatmap_data, cmap= 'YlGnBu', annot=True, fmt=".2f", annot_kws={"fontsize":8})

plt.xlabel('Nº de sesiones', fontsize=20) 
plt.ylabel('Probabilidad rendimiento inferior a\n\n %', fontsize=16)
plt.title(f'{ticker} -  Datos históricos ente {start_date} y {end_date} - Jonhson Su \n', fontsize=24)
          
plt.show()
