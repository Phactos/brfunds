#For date and Time Manipulation
import datetime
import time
#Formatting
from typing import Dict, List, Optional, Tuple, Union

#Data Manipulation
import numpy as np
import pandas as pd

#Request from api
import api

pd.options.mode.chained_assignment = None

VALUE = 'values'
DATE = 'dates'
NAME = 'socialName'
CNPJ = 'cnpj'

#Get rentability of funds
def _baseGetData(cnpj: tuple, scrapType,benchmark: List[str] = None, period: str = None,
            start: Union[str, datetime.date] = None, end: Union[str, datetime.date] = None, multiplier = 1) -> pd.DataFrame:
    """
    Return a pandas.DataFrame representing a time series with each observation
    indexed by its datetime.date and the following variables
        - Value

    Params:
        - cnpj: The fund's cnpj, you can get this info throught searchFund function
        - benchmark: Reference Index.
            - Accept Values: ['cdi', 'ibovespa', 'ipca', 'poupanca']
        - period: Time Analysis, None return all data,
            - Accept Values: '1w', '2w','1m','2m','3m','6m','1y','2y','3y', '4y', '5y'.
        - start and end: Timeframe to search for funds in.
            - Accept Values: datetime.date or string with format 'dd/mm/yy'

    """

    #Convert text to right format
    nameList = []
    for name in cnpj:
        nameList.append(__nameTreatment(name))


    #Convert string to datetime format
    if isinstance(end, str):
        end = datetime.datetime.strptime(end, '%d/%m/%y')
    if isinstance(start, str):
        start = datetime.datetime.strptime(start, '%d/%m/%y')

    #Logic to start, end and period
    end = __endTreatment(end, start, period)
    start = __startTreatment(start, end, period)

    # Try to get the data 5 times before quitting
    for _ in range(5):
        try:
            data = __getData(nameList, scrapType,benchmark= benchmark,start=start, end= end)
            break
        except KeyError:
            time.sleep(1)
            continue
        except AttributeError:
            time.sleep(1)
    else:
        print('Check CVM (http://sistemas.cvm.gov.br/fundos.asp) or Comparador de Fundos (https://www.comparadordefundos.com.br) for a valid fund name')
        raise ConnectionError("Could not load funds from page.")

    FinalList = pd.DataFrame({'Date' : []})
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
        FinalList = pd.merge(FinalList, final, how='outer',on='Date')

    return FinalList.set_index('Date')

def getFundsRentability(*cnpj, benchmark: List[str] = None, period: str = None,
            start: Union[str, datetime.date] = None, end: Union[str, datetime.date] = None) -> pd.DataFrame:
    return _baseGetData(cnpj, scrapType='rentability',benchmark= benchmark,period=period,start=start,end=end, multiplier=1/100)

def getFundsVolatility(*cnpj, period: str = None,
            start: Union[str, datetime.date] = None, end: Union[str, datetime.date] = None) -> pd.DataFrame:
    return _baseGetData(cnpj, scrapType='volatility',period=period,start=start,end=end, multiplier=1/100)

def getFundsShareholders(*cnpj, period: str = None,
            start: Union[str, datetime.date] = None, end: Union[str, datetime.date] = None) -> pd.DataFrame:
    return _baseGetData(cnpj, scrapType='shareholder',period=period,start=start,end=end)

def getFundsNetWorth(*cnpj, period: str = None,
            start: Union[str, datetime.date] = None, end: Union[str, datetime.date] = None) -> pd.DataFrame:
    return _baseGetData(cnpj, scrapType='networth',period=period,start=start,end=end)

def getFundsDrawdown(start: Union[str, datetime.date],*cnpj, period: str = None,
             end: Union[str, datetime.date] = None) -> pd.DataFrame:
    return _baseGetData(cnpj, scrapType='drawdown',period=period,start=start,end=end, multiplier=1/100)

def __nameTreatment(name :str, search = False):
    name = name.lower()
    replace_map = {
        'a': 'ãáâ',
        'e': 'éê',
        'i': 'í',
        'o': 'õóô',
        'u': 'ú',
        'c': 'ç',
        '' : '.-/',
    }
    if search is False: 
        replace_map['-'] = " "
    else:
        replace_map['+'] = " "

    for new, old_letters in replace_map.items():
        for old in old_letters:
            name = name.replace(old, new)

    return name


def __startTreatment(start, end, period):
    if start is None and period is None:
        start = datetime.datetime(2000, 1, 1)
    elif start is None and period is not None:
        return __getPeriodOptions(period, end)
    return int(start.timestamp()*1000)

  
def __endTreatment(end, start, period):    
    if end is None and period is None or end is None and period is not None and start is None:
        end = datetime.datetime.today()
    elif end is None and period is not None and start is not None:
        end = __getPeriodOptions(period, start, signal=False)

    return int(end.timestamp()*1000)


def __getData(cnpj, type,start, end, benchmark = None):
    if type == 'rentability':
        data = api.rentability_info(cnpj, benchmarks= benchmark, startDate=start,endDate=end)
    if type == 'volatility':
        data = api.volatility_info(cnpj, startDate=start,endDate=end)
    if type == 'shareholder':
        data = api.shareholder_info(cnpj, startDate=start, endDate=end)
    if type == 'networth':
        data = api.networth_info(cnpj, startDate=start,endDate=end)
    if type == 'drawdown':
        data = api.drawdown_info(cnpj, startDate=start,endDate=end)
    return data

def __getPeriodOptions(period, reference, signal=True):
    if signal:
        signal = 1
    else:
        signal = -1
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

def searchFund(name:str, max_size : int = 20) -> list:
    """Return a list with funds with similar names, can control the size of the list with the max_size parameter, default 20"""
    name = __nameTreatment(name, search=True)
    fundData = api.search(name, max_size)
    fundList = __getFundNames(fundData)
    return fundList

def __getFundNames(data):    
    fundList = []
    cnpjList = []
    for fund in data:
        fundList.append(fund[NAME])
        cnpjList.append(fund[CNPJ])
    data = pd.DataFrame({'Nome' : fundList, 'CNPJ' : cnpjList})
    return data
