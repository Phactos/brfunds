from typing import Iterable, List

import requests
import datetime

funds_url = 'https://api.compareativos.com.br/fund'


def as_date(epoch_dates: List[int]) -> List[datetime.date]:
    """Transforms a list of dates in epoch milliseconds into an iterable of datetime.dates

    The api frequently returns dates as a list of dates in epoch milliseconds.
    """
    dates = [datetime.date.fromtimestamp(epoch_ms / 1000) for epoch_ms in epoch_dates]
    return dates


def search(name: str, rows: int = 20, offset: int = 0) -> List:
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


def cnpjInfo(*cnpjs: str):
    """Return the company info using the cnpjs id
    """
    cnpj_id = _join(cnpjs)

    response = requests.get(f'{funds_url}/{cnpj_id}/info')
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def rentabilityInfo(cnpjs: Iterable[str], benchmarks: List[str] = None,
                    startDate: int = '', endDate: int = '') -> List:
    """Return the fund info using the fund id
    """
    cnpj = _join(cnpjs)
    benchmark = '' if benchmarks is None else _join(benchmarks)
    startDate = str(startDate)
    endDate = str(endDate)

    response = requests.get(f'{funds_url}/{cnpj}/rentability/chart',
                            params={
                                'indicators': benchmark,
                                'startDate': startDate,
                                'endDate': endDate
                            })
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def volatilityInfo(cnpjs: Iterable[str], startDate: int = '', endDate: int = '') -> List:
    """Return the volatility info of the given fund
    """
    cnpj = _join(cnpjs)
    startDate = str(startDate)
    endDate = str(endDate)

    response = requests.get(f'{funds_url}/{cnpj}/volatility/chart', params={
                                'startDate': startDate,
                                'endDate': endDate})
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def shareholderInfo(cnjps: Iterable[str], startDate: int = '', endDate: int = '') -> List:
    """Return the shareholder info of the given fund
    """
    cnpj = _join(cnjps)
    startDate = str(startDate)
    endDate = str(endDate)

    response = requests.get(f'{funds_url}/{cnpj}/amountShareholders/chart', params={
                                'startDate': startDate,
                                'endDate': endDate})
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def networthInfo(cnpjs: Iterable[str], startDate: int = '', endDate: int = '') -> List:
    """Return the net worth info from the given fund
    """
    cnpj = _join(cnpjs)
    startDate = str(startDate)
    endDate = str(endDate)

    response = requests.get(f'{funds_url}/{cnpj}/netWorth/chart', params={
                                'startDate': startDate,
                                'endDate': endDate})
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def drawdownInfo(cnpjs: Iterable[str], startDate: int = '', endDate: int = ''):
    """Return the drawdown info from the given fund
    """
    cnpj = _join(cnpjs)
    startDate = str(startDate)
    endDate = str(endDate)

    response = requests.get(f'{funds_url}/{cnpj}/drawdown/chart', params={
                                'startDate': startDate,
                                'endDate': endDate})
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def _join(terms: Iterable[str]) -> str:
    result = ','.join(term for term in terms)
    return result


class RequestError(Exception):
    """Error containing status code of a non-200 request"""
