import dataclasses
import requests
from dacite import from_dict
from typing import List, Optional, Tuple
import logging
import coloredlogs

from classes.WikifolioListItem import WikifolioListItem
from classes.Wikifolio import Wikifolio
from classes.Underlying import Underlying
from classes.OrderStatusResponse import OrderStatusResponse

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger, fmt='[%(asctime)s] %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

@dataclasses.dataclass
class WikifolioTradingAPI():
    clientApiKey: str
    userApiKey: str
    
    def __post_init__(self) -> None:
        headers = {
            'accept': 'application/json',
            'clientApiKey': self.clientApiKey,
            'userApiKey': self.userApiKey
        }
        logger.info('Getting session token')
        r = requests.post('https://trading-api.wikifolio.com/v1/sessions', headers=headers)
        r.raise_for_status()
        logger.debug(f'Session token: {r.json()["sessionToken"]}')
        self.sessionToken = r.json()['sessionToken']
        
    def list_wikifolios(self) -> List[WikifolioListItem]:
        """List wikifolios

        Returns:
            List[WikifolioListItem]: A list of wikifolios
        """
        headers = {
            'accept': 'application/json',
            'sessionToken': self.sessionToken
        }
        params = {
            'pageNumber': 1
        }
        list_wikifolios = []
        logger.info(f'Getting wikifolios, page {params["pageNumber"]}')
        r = requests.get('https://trading-api.wikifolio.com/v1/wikifolios', headers=headers, params=params)
        r.raise_for_status()
        logger.info(f'Found {r.json()["totalPages"]} pages of wikifolios')
        logger.info(f'Found {len(r.json()["results"])} wikifolios on page {params["pageNumber"]}')
        list_wikifolios += r.json()['results']
        while r.json()['pageNumber'] < r.json()['totalPages']:
            params['pageNumber'] += 1
            r = requests.get('https://trading-api.wikifolio.com/v1/wikifolios', headers=headers, params=params)
            r.raise_for_status()
            logger.info(f'Found {len(r.json()["results"])} wikifolios on page {params["pageNumber"]}')
            list_wikifolios += r.json()['results']
        
        return [from_dict(data_class=WikifolioListItem, data=wikifolio) for wikifolio in list_wikifolios]
    
    def get_wikifolio(self, wikifolioSymbol: str) -> Wikifolio:
        """Get a wikifolio

        Args:
            wikifolioSymbol (str): The wikifolio symbol

        Returns:
            Wikifolio: The wikifolio
        """
        headers = {
            'accept': 'application/json',
            'sessionToken': self.sessionToken
        }
        logger.info(f'Getting wikifolio {wikifolioSymbol}')
        r = requests.get(f'https://trading-api.wikifolio.com/v1/wikifolios/{wikifolioSymbol}', headers=headers)
        r.raise_for_status()
        
        return from_dict(data_class=Wikifolio, data=r.json())
    
    def list_wikifolio_underlyings(self, wikifolioSymbol: str) -> List[Underlying]:
        """List underlyings for a wikifolio

        Args:
            wikifolioSymbol (str): The wikifolio symbol

        Returns:
            List[Underlying]: A list of underlyings
        """
        headers = {
            'accept': 'application/json',
            'sessionToken': self.sessionToken
        }
        params = {
            'pageNumber': 1
        }
        list_underlyings = []
        logger.info(f'Getting underlyings for {wikifolioSymbol}, page {params["pageNumber"]}')
        r = requests.get(f'https://trading-api.wikifolio.com/v1/wikifolios/{wikifolioSymbol}/underlyings', headers=headers, params=params)
        r.raise_for_status()
        logger.info(f'Found {r.json()["totalPages"]} pages of underlyings for {wikifolioSymbol}')
        logger.info(f'Found {len(r.json()["results"])} underlyings for {wikifolioSymbol} on page {params["pageNumber"]}')
        list_underlyings += r.json()['results']
        while r.json()['pageNumber'] < r.json()['totalPages']:
            params['pageNumber'] += 1
            logger.info(f'Getting underlyings for {wikifolioSymbol}, page {params["pageNumber"]}')
            r = requests.get(f'https://trading-api.wikifolio.com/v1/wikifolios/{wikifolioSymbol}/underlyings', headers=headers, params=params)
            r.raise_for_status()
            logger.info(f'Found {len(r.json()["results"])} underlyings for {wikifolioSymbol} on page {params["pageNumber"]}')
            list_underlyings += r.json()['results']
        
        return [from_dict(data_class=Underlying, data=underlying) for underlying in list_underlyings]
    
    def list_wikifolio_orders(self, wikifolioSymbol: str, status: Optional[str] = None) -> List[OrderStatusResponse]:
        """List orders for a wikifolio

        Args:
            wikifolioSymbol (str): The wikifolio symbol
            status (Optional[str]): The order status to filter by. Defaults to None. Possible values: 'Inactive', 'Waiting', 'Active', 'Evaluating', 'Executing', 'RequestingExecutionInformation', 'PartiallyExecutedActive', 'Executed', 'PartiallyExecutedExecuted', 'Deleted', 'DeleteRequested', 'Updated', 'Obsolete', 'Error', 'Rejected', 'Undone', 'Abandoned'

        Returns:
            List[OrderStatusResponse]: A list of orders
        """
        headers = {
            'accept': 'application/json',
            'sessionToken': self.sessionToken
        }
        params = {
            'pageNumber': 1
        }
        if status:
            logger.debug(f'Filtering orders by status: {status}')
            if status in ['Inactive', 'Waiting', 'Active', 'Evaluating', 'Executing', 'RequestingExecutionInformation', 'PartiallyExecutedActive', 'Executed', 'PartiallyExecutedExecuted', 'Deleted', 'DeleteRequested', 'Updated', 'Obsolete', 'Error', 'Rejected', 'Undone', 'Abandoned']:
                params['status'] = status
            else:
                logger.error(f'Invalid order status: {status}, ignoring filter')
                del params['status']
        list_orders = []
        logger.info(f'Getting orders for {wikifolioSymbol}, page {params["pageNumber"]}')
        r = requests.get(f'https://trading-api.wikifolio.com/v1/wikifolios/{wikifolioSymbol}/orders', headers=headers, params=params)
        r.raise_for_status()
        logger.info(f'Found {r.json()["totalPages"]} pages of orders for {wikifolioSymbol}')
        logger.info(f'Found {len(r.json()["results"])} orders for {wikifolioSymbol} on page {params["pageNumber"]}')
        list_orders += r.json()['results']
        while r.json()['pageNumber'] < r.json()['totalPages']:
            params['pageNumber'] += 1
            logger.info(f'Getting orders for {wikifolioSymbol}, page {params["pageNumber"]}')
            r = requests.get(f'https://trading-api.wikifolio.com/v1/wikifolios/{wikifolioSymbol}/orders', headers=headers, params=params)
            r.raise_for_status()
            logger.info(f'Found {len(r.json()["results"])} orders for {wikifolioSymbol} on page {params["pageNumber"]}')
            list_orders += r.json()['results']
        
        return [from_dict(data_class=OrderStatusResponse, data=order) for order in list_orders]