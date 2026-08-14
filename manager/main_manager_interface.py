from __future__ import annotations

import manager.strategy_manager.manager_interface as strategy_manager_interface
import manager.order_manager.manager_interface as order_manager_interface
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manager.budget_manager import BudgetManager


class MainManagerInterface:

    strategy: strategy_manager_interface.StrategyManagerInterface
    order: order_manager_interface.OrderManagerInterface
    budget: BudgetManager