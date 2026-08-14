from manager.strategy_manager.manager_interface import StrategyManagerInterface
from manager.order_manager.manager_interface import OrderManagerInterface



class MainManagerInterface:

    strategy: StrategyManagerInterface
    order: OrderManagerInterface