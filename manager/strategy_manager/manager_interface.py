from __future__ import annotations

from abc import ABC, abstractmethod

from alpaca.data.models import Quote
from strategy.model.strategy import Strategy


class StrategyManagerInterface(ABC):

    @abstractmethod
    def add(self, parent_id: str, strategy):
        """
        Add a strategy to the manager.
        """
        pass

    @abstractmethod
    def get_children(self, strategy_id: str) -> list[str]:
        """
        Return the direct child strategy ids of a strategy.
        """
        pass

    @abstractmethod
    def get_parent(self, strategy_id: str) -> (str | None):
        """
        Return the parent strategy id for a strategy.
        """
        pass

    @abstractmethod
    def get_strategy(self, strategy_id: str) -> Strategy | None:
        """
        Return a strategy instance by id.
        """
        pass

    @abstractmethod
    def cancel(self, strategy_id: str):
        """
        Manually cancel a strategy.
        """
        pass

    @abstractmethod
    async def on_quote(self, quote: Quote):
        """
        Update all strategies with a new market event.
        """
        pass