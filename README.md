# RETURNS_DISTRIBUTIONS_STUDY
 Utilidades diversas para el estudio de los rendimientos de los activos a diferentes plazos y sus distribuciones


## PROBABILITY_REDUCTIONS_X_PERIODS
Cálculo de las probabilidades de un rendimiento INFERIOR A X% en un periodo de Y sesiones.

CREACIÓN DE MAPA DE CALOR CON EL % DE PROBABILIDADES DE UN RENDIMIENTO INFERIOR A UN  +-'X %' EN UN PERIODO DE TIEMPO DE 'Y' SESIONES

Se utilizan 3 métodos diferentes de cálculo y sus 3 mapas de calor correspondientes para cada ticker:
- Cálculo directo sobre los datos
- Cálculo por distribución normal
- Cálculo por distribución Johnson Su

#### Entrada de datos:
- tickers = ticker o lista de tickers
- start_date = Fecha de inicio de los datos a analizar
- end_date => Fecha de fin de los datos a analizar
- periods => Lista de los intervalos de sesiones a visualizar los datos
- pct_below => Rango y paso de los % a calcular

### Salidas:
- 3 mapas de calor por ticker introducido (calculo directo + calculo con ditribución normal + cálculo con distribución Johnson Su
Los datos indican la probabilidad de un rendimiento INFERIOR A cada %
(Para obtener la probabilidad de rendimiento SUPERIOR A --> 100 - resultado de la tabla)

## PROBABILITY_REDUCTIONS_X_PERIODS_DISTRIBUTIONS
Estudio de correlación de la distribució real de los retornos de un activo a diferentes plazos con diferentes tipos de curvas de distribución.

Se realiza un estudio de correlación de las disctribuciones. Se analizan todas las distribuciones continuas calculables con los datos de la librería scipy.stats

### Entrada de datos: 
- tickers = ticker (Un solo ticker por cálculo, no introducir lista de tickers)
- start_date = Fecha de inicio de los datos a analizar
- end_date = Fecha de fin de los datos a analizar
- periods = Lista de los intervalos de sesiones a visualizar los datos
- pct_below = Rango y paso de los % a calcular

### Salidas:
- correlations_df_global --> Dataframe con las correlaciones del total de los datos con cada distribución.
(incluye tiempo de ejecución requerido para el cálculo de cada distribución)
- correlations_df_periods -->  Dataframe con las correlaciones periodo por periodo con cada distribución.
- 1 gráfico de histograma de los retornos + curvas de distribución, por cada periodo introducido.
