import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
import datetime
import time

def getFund(fundName, benchmark = None,type = None, period = None, start = None, end = None, fullData = False):
    """fundName: String with the fund name.
    type: Type of the investment, usually work as default. Accept values: 'acao', 'fixa', 'cambial' or 'multi'. 
    benchmark: Reference Index. Accept Values: 'cdi', 'ibov', 'ipca'
    period: Time Analysis, None return all data, Accept Values: '1w', '2w','1m','2m','3m','6m','1y','2y','3y', '4y', '5y'.
    start and end: You can also set the date, Accept Values: datetime.date or string with format 'dd/mm/yy' 
    fullData: Return time series of quote holders and patrimony"""
    name = __nameTreatment(fundName)

    if (type == None):
        type = 'acao'
    if (isinstance(end, str)):
        end = datetime.datetime.strptime(end,'%d/%m/%y').date()
    if (isinstance(start,str)):
        start = datetime.datetime.strptime(start,'%d/%m/%y').date()
    
    end = __endTreatment(end, start, period)
    
    start = __startTreatment(start, end, period)
    
    for i in range(5):
        try:
            data = __getData(name,type)
            fund = data['props']['pageProps']['fund']
            break
        except Exception:
            time.sleep(1)
            continue
    else:
        raise Exception
    value = []
    date = []
    if (fullData == True):
        netAssets = []
        shareholders = []
    for i in range(len(fund['r'])):        
        tempDate = datetime.datetime.strptime(fund['r'][i]['d'],'%Y-%m-%d').date()
        if (start <= tempDate <= end ):
            date.append(tempDate)
            value.append(fund['r'][i]['q'])
            if (fullData == True):
                netAssets.append(fund['r'][i]['nw'])
                shareholders.append(fund['r'][i]['qh'])
    final = {}
    final['Date'] = np.array(date)
    final['Value'] = np.array(value)
    if (fullData == True):
        final['Net Assets'] = np.array(netAssets)
        final['# of Shareholders'] = np.array(shareholders) 
    final = pd.DataFrame(final)
    final["Daily Variation"] = final['Value'].pct_change()
    final['Daily Variation'][0] = 0
    final['Total Variation'] = final['Value']/final['Value'][0] - 1
    final.set_index('Date', inplace=True)
    if (benchmark != None):
        bench = __getBenchmark(benchmark, final.index[0], final.index[-1], data)
        final = pd.merge(final,bench,'inner',left_index=True, right_index=True)
        final['Total Variation'] = final['Value']/final['Value'][0] - 1
    return final

def getFunds(fundList, type = None, period = None, start = None, end = None, simplifiedName = False):
    """fundList: List with the strings of the fund names.
    type: Type of the investment, usually work as default. Accept values: 'acao', 'fixa', 'cambial' or 'multi'. 
    period: Time Analysis, None return all data, Accept Values: '1w', '2w','1m','2m','3m','6m','1y','2y','3y', '4y', '5y'.
    start and end: You can also set the date, Accept Values: datetime.date or string with format 'dd/mm/yy' 
    fullData: Return time series of quote holders and patrimony"""

    listFinal = {}
    for fundName in fundList:
        name = __nameTreatment(fundName)
        if simplifiedName:
            fundName = fundName.upper()
            fundName = fundName.split('FUNDO',1)[0]

        if (type == None):
            type = 'acao'
        
        if (isinstance(end,str)):
            end = datetime.datetime.strptime(end,'%d/%m/%y').date()
        if (isinstance(start,str)):
            start = datetime.datetime.strptime(start,'%d/%m/%y').date()
        
        end = __endTreatment(end, start, period)
        start = __startTreatment(start, end, period)           
        
        for i in range(5):
            try:
                data = __getData(name,type)
                fund = data['props']['pageProps']['fund']
                break
            except Exception:
                time.sleep(1)
                continue
        else:
            raise Exception
        value = []
        date = []
        for i in range((len(fund['r']))):        
            tempDate = datetime.datetime.strptime(fund['r'][i]['d'],'%Y-%m-%d').date()
            if (start <= tempDate <= end ):
               date.append(tempDate)
               value.append(fund['r'][i]['q'])
        final = {}
        final['Date'] = np.array(date)
        final['Value'] = np.array(value)
        final = pd.DataFrame(final)
        final.set_index('Date', inplace=True)
        if (len(final['Value']) > 1):
            listFinal[fundName] = final['Value']/final['Value'][0] - 1
    listFinal = pd.DataFrame(listFinal)
    return listFinal

