from typing import List

import requests
import datetime

funds_url = 'https://api.compareativos.com.br/fund'


def as_date(epoch_dates: List[int]) -> List[datetime.date]:
    """Transforms a list of dates in epoch milliseconds into an iterable of datetime.dates

    The api frequently returns dates as a list of dates in epoch milliseconds.
    """
    dates = [datetime.date.fromtimestamp(epoch_ms / 1000) for epoch_ms in epoch_dates]
    return dates


def search(name: str, rows: int = 20, offset: int = 0):
    """Return the search data for funds found with the given name
    """
    response = requests.get(f'{funds_url}/list',
                            params={
                                'search': name,
                                'rows': rows,
                                'offset': offset
                            })
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def cnpj_info(*cnpj_ids: str):
    """Return the company info using the cnpj id
    """
    cnpj_id = _join(cnpj_ids)

    response = requests.get(f'{funds_url}/{cnpj_id}/info')
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def rentability_info(fund_ids: str, benchmarks: List[str] = None, startDate = '', endDate = ''):
    """Return the fund info using the fund id
    """
    fund_id = _join(fund_ids)
    indicator_arg = '' if benchmarks is None else ','.join(benchmarks)
    startDate = str(startDate)
    endDate = str(endDate)

    
    response = requests.get(f'{funds_url}/{fund_id}/rentability/chart',
                            params={
                                'indicators': indicator_arg,
                                'startDate' : startDate,
                                'endDate' : endDate
                            })
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def volatility_info(fund_ids: str, startDate = '', endDate = ''):
    """Return the volatility info of the given fund
    """
    fund_id = _join(fund_ids)
    startDate = str(startDate)
    endDate = str(endDate)

    response = requests.get(f'{funds_url}/{fund_id}/volatility/chart',params={
                                'startDate' : startDate,
                                'endDate' : endDate})
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def shareholder_info(*cpnj_ids: str):
    """Return the shareholder info of the given fund
    """
    cpnj_id = _join(cpnj_ids)

    response = requests.get(f'{funds_url}/{cpnj_id}/amountShareholders/chart')
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def networth_info(*cpnj_ids: str):
    """Return the net worth info from the given fund
    """
    cpnj_id = _join(cpnj_ids)

    response = requests.get(f'{funds_url}/{cpnj_id}/netWorth/chart')
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def _join(terms):
    result = ','.join(term for term in terms)
    return result



class RequestError(Exception):
    """Error containing status code of a non-200 request"""
