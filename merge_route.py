import json
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class Swap:
    pool: str
    token_in: int
    token_out: int
    exchange: str

    def __init__(self, pool, token_in, token_out, exchange, pool_extra):
        self.pool = pool
        self.token_in = token_in
        self.token_out = token_out
        self.exchange = exchange
        self.pool_extra = pool_extra


node_sum_amount_ins = {}
swap_amount_ins = {}
adj_lists = {}
token_ids = {}


def add_token(token):
    if token not in node_sum_amount_ins:
        node_sum_amount_ins[token] = 0
    if token not in adj_lists:
        adj_lists[token] = []


def add_swap(swap):
    if swap not in swap_amount_ins:
        swap_amount_ins[swap] = 0


with open("routeSummary.json", "r") as f:
    data = json.load(f)

for path in data["route"]:
    for raw_swap in path:
        add_token(raw_swap["tokenIn"])
        add_token(raw_swap["tokenOut"])

        adj_lists[raw_swap["tokenIn"]].append(raw_swap["tokenOut"])

        swap = Swap(
            raw_swap["pool"],
            raw_swap["tokenIn"],
            raw_swap["tokenOut"],
            raw_swap["exchange"],
            raw_swap["poolExtra"],
        )
        add_swap(swap)

        amount_in = int(raw_swap["swapAmount"])
        node_sum_amount_ins[raw_swap["tokenIn"]] += amount_in
        swap_amount_ins[swap] += amount_in

# topological sort
deg = {}
for node in adj_lists:
    deg[node] = 0

for node in adj_lists:
    for neighbor in adj_lists[node]:
        deg[neighbor] += 1

stack = []
for node in deg:
    if deg[node] == 0:
        stack.append(node)

while stack:
    node = stack.pop()
    token_ids[node] = len(token_ids)
    for neighbor in adj_lists[node]:
        deg[neighbor] -= 1
        if deg[neighbor] == 0:
            stack.append(neighbor)

# store token_ids with sum amount in as json, inside a json object with key "tokens"
routeMerged = {}
routeMerged["tokens"] = [
    {
        "token": token,
        "id": token_ids[token],
        "sum_amount_in": node_sum_amount_ins[token],
    }
    for token in token_ids
]

# append swaps as json, inside a json object with key "swaps"
routeMerged["swaps"] = [
    {
        "pool": swap.pool,
        "token_in_id": token_ids[swap.token_in],
        "token_out_id": token_ids[swap.token_out],
        "exchange": swap.exchange,
        "pool_extra": swap.pool_extra,
        "amount_in": swap_amount_ins[swap],
    }
    for swap in swap_amount_ins.keys()
]

# write result to file
with open("routeMerged.json", "w") as f:
    f.write(json.dumps(routeMerged, indent=2))

print(len(routeMerged["swaps"]))
