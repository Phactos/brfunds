[![PyPI Latest Release](https://img.shields.io/pypi/v/brfunds.svg)](https://pypi.org/project/brfunds/)

[English]
Brazilian Fund Scrapper (or brfunds) is a package to recover data from investment funds without the need to download data to your computer. It uses the data available on https://comparadordefundos.com.br/ and can be used to Time Series Analysis of quote price, net assets and number of  shareholders. It can also be used for comparing rentability of different funds.

[Português]
Brazilian Fund Scrapper (ou brfunds) é um pacote para obter dados de fundos de investimentos brasileiros sem precisar baixar arquivos para o drive do computador. Ele utiliza o banco de dados disponível em https://comparadordefundos.com.br/ e pode ser usado para Análise de Séries Temporais do valor de cotas, patrimônio do fundo e do número de cotistas.

Examples:

```python
from brfunds import getFund

#Check CVM (http://sistemas.cvm.gov.br/fundos.asp) 
# or Comparador de Fundos (https://www.comparadordefundos.com.br/fundos-de-investimento) 
# for a valid fund name
getFund('Example Fund 1')
# You can also use the fund CNPJ as the name
```

|   Date    | Value      | Daily Variation |   Total Variation |
|-----------|------------|-----------------|-------------------|
|2008-01-31 | 500.000000 | 0.000000	       | 0.000000          |
|2008-02-01 | 499.642439 |-0.000715	       |-0.000715          |
|2008-02-06	| 495.049247 |-0.009193	       |-0.009902          |
|2008-02-07	| 495.495279 | 0.000901	       |-0.009009          |
|2008-02-08	| 496.193927 | 0.001410	       |-0.007612          |
| ...       | ...        | ...	           | ...               |
|2021-06-02	|1955.032101 | 0.002320	       | 2.910064          |
|2021-06-04	|1957.100361 | 0.001058	       | 2.914201          |
|2021-06-07	|1958.504200 | 0.000717	       | 2.917008          |
|2021-06-08	|1955.777186 |-0.001392	       | 2.911554          |
|2021-06-09	|1955.800510 | 0.000012	       | 2.911601          |



```python
#Filter by Date
getFund('Example Fund 2', start='15/03/10', end='15/03/20')

#or 

getFund('Example Fund 2', start=datetime.date(2010,3,15), end=datetime.date(2020,3,15))
```

|   Date    | Value      | Daily Variation |   Total Variation |
|-----------|------------|-----------------|-------------------|
|2010-03-15 | 2.921359   | 0.000000	       | 0.000000          |
|2010-03-16 | 2.925038   | 0.001259	       | 0.001259          |
|2010-03-17	| 2.922054	 |-0.001020	       | 0.000238          |
|2010-03-18	| 2.959106   | 0.012680	       | 0.012921          |
|2010-03-19	| 2.977092   | 0.006078	       | 0.019078          |
| ...       | ...        | ...	           | ...               |
|2020-03-09	| 8.545470   | 0.023635	       | 1.925169          |
|2020-03-10	| 8.379862   |-0.019380	       | 1.868481          |
|2020-03-11	| 8.552295   | 0.020577	       | 1.927505          |
|2020-03-12	| 8.666684   | 0.013375	       | 1.966661          |
|2020-03-13	| 8.722922   | 0.006489	       | 1.985912          |


```python
#Filter by period
getFund('Example Fund 3', period='2w')
```

|   Date    | Value      | Daily Variation |   Total Variation |
|-----------|------------|-----------------|-------------------|
|2021-06-01 | 66.362416  | 0.000000	       | 0.000000          |
|2021-06-02	| 66.339371  |-0.000347	       |-0.000347          |
|2021-06-04	| 66.355157	 | 0.000238	       |-0.000109          |
|2021-06-07	| 66.338489  |-0.000251	       |-0.000361          |
|2021-06-08	| 66.342636  | 0.000063	       |-0.000298          |
|2021-06-09	| 66.335420	 |-0.000109	       |-0.000407          |
|2021-06-10	| 66.321279  |-0.000213	       |-0.000620          |

```python
#Compare the results with the benchmark
#Available benchmarks: cdi, ipca and ibov
getFund('Example Fund 4', benchmark = 'ibov')
```
|   Date    | Value      | Daily Variation |   Total Variation | IBOVESPA |
|-----------|------------|-----------------|-------------------|------|
|2019-11-29	|10.000000	|0.000000	|0.000000	|0.000000|
|2019-12-02	|10.066960	|0.006696	|0.006696	|0.006421|
|2019-12-03	|10.041310	|-0.002548	|0.004131	|0.006680|
|2019-12-04	|10.167330	|0.012550	|0.016733	|0.019107|
|2019-12-05	|10.192820	|0.002507	|0.019282	|0.022073|
|...|	...|	...|	...|	...|
|2021-06-02	|12.126600	|0.016673	|0.212660	|0.197430|
|2021-06-04	|12.169782	|0.003561	|0.216978	|0.202275|
|2021-06-07	|12.250059	|0.006596	|0.225006	|0.208285|
|2021-06-08	|12.152019	|-0.008003	|0.215202	|0.199145|
|2021-06-09	|12.153443	|0.000117	|0.215344	|0.200251|



```python
#Obtain data about Net Assets and # of Shareholders
getFund('Example Fund 5', fullData = True)
```
|Date | Value | Net Assets | # of Shareholders | Daily Variation | Total Variation |
|----|----|----|----|----|----|
|2020-11-16	|100.000000	|6130.00	|6	|0.000000	|0.000000
|2020-11-17	|99.727896	|6113.32	|6	|-0.002721	|-0.002721
|2020-11-18	|99.640946	|7228.91	|13	|-0.000872	|-0.003591
|2020-11-19	|99.828543	|7642.52	|14	|0.001883	|-0.001715
|2020-11-20	|99.508648	|9318.03	|17	|-0.003204	|-0.004914
|... |	...	|...|	...	|...|	... |
|2021-06-02	|117.688508	|5578444.17	|5892|	0.007624|	0.176885
|2021-06-04	|118.225607	|5748230.07	|6005|	0.004564|	0.182256
|2021-06-07	|118.538179	|5882600.39	|6231|	0.002644|	0.185382
|2021-06-08	|118.133825	|6074472.90	|6556|	-0.003411|	0.181338
|2021-06-09	|117.782325	|6249691.48	|6865|	-0.002975|	0.177823