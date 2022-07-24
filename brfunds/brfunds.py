#For date and Time Manipulation
import datetime
import time
#Formatting
from typing import List, Union, Iterable

#Data Manipulation
import numpy as np
import pandas as pd

#Request from api
from . import api

pd.options.mode.chained_assignment = None

VALUE = 'values'
DATE = 'dates'
NAME = 'socialName'
CNPJ = 'cnpj'


#Get rentability of funds
def _baseGetData(cnpjs: Iterable[str], scrapType: str, benchmarks: List[str] = None, period: str = None,
                 start: Union[str, datetime.date] = None, end: Union[str, datetime.date] = None,
                 multiplier: float = 1) -> pd.DataFrame:
    """
    Return a pandas.DataFrame representing a time series with each observation
    indexed by its datetime.date and the following variables
        - CNPJ names (containing the rentability/volatility/shareholders/networth)
        - benchmarks names

    Params:
        - cnpjs: The list of fund cnpjs. You can get this info through the searchFund function
        - scrapType: Type of data to pull
            - Accept Values: 'rentability', 'volatility', 'shareholder', 'networth', 'drawdown'
        - benchmarks: Reference Index.
            - Accept Values: 'cdi', 'ibovespa', 'ipca', 'poupanca'
        - period: Time Analysis, None return all data,
            - Accept Values: '1w', '2w','1m','2m','3m','6m','1y','2y','3y', '4y', '5y'.
        - start and end: Timeframe to search for funds in.
            - Accept Values: datetime.date or string with format 'dd/mm/yy'
        - multiplier: ratio to scale the data points by

    """

    #Convert text to right format
    cnpjList = []
    for cnpj in cnpjs:
        cnpjList.append(__nameTreatment(cnpj))


    #Convert string to datetime format
    if isinstance(end, str):
        end = datetime.datetime.strptime(end, '%d/%m/%y')
    if isinstance(start, str):
        start = datetime.datetime.strptime(start, '%d/%m/%y')

    #Logic to start, end and period
    endEpoch = __endTreatment(end, start, period)
    startEpoch = __startTreatment(start, end, period)

    # Try to get the data 5 times before quitting
    for _ in range(5):
        try:
            data = __getData(cnpjList, scrapType, benchmarks=benchmarks, start=startEpoch, end=endEpoch)
            break
        except KeyError:
            time.sleep(1)
            continue
        except AttributeError:
            time.sleep(1)
    else:
        print('Check CVM (http://sistemas.cvm.gov.br/fundos.asp) or Comparador de Fundos (https://www.comparadordefundos.com.br) for a valid fund name')
        raise ConnectionError("Could not load funds from page.")

    finalList = pd.DataFrame({'Date': []})
    for fund in data:
        if scrapType == 'drawdown':
            valueList = list(list(zip(*fund[VALUE]))[0])
        else:
            valueList = fund[VALUE]
        dateList = api.as_date(fund[DATE])

        fundDict = {
            'Date': np.array(dateList),
            f'{fund["indicatorName"].upper()}': np.array(valueList)
        }

        final = pd.DataFrame(fundDict)
        final = final.dropna()
        final[fund["indicatorName"].upper()] = final[fund["indicatorName"].upper()] * multiplier

        final.set_index('Date', inplace=True)
        finalList = pd.merge(finalList, final, how='outer', on='Date')

    return finalList.set_index('Date')


def getFundsRentability(*cnpjs: str, benchmarks: List[str] = None, period: str = None,
                        start: Union[str, datetime.date] = None,
                        end: Union[str, datetime.date] = None) -> pd.DataFrame:
    """Return the profitability data for the specified cnpjs

    See _baseGetData for parameter reference
    """
    return _baseGetData(cnpjs, scrapType='rentability', benchmarks=benchmarks, period=period,
                        start=start, end=end, multiplier=1/100)


def getFundsVolatility(*cnpjs: str, period: str = None, start: Union[str, datetime.date] = None,
                       end: Union[str, datetime.date] = None) -> pd.DataFrame:
    """Return the volitility data for the specified cnpjs

    See _baseGetData for parameter reference
    """
    return _baseGetData(cnpjs, scrapType='volatility', period=period, start=start, end=end,
                        multiplier=1/100)


