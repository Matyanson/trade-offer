from abc import ABC, abstractmethod
from alpaca.data.models import Quote


class OrderManagerInterface(ABC):
    
    @abstractmethod
    def add(self, order_id: str, order):
        """
        Add an order to the manager.
        """
        pass


    @abstractmethod
    async def on_trade_update(self, quote: Quote):
        """
        Update all orders with a new market event.
        """
        pass