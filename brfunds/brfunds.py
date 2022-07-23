#For date and Time Manipulation
import datetime
import time
#Formatting
from typing import Dict, List, Optional, Tuple, Union

#Data Manipulation
import numpy as np
import pandas as pd

#Request from api
from api import search, rentability_info, as_date

pd.options.mode.chained_assignment = None

VALUE = 'values'
DATE = 'dates'
NAME = 'socialName'
CNPJ = 'cnpj'

#Get rentability of funds
def getFund(*cnpj: str, benchmark: List[str] = None, period: str = None,
            start: Union[str, datetime.date] = None, end: Union[str, datetime.date] = None) -> pd.DataFrame:
    """
    Return a pandas.DataFrame representing a time series with each observation
    indexed by its datetime.date and the following variables
        - Value

    Params:
        - cnpj: The fund's cnpj, you can get this info throught searchFund function
        - benchmark: Reference Index.
            - Accept Values: 'cdi', 'ibov', 'ipca'
        - period: Time Analysis, None return all data,
            - Accept Values: '1w', '2w','1m','2m','3m','6m','1y','2y','3y', '4y', '5y'.
        - start and end: Timeframe to search for funds in.
            - Accept Values: datetime.date or string with format 'dd/mm/yy'
        - fullData: Whether to return the time series of quote holders and patrimony

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
            data = __getData(nameList, benchmark= benchmark,start=start, end= end)
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
        valueList = fund[VALUE]
        dateList = as_date(fund[DATE])

        fundDict = {
            'Date': np.array(dateList),
            f'{fund["indicatorName"].upper()}': np.array(valueList)
        }

        final = pd.DataFrame(fundDict)
        final = final.dropna()
        final[fund["indicatorName"].upper()] = final[fund["indicatorName"].upper()] / 100

        final.set_index('Date', inplace=True)
        FinalList = pd.merge(FinalList, final, how='outer',on='Date')

    return FinalList.set_index('Date')


def getFunds(fundList: List[str], type_: str = None, period: str = None,
              start: Union[str, datetime.date] = None, end: Union[str, datetime.date] = None,
             simplifiedName: bool = False) -> pd.DataFrame:
    """
    Return a pandas.DataFrame representing a time series with each observation
    indexed by its datetime.date and the variation of each fund on the list.
    Params:
        - fundList: List with the strings of the fund names.
        - type_: Type of the investment, usually work as default.
            - Accept values: 'acao', 'fixa', 'cambial' or 'multi'.
        - period: Time Analysis, None return all data,
            - Accept Values: '1w', '2w','1m','2m','3m','6m','1y','2y','3y', '4y', '5y'.
        - start and end: You can also set the date,
            - Accept Values: datetime.date or string with format 'dd/mm/yy'
        - simplifiedName: Shorter names for plot and matrix visualization
    """

    listFinalDict = {}
    for fundName in fundList:
        name = __nameTreatment(fundName)
        if simplifiedName:
            fundName = fundName.upper()
            fundName = fundName.split('FUNDO',1)[0]

        if type_ is None:
            type_ = 'acao'

        if isinstance(end, str):
            end = datetime.datetime.strptime(end, '%d/%m/%y')
        if isinstance(start, str):
            start = datetime.datetime.strptime(start, '%d/%m/%y')

        end = __endTreatment(end, start, period)
        start = __startTreatment(start, end, period)

        # try to get the data 5 times before quitting
        for _ in range(5):
            try:
                data = __getData(name, type_)
                fund = data
                break
            except KeyError:
                time.sleep(1)
                continue
        else:
            raise ConnectionError("Could not load funds from page")

        value = []
        date = []

        #fund_observations = fund[OBS]
        #for observation in fund_observations:
        #    tempDate = datetime.datetime.strptime(observation[OBS_DATE], '%Y-%m-%d').date()
        #    if start <= tempDate <= end:
        #        date.append(tempDate)
        #        value.append(observation[OBS_VALUE])

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
        start = __getPeriodOptions(period, end)
    return int(start.timestamp()*1000)

  
def __endTreatment(end, start, period):    
    if end is None and period is None or end is None and period is not None and start is None:
        end = datetime.datetime.today()
    elif end is None and period is not None and start is not None:
        end = __getPeriodOptions(period, start, signal=False)

    return int(end.timestamp()*1000)


def __getData(cnpj, start, end, benchmark = None):
    data = rentability_info(cnpj, benchmarks= benchmark, startDate=start,endDate=end)
    return data

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

def searchFund(name:str, max_size : int = 20) -> list:
    """Return a list with funds with similar names, can control the size of the list with the max_size parameter, default 20"""
    name = __nameTreatment(name, search=True)
    fundData = search(name, max_size)
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
