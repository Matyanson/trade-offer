from abc import ABC, abstractmethod
from uuid import UUID
from alpaca.trading.models import Order, OrderSide
from enum import Enum
from setup.trading import trading_client
from strategy.model.budget import Budget

class OrderState(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    FINISHED = "finished" # ready to be cleared from the manager


class OrderInterface(ABC):

    def __init__(self, symbol: str, qty: float, alpaca_order: Order):
        order_side = alpaca_order.side

        self.id = f"{self.__class__.__name__}_{id(self)}"
        self.symbol = symbol
        self.budget = Budget(
            budget_qty=qty if order_side == OrderSide.BUY else -qty,
            reserved_qty=qty if order_side == OrderSide.BUY else -qty,
            position_qty=0.0,
            filled_qty=0.0,
        )

        self.state = OrderState.PENDING
        self.alpaca_order = alpaca_order

    @abstractmethod
    def update(self) -> UUID:
        """
        Replace the order with a new one (updating the stop price, limit price, etc., all its attributes).
        Returns:
            UUID: The new order ID after the update.
        """
        pass

    def update_filled_qty(self, order: Order, position_qty: float):
        """
        Update the order's filled quantity based on the latest trade event.
        """
        order_side = order.side
        filled_qty = float(order.filled_qty)
        if order_side == OrderSide.SELL:
            filled_qty = -filled_qty

        # Update qty values
        self.budget.filled_qty = filled_qty
        self.budget.position_qty = position_qty
        self.budget.reserved_qty = self.budget.budget_qty - self.budget.filled_qty

        # Update the alpaca order reference
        self.alpaca_order = order

        # Update the order state based on filled quantity
        if abs(self.budget.filled_qty) >= abs(self.budget.budget_qty):
            self.state = OrderState.FINISHED
        else:
            self.state = OrderState.ACTIVE

        print(f"Order {self.id} updated state: {self.state}, budget_qty: {self.budget.budget_qty}, filled_qty: {self.budget.filled_qty}, position_qty: {self.budget.position_qty}, reserved_qty: {self.budget.reserved_qty}.")

    def cancel(self):
        """
        Cancel the order.
        """
        trading_client.cancel_order_by_id(self.alpaca_order.id)
        self.state = OrderState.FINISHED
