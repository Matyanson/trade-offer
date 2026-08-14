from types import CoroutineType
from typing import Any

from alpaca.trading.models import TradeUpdate
from manager.main_manager_interface import MainManagerInterface
from orders.model.order_interface import OrderInterface
from manager.order_manager.manager_interface import OrderManagerInterface


class OrderManager(OrderManagerInterface):

    def __init__(self, manager: MainManagerInterface):
        self.manager = manager
        self.last_position_qty: float = 0.0
        # alpaca order id -> (parent strategy id, order)
        self.orders: dict[str, tuple[str, OrderInterface]] = {}
        print("OrderManager initialized.")

    def add(self, parent_strategy_id: str, order: OrderInterface):
        """
        Add a new order to the manager.
        """
        self.orders[str(order.alpaca_order.id)] = (parent_strategy_id, order)
        print(f"Order {order.alpaca_order.id} / {order.id} added to the manager under strategy {parent_strategy_id}.")

    def update(self, alpaca_order_id: str):
        """
        Update the order in the manager with the latest data from Alpaca.
        """
        if alpaca_order_id not in self.orders:
            print(f"Order {alpaca_order_id} not found in the manager!!!")
            return

        parent_strategy_id, order = self.orders[alpaca_order_id]
        new_alpaca_order_id = order.update()
        self.orders[str(new_alpaca_order_id)] = (parent_strategy_id, order)
        del self.orders[alpaca_order_id]
        print(f"Order {new_alpaca_order_id} updated.")

    def _get_order_position_qty(self, total_position_qty: float) -> float:
        """
        Calculate the position quantity for the given order.
        """
        # calculate position_qty for the order
        return total_position_qty - self.last_position_qty

    async def _on_fill(self, data: TradeUpdate):
        """
        Handle the fill or partial_fill event for an order.
        """
        alpaca_order_id = str(data.order.id)
        total_position_qty = float(data.position_qty)
        

        if alpaca_order_id not in self.orders:
            print(f"Order {alpaca_order_id} not found in the manager!!!")
            if data.position_qty:
                # update last_position_qty
                self.last_position_qty = total_position_qty
            return

        parent_strategy_id, order = self.orders[alpaca_order_id]
        
        # calculate position_qty of the order
        # positive = buy, negative = sell
        order_position_qty = self._get_order_position_qty(total_position_qty)
        
        # update last_position_qty
        self.last_position_qty = total_position_qty

        # update the order and strategy budget
        order.update_filled_qty(data.order, order_position_qty)
        print(f"Order {order.id} position quantity updated to {order_position_qty}.")
        self.manager.strategy.update_budget(parent_strategy_id)


    async def on_trade_update(self, data: TradeUpdate):
        """
        Update new filled quantity for the order
        """
        print(f"Trade update received for order {data.order.id}: {data.event}")
        match data.event:
            case "fill" | "partial_fill":
                await self._on_fill(data)
            case _:
                pass
