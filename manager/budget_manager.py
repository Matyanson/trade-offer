from manager.main_manager_interface import MainManagerInterface
from orders.model.order_interface import OrderState
from strategy.model.budget import Budget
from strategy.model.pnl import Pnl


class BudgetManager:
    def __init__(self, manager: MainManagerInterface):
        self.strategy_manager = manager.strategy
        self.order_manager = manager.order

    def _itterate_strategy_children(self, strategy_id: str):
        """
        Iterate over all children of the given strategy_id.
        """
        for child_id in self.strategy_manager.get_children(strategy_id):
            child_strategy = self.strategy_manager.get_strategy(child_id)
            if child_strategy is not None:
                yield child_strategy
    
    def _aggregate_order_budget(self, strategy_id: str):
        child_orders = self.order_manager.get_orders_for_strategy(strategy_id)

        aggregated = Budget.zero()
        for order in child_orders:
            aggregated = aggregated.add(order.budget)
        return aggregated

    def _aggregate_child_budget(self, strategy_id: str):
        aggregated = Budget.zero()
        for child_strategy in self._itterate_strategy_children(strategy_id):
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

    
    def _get_strategy_pnl(self, strategy_id: str):
        pnl = Pnl()
        # 1) get child order average_filled_price and qty
        child_orders = self.order_manager.get_orders_for_strategy(strategy_id)
        for order in child_orders:
            if order.filled_avg_price is None or order.state == OrderState.PENDING:
                continue  # Skip orders that haven't been filled yet
            # Opening order
            if order.budget.budget_qty > 0:
                pnl.total_cost_opened += order.budget.position_qty * order.filled_avg_price
                pnl.total_qty_opened += order.budget.position_qty
            # Closing order
            else:
                pnl.total_cost_closed += order.budget.position_qty * order.filled_avg_price
                pnl.total_qty_closed += order.budget.position_qty

        # 2) get child strategy pnl
        for child_strategy in self._itterate_strategy_children(strategy_id):
            pnl = pnl.add(child_strategy.pnl)
        return pnl

    
    def update_budget(self, strategy_id: str):
        for current_strategy in self._itterate_strategy_to_root(strategy_id):
            # 1) Update budget
            child_total = self._aggregate_child_budget(current_strategy.id)
            current_strategy.budget = child_total.copy()
            # 2) update pnl
            pnl = self._get_strategy_pnl(current_strategy)
            current_strategy.pnl = pnl
