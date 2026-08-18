from dataclasses import dataclass


@dataclass
class Budget:
    budget_qty: float
    _available_qty: float
    reserved_qty: float
    position_qty: float
    filled_qty: float

    def get_available_qty(self) -> float:
        return self.budget_qty - self.filled_qty - self.reserved_qty
    available_qty = property(get_available_qty)

    @classmethod
    def zero(cls) -> "Budget":
        return cls(0.0, 0.0, 0.0, 0.0, 0.0)

    def copy(self):
        return Budget(
            budget_qty=self.budget_qty,
            available_qty=self.available_qty,
            reserved_qty=self.reserved_qty,
            position_qty=self.position_qty,
            filled_qty=self.filled_qty,
        )

    def add(self, other: "Budget"):
        return Budget(
            budget_qty=self.budget_qty + other.budget_qty,
            available_qty=self.available_qty + other.available_qty,
            reserved_qty=self.reserved_qty + other.reserved_qty,
            position_qty=self.position_qty + other.position_qty,
            filled_qty=self.filled_qty + other.filled_qty,
        )

    def merge(self, *others: "Budget"):
        merged = self.copy()
        for other in others:
            merged = merged.add(other)
        return merged
