from abc import ABC, abstractmethod
from alpaca.data.models import Quote

from orders.model.order_interface import OrderInterface


class OrderManagerInterface(ABC):

    @abstractmethod
    def add(self, order_id: str, order):
        """
        Add an order to the manager.
        """
        pass

    def update(self, order: OrderInterface):
        """
        Update an order in the manager.
        """
        pass

    @abstractmethod
    def get_orders_for_strategy(self, strategy_id: str):
        """
        Return all orders belonging to the given strategy.
        """
        pass

    @abstractmethod
    async def on_trade_update(self, quote: Quote):
        """
        Update all orders with a new market event.
        """
        pass