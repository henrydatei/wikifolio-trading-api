import dataclasses
import requests
from dacite import from_dict
from typing import List, Optional, Tuple
import logging
import coloredlogs
import datetime

from classes.WikifolioListItem import WikifolioListItem
from classes.Wikifolio import Wikifolio
from classes.Underlying import Underlying
from classes.OrderStatusResponse import OrderStatusResponse

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger, fmt='[%(asctime)s] %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

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
        
    def logout(self) -> None:
        """Logout
        """
        headers = {
            'accept': 'application/json',
            'sessionToken': self.sessionToken
        }
        logger.info('Logging out')
        r = requests.delete('https://trading-api.wikifolio.com/v1/sessions', headers=headers)
        r.raise_for_status()
        logger.info('Logged out')
        
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
    
    def place_limit_order(self, wikifolioSymbol: str, underlying: str, amount: int, limitPrice: float, validUntilDate: datetime.date, side: str, stopPrice: Optional[float] = None) -> str:
        """Place a limit order

        Args:
            wikifolioSymbol (str): The wikifolio symbol
            underlying (str): The ISIN
            amount (int): The amount
            limitPrice (float): The limit price
            validUntilDate (datetime.date): The valid until date, this can't go too far into the future, not sure how far
            side (str): The side. Possible values: 'buy', 'sell'
            stopPrice (Optional[float]): The stop price. Defaults to None.

        Returns:
            str: The order ID
        """
        side = side.lower()
        if side not in ['buy', 'sell']:
            logger.error(f'Invalid side: {side}, must be "buy" or "sell"')
            return
        if side == 'sell' and stopPrice:
            logger.error('Stop price is only allowed for buy orders')
            return
        if stopPrice and side == 'buy':
            orderType = 'BuyStopLimit'
        elif side == 'buy':
            orderType = 'BuyLimit'
        elif side == 'sell':
            orderType = 'SellLimit'
            
        headers = {
            'accept': 'application/json',
            'sessionToken': self.sessionToken
        }
        data = {
            'wikifolioSymbol': wikifolioSymbol,
            'underlying': underlying,
            'amount': amount,
            'limitPrice': limitPrice,
            'validUntilDate': validUntilDate.strftime('%Y-%m-%d'),
            'orderType': orderType
        }
        if stopPrice:
            data['stopPrice'] = stopPrice
        
        logger.debug(f'Data for limit order: {data}')    
        logger.info(f'Placing limit order for {wikifolioSymbol}')
        r = requests.post(f'https://trading-api.wikifolio.com/v1/limitorders', headers=headers, json=data)
        logger.debug(f'Limit order response: {r.text}')
        r.raise_for_status()
        logger.info(f'Placed limit order for {wikifolioSymbol}')
        
        return r.json()['orderId']
    
    def update_limit_order(self, orderId: str, limitPrice: float, amount: int, validUntilDate: datetime.date, stopPrice: Optional[float] = None) -> None:
        """Update a limit order

        Args:
            orderId (str): The order ID
            limitPrice (float): The limit price
            amount (int): The amount
            validUntilDate (datetime.date): The valid until date, this can't go too far into the future, not sure how far
            stopPrice (Optional[float]): The stop price. Defaults to None.
        """
        headers = {
            'accept': 'application/json',
            'sessionToken': self.sessionToken
        }
        data = {
            'limitPrice': limitPrice,
            'amount': amount,
            'validUntilDate': validUntilDate.strftime('%Y-%m-%d')
        }
        if stopPrice:
            data['stopPrice'] = stopPrice
        
        logger.debug(f'Data for updating limit order: {data}')    
        logger.info(f'Updating limit order {orderId}')
        r = requests.put(f'https://trading-api.wikifolio.com/v1/limitorders/{orderId}', headers=headers, json=data)
        logger.debug(f'Update limit order response: {r.text}')
        r.raise_for_status()
        logger.info(f'Updated limit order {orderId}')
        
    def delete_limit_order(self, orderId: str) -> None:
        """Delete a limit order

        Args:
            orderId (str): The order ID
        """
        headers = {
            'accept': 'application/json',
            'sessionToken': self.sessionToken
        }
        logger.info(f'Deleting limit order {orderId}')
        r = requests.delete(f'https://trading-api.wikifolio.com/v1/limitorders/{orderId}', headers=headers)
        logger.debug(f'Delete limit order response: {r.text}')
        r.raise_for_status()
        logger.info(f'Deleted limit order {orderId}')
        
    def get_limit_order(self, orderId: str) -> OrderStatusResponse:
        """Get a limit order

        Args:
            orderId (str): The order ID

        Returns:
            OrderStatusResponse: The order
        """
        headers = {
            'accept': 'application/json',
            'sessionToken': self.sessionToken
        }
        logger.info(f'Getting limit order {orderId}')
        r = requests.get(f'https://trading-api.wikifolio.com/v1/limitorders/{orderId}', headers=headers)
        r.raise_for_status()
        
        return from_dict(data_class=OrderStatusResponse, data=r.json())
    
    def place_quote_order(self, wikifolioSymbol: str, underlying: str, amount: int, side: str) -> str:
        """Place a quote order

        Args:
            wikifolioSymbol (str): The wikifolio symbol
            underlying (str): The ISIN
            amount (int): The amount
            side (str): The side. Possible values: 'buy', 'sell'

        Returns:
            str: The order ID
        """
        
        # Step 1: get quote
        
        side = side.lower()
        if side not in ['buy', 'sell']:
            logger.error(f'Invalid side: {side}, must be "buy" or "sell"')
            return
        if side == 'buy':
            orderType = 'Buy'
        elif side == 'sell':
            orderType = 'Sell'
            
        headers = {
            'accept': 'application/json',
            'sessionToken': self.sessionToken
        }
        data = {
            'wikifolioSymbol': wikifolioSymbol,
            'underlying': underlying,
            'amount': amount,
            'orderType': orderType
        }
        
        logger.debug(f'Data for quote: {data}')    
        logger.info(f'Getting quote for {wikifolioSymbol}')
        r = requests.post(f'https://trading-api.wikifolio.com/v1/quotes', headers=headers, json=data)
        logger.debug(f'Quote response: {r.text}')
        r.raise_for_status()
        logger.info(f'Got quote for {wikifolioSymbol}')
        
        # Step 2: place order
        quoteId = r.json()['quoteId']
        data = {
            'quoteId': quoteId
        }
        logger.info(f'Placing quote order for {wikifolioSymbol}')
        r = requests.post(f'https://trading-api.wikifolio.com/v1/quoteorders', headers=headers, json=data)
        logger.debug(f'Quote order response: {r.text}')
        r.raise_for_status()
        logger.info(f'Placed quote order for {wikifolioSymbol}')
        
        return r.json()['orderId']
        