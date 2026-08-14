from manager.main_manager_interface import MainManagerInterface


class BudgetManager:
    def __init__(self, manager: MainManagerInterface):
        self.strategy_manager = manager.strategy
        self.order_manager = manager.order

    def _aggregate_order_budget(self, strategy_id: str):
        total = self.order_manager.get_orders_for_strategy(strategy_id)
        if not total:
            return None

        aggregated = None
        for order in total:
            order_budget = order.budget
            aggregated = order_budget if aggregated is None else aggregated.add(order_budget)
        return aggregated

    def _aggregate_child_budget(self, strategy_id: str):
        child_strategy_ids = self.strategy_manager.get_children(strategy_id)
        aggregated = None

        for child_strategy_id in child_strategy_ids:
            child_strategy = self.strategy_manager.get_strategy(child_strategy_id)
            if child_strategy is None:
                continue
            child_budget = child_strategy.budget
            aggregated = child_budget if aggregated is None else aggregated.add(child_budget)

        order_budget = self._aggregate_order_budget(strategy_id)
        if order_budget is not None:
            aggregated = order_budget if aggregated is None else aggregated.add(order_budget)

        return aggregated

    def update_budget(self, strategy_id: str):
        strategy = self.strategy_manager.get_strategy(strategy_id)
        if strategy is None:
            return

        child_total = self._aggregate_child_budget(strategy_id)
        if child_total is not None:
            strategy.budget = child_total.copy()
            strategy.budget.available_qty = strategy.budget.budget_qty - strategy.budget.filled_qty - strategy.budget.reserved_qty

        current = self.strategy_manager.get_parent(strategy_id)
        while current is not None:
            parent_strategy = self.strategy_manager.get_strategy(current)
            if parent_strategy is None:
                break

            parent_total = self._aggregate_child_budget(current)
            if parent_total is not None:
                parent_strategy.budget = parent_total.copy()
                parent_strategy.budget.available_qty = parent_strategy.budget.budget_qty - parent_strategy.budget.filled_qty - parent_strategy.budget.reserved_qty
            current = self.strategy_manager.get_parent(current)
