from manager.strategy_manager.manager_interface import StrategyManagerInterface
from strategy.model.strategy import Strategy, StrategyState
from alpaca.data.models import Quote


class StrategyManager(StrategyManagerInterface):

    def __init__(self):
        self.strategies: dict[str, Strategy] = {}       # id -> strategy
        self.parents: dict[str, str] = {}               # id -> parent_id
        self.children: dict[str, list[str]] = {}        # id -> id[]
        self.children["root"] = []

    def add(self, parent_id: str, strategy: Strategy):
        print(f"Adding strategy {strategy.id} under parent {parent_id}.")
        self.strategies[strategy.id] = strategy
        self.parents[strategy.id] = parent_id
        self.children.get(parent_id, []).append(strategy.id)
        self.children[strategy.id] = []

    def get_children(self, strategy_id: str):
        return list(self.children.get(strategy_id, []))

    def get_parent(self, strategy_id: str):
        return self.parents.get(strategy_id)

    def get_strategy(self, strategy_id: str):
        return self.strategies.get(strategy_id)

    # clean-up finished strategies
    def __remove(self, parent_id: str, strategy_id: str):
        print(f"Removing strategy {strategy_id} from manager.")
        self.strategies.pop(strategy_id, None)
        self.parents.pop(strategy_id, None)
        self.children.pop(strategy_id, None)
        self.children.get(parent_id, []).remove(strategy_id)

    # manual cancel of a strategy
    def cancel(self, strategy_id):
        # cancel the strategy
        strategy = self.strategies.get(strategy_id)
        if strategy is None:
            return

        strategy.state = StrategyState.FINISHED

        # TODO: strategy.cancel()
        pass

    # traverse bottom-up
    def itterate_bottom_up(self, parent_id: str, strategy_id: str):
        for child_id in self.children.get(strategy_id, []):
            yield from self.itterate_bottom_up(strategy_id, child_id)

        yield (parent_id, strategy_id)

    async def update_tree(self, quote: Quote):
        finished: list[tuple[str, str]] = [] # list of (parent_id, strategy_id) pairs to be removed

        for parent_id, strategy_id in self.itterate_bottom_up("root", "root"):
            strategy = self.strategies.get(strategy_id)
            if strategy is None:
                continue

            # 1) Update all strategies with the new quote
            await strategy.on_quote(quote)

            # 2) Clean-up finished strategies later
            if strategy.state == StrategyState.FINISHED:
                finished.append((parent_id, strategy_id))

        return finished

    async def on_quote(self, quote):
        print(f"Quote received: {quote.bid_price}-{quote.ask_price}, {quote.symbol} at {quote.timestamp}.")
        finished = await self.update_tree(quote)

        # Clean-up step
        for parent_id, strategy_id in finished:
            self.__remove(parent_id, strategy_id)