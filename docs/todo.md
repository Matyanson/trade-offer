## handle budget
1) each strategy will have a budget:
- budget            (total budget allocated to the strategy, can be reallocated)
- available_budget  (budget not used = budget - reserved_budget - invested_budget)
- reserved_budget   (pending orders)
- invested_budget   (filled positions)

TODO: let the manager handle budget calculations

2) reallocate budget

## handle partial fills (and hidden fees)

budget: .200
set limit buy for: .200
- reserved_budget: .200

buy order fills partially: .100
- reserved_budget: .100
- invested_budget: .100

set stop sell order for: .100
can I do that? it says order filled for .100, but maybe I have less than .100 stock bought because of fees!!!
TODO: I need to track the actual filled quantity
the buy order says filled for .100, the position says .099 though...

ok so this is how we can track the difference between the reported filled quantity and the actual filled quantity:
all orders share a single position across one asset (BTC/USD).
We develop a position manager:
it tracks the last position quantity. when a new change happens (order gets filled, partially or fully, or canceled), we save the difference between the last and current postion. Then we go through a list of all orders that happened in between (sells and buys). Then we get the total reported buy quantity, total reported sell quantity and the total reported difference.
fees = total_reported_difference - actual_difference (I think)
then we split the fees proportionally to all orders that happened in between (weighted by their quantity). Then we update the actual filled quantity for each order.


## manually cancel strategy


## dynamic pending order budget reallocation
We cannot place new orders if all budget is reserved on pending orders. We can free some of the reserved budget to place new orders.
However, we risk missing a fill on the pending orders. We need to somehow manage the possibility if that happens.

there are two ways to reallocate the budget:
1) Manager side:

This is preemptively, conservativelly done before the extra budget is needed.
Say we set:
- shared_reserved_budget # all strategies and pending orders share this budget

We dynamically reallocate the budget to positions that are more likely to be filled.
wait, but this means, we cannot have a single pending order that is larger than the shared_reserved_budget.
TODO: think about this more.

We can set the shared_reserved_budget to be the larest pending order... but we must make sure the pending orders are not related.
What if two pending orders can become filled at the same time? Then we need to have a shared_reserved_budget that is larger than the sum of those two pending orders.

1.1) the manager modifies or cancels the pending orders directly.
1.2) the manager directly modifies the strategy's reserved budget.
1.3) the manager orders the strategy to modify or free some of its reserved budget.


2) Strategy side: