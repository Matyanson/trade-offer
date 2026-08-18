from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

from alpaca.data.models import Quote
from strategy.model.budget import Budget
from strategy.model.pnl import Pnl

if TYPE_CHECKING:
    from manager.main_manager_interface import MainManagerInterface


class StrategyState(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    FINISHED = "finished" # ready to be cleared from the manager


# Basically an interface for a strategy.
class Strategy(ABC):
    def __init__(
        self,
        manager: MainManagerInterface,
        symbol: str,
        qty: float,
    ):
        self.manager = manager
        self.name = self.__class__.__name__
        self.id = f"{self.name}_{id(self)}"
        self.symbol = symbol

        self.budget = Budget(
            budget_qty=qty,
            reserved_qty=0.0,
            position_qty=0.0,
            filled_qty=0.0,
        )

        self.pnl = Pnl()

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
    

    