from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

from alpaca.data.models import Quote
from manager.manager_interface import StrategyManagerInterface


class StrategyState(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    FINISHED = "finished" # ready to be cleared from the manager


# Basically an interface for a strategy.
class Strategy(ABC):
    def __init__(
        self,
        manager: StrategyManagerInterface,
        symbol: str,
        qty: float,
    ):
        self.manager = manager
        self.name = self.__class__.__name__
        self.symbol = symbol
        self.qty = qty

        self.id = f"{self.name}_{id(self)}"
        self.state = StrategyState.PENDING
        self.on_init()

    @abstractmethod
    def on_init(self):
        """
        Called when the strategy is added to the manager.
        """
        pass

    @abstractmethod
    async def on_quote(self, quote: Quote):
        """
        Called for every incoming quote.
        """
        pass

    

    