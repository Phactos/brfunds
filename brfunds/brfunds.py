from typing import Optional, Union

import json
import requests
import datetime

from bs4 import BeautifulSoup

import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None

FUND_OBSERVATIONS = 'r'

OBS_DATE = 'd'
OBS_VALUE = 'q'
OBS_PATRIMONY = 'nw'
OBS_SHAREHOLDER = 'qh'


def getFund(fundName: str, benchmark: str = None, type_: str = None, period: str = None,
            start: Union[str, datetime.date] = None, end: Union[str, datetime.date] = None,
            fullData: bool = False) -> pd.DataFrame:
    """
    Return a pandas.DataFrame representing a time series with each observation
    indexed by its datetime.date and the following variables
        - Value
        - Daily Variation
        - Total Variation
        - Net Assets (if fullData)
        - # of Shareholders (if FullData)

    Params:
        - fundName: The fund name (will find the closest result to the given name)
        - benchmark: Reference Index.
            - Accept Values: 'cdi', 'ibov', 'ipca'
        - type_: Type of the investment, usually work as default.
            - Accept values: 'acao', 'fixa', 'cambial' or 'multi'.
        - period: Time Analysis, None return all data,
            - Accept Values: '1w', '2w','1m','2m','3m','6m','1y','2y','3y', '4y', '5y'.
        - start and end: Timeframe to search for funds in.
            - Accept Values: datetime.date or string with format 'dd/mm/yy'
        - fullData: Whether to return the time series of quote holders and patrimony

    """

    name, type_, start, end = __paramTreatment(fundName, type_, start, end, period)

    data = __getData(name, type_)
    fund = data['props']['pageProps']['fund']

    value, date, netAssets, shareholders = __extractDataColumns(fund, start, end)

    finalDict = {
        'Date': np.array(date),
        'Value': np.array(value)
    }
    if fullData:
        finalDict['Net Asssets'] = np.array(netAssets)
        finalDict['# of Shareholders'] = np.array(shareholders)

    final = pd.DataFrame(finalDict)
    final["Daily Variation"] = final['Value'].pct_change()
    final['Daily Variation'][0] = 0
    final['Total Variation'] = final['Value'] / final['Value'][0] - 1
    final.set_index('Date', inplace=True)
    if benchmark is not None:
        bench = __getBenchmark(benchmark, final.index[0], final.index[-1], data)
        final = pd.merge(final, bench, 'inner', left_index=True, right_index=True)
        final['Total Variation'] = final['Value'] / final['Value'][0] - 1
    return final


def get_funds(fundList: list[str], type_: str = None, period: str = None,
              start: Union[str, datetime.date] = None, end: Union[str, datetime.date] = None):
    """
    Params:
        - fundList: List with the strings of the fund names.
        - type_: Type of the investment, usually work as default.
            - Accept values: 'acao', 'fixa', 'cambial' or 'multi'.
        - period: Time Analysis, None return all data,
            - Accept Values: '1w', '2w','1m','2m','3m','6m','1y','2y','3y', '4y', '5y'.
        - start and end: You can also set the date,
            - Accept Values: datetime.date or string with format 'dd/mm/yy'
    """

    listFinalDict = {}
    for fundName in fundList:
        name, type_, start, end = __paramTreatment(fundName, type_, start, end, period)

        data = __getData(name, type_)
        fund = data['props']['pageProps']['fund']

        value, date, _, _ = __extractDataColumns(fund, start, end)

        finalDict = {
            'Date': np.array(date),
            'Value': np.array(value)
        }

        final = pd.DataFrame(finalDict)
        final.set_index('Date', inplace=True)
        if len(final['Value']) > 1:
            listFinalDict[fundName] = final['Value'] / final['Value'][0] - 1

    listFinal = pd.DataFrame(listFinalDict)
    return listFinal


def __extractDataColumns(fund: dict, start: datetime.date, end: datetime.date) -> \
        tuple[list, list, list, list]:
    value = []
    date = []
    patrimony = []
    shareholders = []

    fund_observations = fund[FUND_OBSERVATIONS]
    for observation in fund_observations:
        tempDate = datetime.datetime.strptime(observation[OBS_DATE], '%Y-%m-%d').date()
        if start <= tempDate <= end:
            date.append(tempDate)
            value.append(observation[OBS_VALUE])
            patrimony.append(observation[OBS_PATRIMONY])
            shareholders.append(observation[OBS_SHAREHOLDER])

    return value, date, patrimony, shareholders


