from abc import ABC, abstractmethod
from alpaca.data.models import Quote


class StrategyManagerInterface(ABC):

    @abstractmethod
    def add(self, parent_id: str, strategy):
        """
        Add a strategy to the manager.
        """
        pass


    @abstractmethod
    def cancel(self, strategy_id: str):
        """
        Manually cancel a strategy.
        """
        pass

    @abstractmethod
    def update_budget(self, strategy_id):
        """
        Update the budget of a strategy and its parents.
        """
    pass

    @abstractmethod
    async def on_quote(self, quote: Quote):
        """
        Update all strategies with a new market event.
        """
        pass