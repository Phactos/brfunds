from typing import Iterator, List

import requests
import datetime


assets_url = 'https://api.compareativos.com.br/assets'
funds_url = 'https://api.compareativos.com.br/fund'


def as_date(epoch_dates: List[int]) -> Iterator[datetime.date]:
    """Transforms a list of dates in epoch milliseconds into an iterable of datetime.dates

    The api frequently returns dates as a list of dates in epoch milliseconds.
    """
    return (datetime.date.fromtimestamp(epoch_ms / 1000) for epoch_ms in epoch_dates)


def search(name: str, rows: int = 1, offset: int = 0):
    """Return the search data for funds found with the given name
    """
    response = requests.get(f'{assets_url}/list',
                            params={
                                'search': name,
                                'rows': rows,
                                'offset': offset
                            })
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def cnpj_info(*cnpj_ids: int):
    """Return the company info using the cnpj id
    """
    cnpj_id = _join(cnpj_ids)

    response = requests.get(f'{assets_url}/{cnpj_id}/info')
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def benchmark_info(*fund_ids: str, benchmarks: List[str] = None):
    """Return the fund info using the fund id
    """
    fund_id = _join(fund_ids)
    indicator_arg = '' if benchmarks is None else ','.join(benchmarks)

    response = requests.get(f'{assets_url}/{fund_id}/rentability/chart',
                            params={
                                'indicators': indicator_arg
                            })
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def volatility_info(*fund_ids: str):
    """Return the volatility info of the given fund
    """
    fund_id = _join(fund_ids)

    response = requests.get(f'{assets_url}/{fund_id}/volatility/chart')
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def shareholder_info(*cpnj_ids: int):
    """Return the shareholder info of the given fund
    """
    cpnj_id = _join(cpnj_ids)

    response = requests.get(f'{funds_url}/{cpnj_id}/amountShareholders/chart')
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def networth_info(*cpnj_ids: int):
    """Return the net worth info from the given fund
    """
    cpnj_id = _join(cpnj_ids)

    response = requests.get(f'{funds_url}/{cpnj_id}/netWorth/chart')
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def _join(terms):
    return ','.join(str(term) for term in terms)


class RequestError(Exception):
    """Error containing status code of a non-200 request"""
