from dataclasses import dataclass


@dataclass
class Pnl:
    # Minimal P/L aggregates (strategy + child resources).
    total_cost_opened: float = 0.0
    total_qty_opened: float = 0.0
    total_cost_closed: float = 0.0
    total_qty_closed: float = 0.0

    def add(self, other: "Pnl"):
        return Pnl(
            total_cost_opened=self.total_cost_opened + other.total_cost_opened,
            total_qty_opened=self.total_qty_opened + other.total_qty_opened,
            total_cost_closed=self.total_cost_closed + other.total_cost_closed,
            total_qty_closed=self.total_qty_closed + other.total_qty_closed,
        )

    def get_realized_pnl(self) -> float:
        avg_open_price = 0.0
        if self.total_qty_opened > 0:
            avg_open_price = self.total_cost_opened / self.total_qty_opened

        realized_pnl = self.total_cost_closed - self.total_qty_closed * avg_open_price
        return realized_pnl

    def get_pnl(self, current_price: float) -> tuple[float, float, float]:
        position_qty = self.total_qty_opened - self.total_qty_closed

        realized_pnl = self.get_realized_pnl()

        total_pnl = (self.total_cost_closed + position_qty * current_price) - self.total_cost_opened

        unrealized_pnl = total_pnl - realized_pnl
        return realized_pnl, unrealized_pnl, total_pnl