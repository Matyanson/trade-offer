from manager.main_manager_interface import MainManagerInterface
from strategy.model.budget import Budget


class BudgetManager:
    def __init__(self, manager: MainManagerInterface):
        self.strategy_manager = manager.strategy
        self.order_manager = manager.order

    def _aggregate_order_budget(self, strategy_id: str):
        child_orders = self.order_manager.get_orders_for_strategy(strategy_id)

        aggregated = Budget.zero()
        for order in child_orders:
            aggregated = aggregated.add(order.budget)
        return aggregated

    def _aggregate_child_budget(self, strategy_id: str):
        child_strategy_ids = self.strategy_manager.get_children(strategy_id)
        aggregated = Budget.zero()

        for child_strategy_id in child_strategy_ids:
            child_strategy = self.strategy_manager.get_strategy(child_strategy_id)
            if child_strategy is None:
                continue
            aggregated = aggregated.add(child_strategy.budget)

        order_budget = self._aggregate_order_budget(strategy_id)
        aggregated = aggregated.add(order_budget)

        return aggregated

    def _itterate_strategy_to_root(self, strategy_id: str):
        """
        Iterate from the given strategy_id up to the root (the provided strategy is included).
        """
        current = strategy_id
        current_strategy = self.strategy_manager.get_strategy(current)
        while current_strategy is not None:
            yield current_strategy
            current = self.strategy_manager.get_parent(current)
            current_strategy = self.strategy_manager.get_strategy(current)

    
    def update_budget(self, strategy_id: str):
        for current_strategy in self._itterate_strategy_to_root(strategy_id):
            child_total = self._aggregate_child_budget(current_strategy.id)
            if child_total is not None:
                current_strategy.budget = child_total.copy()
