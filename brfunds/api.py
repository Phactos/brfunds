from typing import List

import requests

api_url = 'https://api.compareativos.com.br/assets/'


def search(name: str, rows: int = 1, offset: int = 0):
    """Return the search data for funds found with the given name
    """
    response = requests.get(f'{api_url}/list',
                            params={
                                'search': name,
                                'rows': rows,
                                'offset': offset
                            })
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def cnpj_info(cnpj_id: int):
    """Return the company info using the cnpj id
    """
    response = requests.get(f'{api_url}/{cnpj_id}/info')
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


def fund_info(fund_id: str, indicators: List[str] = None):
    """Return the fund info using the fund id
    """
    indicator_arg = '' if indicators is None else ','.join(indicators)

    response = requests.get(f'{api_url}/{fund_id}/rentability/chart',
                            params={
                                'indicators': indicator_arg
                            })
    if response.ok:
        return response.json()
    else:
        raise RequestError(response.status_code)


class RequestError(Exception):
    """Error containing status code of a non-200 request"""