def getFundsShareholders(*cnpjs: str, period: str = None, start: Union[str, datetime.date] = None,
                         end: Union[str, datetime.date] = None) -> pd.DataFrame:
    """Return the shareholder amount data for the specified cnpjs

    See _baseGetData for parameter reference
    """
    return _baseGetData(cnpjs, scrapType='shareholder', period=period, start=start, end=end)


def getFundsNetWorth(*cnpjs: str, period: str = None, start: Union[str, datetime.date] = None,
                     end: Union[str, datetime.date] = None) -> pd.DataFrame:
    """Return the net worth data for the specified cnpjs

    See _baseGetData for parameter reference
    """
    return _baseGetData(cnpjs, scrapType='networth', period=period, start=start, end=end)


def getFundsDrawdown(*cnpjs: str, period: str = None, start: Union[str, datetime.date],
                     end: Union[str, datetime.date] = None) -> pd.DataFrame:
    """Return the drawdown data for the specified cnpjs

    See _baseGetData for parameter reference
    """
    return _baseGetData(cnpjs, scrapType='drawdown', period=period, start=start, end=end,
                        multiplier=1/100)


def __nameTreatment(name: str, search: bool = False) -> str:
    name = name.lower()
    replace_map = {
        'a': 'ãáâ',
        'e': 'éê',
        'i': 'í',
        'o': 'õóô',
        'u': 'ú',
        'c': 'ç',
        '': '.-/',
    }
    if search is False: 
        replace_map['-'] = " "
    else:
        replace_map['+'] = " "

    for new, old_letters in replace_map.items():
        for old in old_letters:
            name = name.replace(old, new)

    return name


def __startTreatment(start: datetime.datetime, end: datetime.datetime, period: str) -> int:
    if start is None and period is None:
        start = datetime.datetime(2000, 1, 1)
    elif start is None and period is not None:
        return __getPeriodOptions(period, end)
    return int(start.timestamp()*1000)

  
def __endTreatment(end: datetime.datetime, start: datetime.datetime, period: str) -> int:
    if end is None and period is None or end is None and period is not None and start is None:
        end = datetime.datetime.today()
    elif end is None and period is not None and start is not None:
        end = __getPeriodOptions(period, start, signal=False)

    return int(end.timestamp()*1000)


def __getData(cnpjs: Iterable[str], type: str, start: int, end: int, benchmarks: List[str] = None):
    if type == 'rentability':
        data = api.rentabilityInfo(cnpjs, benchmarks=benchmarks, startDate=start, endDate=end)
    if type == 'volatility':
        data = api.volatilityInfo(cnpjs, startDate=start, endDate=end)
    if type == 'shareholder':
        data = api.shareholderInfo(cnpjs, startDate=start, endDate=end)
    if type == 'networth':
        data = api.networthInfo(cnpjs, startDate=start, endDate=end)
    if type == 'drawdown':
        data = api.drawdownInfo(cnpjs, startDate=start, endDate=end)
    return data


def __getPeriodOptions(period: str, reference: datetime.datetime, signal: bool = True) -> int:
    if signal:
        signal = 1
    else:
        signal = -1
    reference = reference.timestamp() * 1000
    periodOptions = {'1w': reference - signal * 604800 * 1000,
                     '2w': reference - signal * 1209600 * 1000,
                     '1m': reference - signal * 2629743 * 1000,
                     '2m': reference - signal * 2629743 * 2000,
                     '3m': reference - signal * 2629743 * 3000,
                     '6m': reference - signal * 2629743 * 6000,
                     '1y': reference - signal * 31556926 * 1000,
                     '2y': reference - signal * 31556926*2000,
                     '3y': reference - signal * 31556926*3000,
                     '4y': reference - signal * 31556926*4000,
                     '5y': reference - signal * 31556926*5000}
    return periodOptions[period]


def searchFund(name: str, max_size: int = 20) -> pd.DataFrame:
    """Return a list with funds with similar names, can control the size of the list with the max_size parameter, default 20"""
    name = __nameTreatment(name, search=True)
    fundData = api.search(name, max_size)
    fundList = __getFundNames(fundData)
    return fundList


def __getFundNames(data: List) -> pd.DataFrame:
    fundList = []
    cnpjList = []
    for fund in data:
        fundList.append(fund[NAME])
        cnpjList.append(fund[CNPJ])
    data = pd.DataFrame({'Nome': fundList, 'CNPJ': cnpjList})
    return data