def __paramTreatment(fundName: str, type_: str,
                     start: Union[str, datetime.date], end: Union[str, datetime.date],
                     period: Optional[str]) -> tuple[str, str, datetime.date, datetime.date]:
    name = __nameTreatment(fundName)

    if type_ is None:
        type_ = 'acao'

    if isinstance(end, str):
        end = datetime.datetime.strptime(end, '%d/%m/%y').date()
    if isinstance(start, str):
        start = datetime.datetime.strptime(start, '%d/%m/%y').date()

    end = __endTreatment(end, start, period)
    start = __startTreatment(start, end, period)

    return name, type_, start, end


def __nameTreatment(name):
    name = name.lower()
    replace_map = {
        "-": " ",
        'a': 'ãáâ',
        'e': 'éê',
        'i': 'í',
        'o': 'õóô',
        'u': 'ú',
        'c': 'ç'
    }
    for new, old_letters in replace_map.items():
        for old in old_letters:
            name = name.replace(old, new)

    return name


def __startTreatment(start, end, period):
    if start is None and period is None:
        start = datetime.date(1, 1, 1)
    elif start is None and period is not None:
        start = __getPeriodOptions(period, end)
    return start


def __endTreatment(end, start, period):
    if end is None and period is None:
        end = datetime.date.today()
    elif end is None and period is not None and start is not None:
        end = __getPeriodOptions(period, start, signal=False)

    return end


def __getData(name, type_):
    type_ = __nameTreatment(type_)
    typeOptions = {'acao': 'fundos-de-acoes',
                   'fixa': 'fundos-de-renda-fixa',
                   'cambial': 'fundos-cambial',
                   'multi': 'fundos-multimercado'}
    url = f"https://www.comparadordefundos.com.br/fundos-de-investimento/{typeOptions[type_]}/{name}?period=otimo"
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find(id="__NEXT_DATA__").contents
    data = [json.loads(script) for script in table][0]
    return data


def __getBenchmark(benchmark, start, end, data):
    benchmark = benchmark.lower()
    benchmarkOptions = {'cdi': 'cdi', 'ibov': 'ibovespa', 'ipca': 'ipca', 'ibovespa': 'ibovespa'}
    benchmarkData = data["props"]["initialReduxState"][benchmarkOptions[benchmark]]
    bench = []
    benchDate = []
    funds = benchmarkData[FUND_OBSERVATIONS]
    for i in range(len(funds)):
        tempDate = datetime.datetime.strptime(funds[i]['d'], '%Y-%m-%d').date()
        if start <= tempDate <= end:
            bench.append(funds[OBS_VALUE])
            benchDate.append(tempDate)

    bench = np.array(bench)
    benchDate = np.array(benchDate)
    bench = bench / bench[0] - 1
    benchmarkData = {
        f'{benchmarkOptions[benchmark]}'.upper(): bench,
        'Date': benchDate
    }
    bench = pd.DataFrame(benchmarkData)
    bench.set_index('Date', inplace=True)
    return bench


def __getPeriodOptions(period, reference, signal=True):
    if signal:
        signal = 1
    else:
        signal = -1
    periodOptions = {'1w': reference - signal * datetime.timedelta(days=7),
                     '2w': reference - signal * datetime.timedelta(days=14),
                     '1m': reference - signal * datetime.timedelta(days=30),
                     '2m': reference - signal * datetime.timedelta(days=60),
                     '3m': reference - signal * datetime.timedelta(days=91),
                     '6m': reference - signal * datetime.timedelta(days=182),
                     '1y': reference - signal * datetime.timedelta(days=365),
                     '2y': reference - signal * datetime.timedelta(days=730),
                     '3y': reference - signal * datetime.timedelta(days=1095),
                     '4y': reference - signal * datetime.timedelta(days=1460),
                     '5y': reference - signal * datetime.timedelta(days=1825)}
    return periodOptions[period]