def __nameTreatment(name):
    name = name.lower()
    name = name.replace(" ","-").replace('ã','a').replace('á','a').replace('â','a').replace(
                        'é','e').replace('ê','e').replace('í','i').replace('õ','o').replace(
                        'ó','o').replace('ô','o').replace('ú','u').replace('ç','c')
    return name

def __startTreatment(start, end, period):
    if (start == None and period == None):
        start = datetime.date(1,1,1)
    elif (start == None and period != None):
        start = __getPeriodOptions(period, end)
    return start

def __endTreatment(end, start, period):    
    if (end == None and period == None or end == None and period != None and start == None):
        end = datetime.date.today()
    elif(end == None and period != None and start != None):
        end = __getPeriodOptions(period, start, signal= False)
    
    return end

def __getData(name,type):
    type = __nameTreatment(type)
    typeOptions = {'acao' : 'fundos-de-acoes', 
                   'fixa' : 'fundos-de-renda-fixa',
                   'cambial' : 'fundos-cambial',
                   'multi' : 'fundos-multimercado'}
    url = f"https://www.comparadordefundos.com.br/fundos-de-investimento/{typeOptions[type]}/{name}?period=otimo"
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find(id="__NEXT_DATA__").contents
    data = [json.loads(script) for script in table][0]
    return data


def __getBenchmark(benchmark, start, end, data):
    benchmark = benchmark.lower()
    benchmarkOptions = {'cdi' : 'cdi', 'ibov' : 'ibovespa', 'ipca' : 'ipca', 'ibovespa' : 'ibovespa'}
    benchmarkData = data["props"]["initialReduxState"][benchmarkOptions[benchmark]]
    bench = []
    benchDate = []
    for i in range(len(benchmarkData['r'])):
        tempDate = datetime.datetime.strptime(benchmarkData['r'][i]['d'],'%Y-%m-%d').date()
        if (start <= tempDate <= end):
           bench.append(benchmarkData['r'][i]['q'])
           benchDate.append(tempDate)
    
    bench = np.array(bench)
    benchDate = np.array(benchDate)
    bench = bench/bench[0] - 1
    benchmarkData = {}
    benchmarkData[f'{benchmarkOptions[benchmark]}'.upper()] = bench
    benchmarkData['Date'] = benchDate
    bench = pd.DataFrame(benchmarkData)
    bench.set_index('Date', inplace=True)
    return bench

def __getPeriodOptions(period, reference, signal = True):
    if(signal == True):
        signal = 1
    else:
        signal = -1
    periodOptions = {   '1w' : reference - signal*datetime.timedelta(days=7),
                        '2w' : reference - signal*datetime.timedelta(days=14),
                        '1m' : reference - signal*datetime.timedelta(days=30),
                        '2m' : reference - signal*datetime.timedelta(days=60),
                        '3m' : reference - signal*datetime.timedelta(days=91),
                        '6m' : reference - signal*datetime.timedelta(days=182),
                        '1y' : reference - signal*datetime.timedelta(days=365),
                        '2y' : reference - signal*datetime.timedelta(days=730),
                        '3y' : reference - signal*datetime.timedelta(days=1095),
                        '4y' : reference - signal*datetime.timedelta(days=1460),
                        '5y' : reference - signal*datetime.timedelta(days=1825)}
    return periodOptions[period]