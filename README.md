[![PyPI Latest Release](https://img.shields.io/pypi/v/brfunds.svg)](https://pypi.org/project/brfunds/)
[![Package Status](https://img.shields.io/pypi/status/brfunds.svg)](https://pypi.org/project/brfunds/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/brfunds.svg)](https://pypi.org/project/brfunds/)

[English]
Brazilian Fund Scrapper (or brfunds) is a package to recover data from investment funds without the need to download data to your computer. It uses the data available on https://comparadordefundos.com.br/ and can be used to Time Series Analysis of earnings, net assets and number of  shareholders. It can also be used for comparing rentability of different funds.

Ps: Due to changes on the api, the search is done exclusively with the CNPJ of the fund (company id), this changed occured starting on version 0.2.0.

[Português]
Brazilian Fund Scrapper (ou brfunds) é um pacote para obter dados de fundos de investimentos brasileiros sem precisar baixar arquivos para o drive do computador. Ele utiliza o banco de dados disponível em https://comparadordefundos.com.br/ e pode ser usado para Análise de Séries Temporais da rentabilidade, patrimônio do fundo e do número de cotistas.

Obs: Por conta de mudanças na api, a busca pelos fundos é feita exclusivamente pelo CNPJ do fundo, a mudança é válida a partir da versão 0.2.0.

Examples:

```python
from brfunds import searchFund

#The search fuction can be used to get the fund CNPJ (brazilian company id)
# The max_size param can be used to control the size of the search 
searchFund('Example Fund', max_size = 1)
```
|   Name         | CNPJ               |
|----------------|--------------------|
| Example Fund 1 | 00.000.000/0000-00 |

```python
from brfunds import getFundsEarnings

#With the CNPJ, you can get data from the statistic of the fund 
getFundsEarnings('00.000.000/0000-00')
```

|   Date    | Example Fund 1 |
|-----------|----------------|
|2016-01-31 | 0.000000       |
|2016-02-01 | -0.000715      |
|2016-02-06	| -0.009902      |
|2016-02-07	| -0.009009      |
|2016-02-08	| -0.007612      |
| ...       |  ...           |
|2021-06-02	| 0.910064       |
|2021-06-04	| 0.914201       |
|2021-06-07	| 0.917008       |
|2021-06-08	| 0.911554       |
|2021-06-09	| 0.911601       |

```python
#It can also be used to multiple funds and benchmarks
getFundsEarnings('00.000.000/0000-00','00.000.000/0000-00', benchmarks = ['cdi','ibovespa'], start = '31/01/16', end = '09/06/21')
```

|   Date    | Example Fund 1 | Example Fund 2 | CDI     | IBOV       |
|-----------|----------------|----------------|---------|------------|
|2016-01-31 | 0.000000       |  0.00000       | 0.00000 |  0.00000   |
|2016-02-01 | -0.000715      |  0.001136      | 0.000525| -0.048653  |
|2016-02-06	| -0.009902      | -0.005026      | 0.001049| -0.024186  |
|2016-02-07	| -0.009009      | -0.006855      | 0.001575|  0.006204  |
|2016-02-08	| -0.007612      | -0.009379      | 0.002100|  0.000544  |
| ...       |  ...           |  ...           | ...     |  ...       |
|2021-06-02	| 0.910064       | 1.324291       | 0.450420|  2.194512  |
|2021-06-04	| 0.914201       | 1.323814       | 0.450612|  2.207436  |
|2021-06-07	| 0.917008       | 1.323690       | 0.450805|  2.22347   |
|2021-06-08	| 0.911554       | 1.327529       | 0.450997|  2.199088  |
|2021-06-09	| 0.911601       | 1.329402       | 0.451190|  2.202039  |

```python
#The package also includes functions for drawdown, 30d Volatility, Number of Shareholders and Net Worth. 
getFundsDrawdown('00.000.000/0000-00','00.000.000/0000-00', start = '08/01/20')
getFundsVolatility('00.000.000/0000-00', start = '13/10/20')
getFundsShareholders('00.000.000/0000-00','00.000.000/0000-00')
getFundsNetWorth('00.000.000/0000-00', end = '31/12/18')
```