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