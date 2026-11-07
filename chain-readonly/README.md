# Chain read-only prototype — LOCAL ONLY

Built 2026-10-27 (Beijing morning) as the next step named in the
2026-10-27 daily earning report: "locally build a chain read-only
interface prototype and record latency / failure rate, then ask
George whether to put it online and at what price."

## What it is
`chain_readonly.py` — Base mainnet, read-only JSON-RPC only:
- `get_latest_block` → eth_blockNumber
- `get_gas_price_gwei` → eth_gasPrice
- `get_balance_eth(address)` → eth_getBalance (public address input only)
- `get_snapshot` → block + gas (+ balance when an address is given),
  each call timed in ms via `measure_call`
- `build_request` refuses any method outside the three read-only
  methods, so no write / send / sign call can pass through it.

No wallet is created, no key is held, nothing is signed.

## What it is NOT
- Not deployed. Nothing on https://agent-transcript.fly.dev changed.
- Not priced. No price for this endpoint has been decided by George.
- Not a claim of agent demand: the 2026-10-27 report itself said the
  x402 Bazaar chain-data signal is only an upper-bound reference
  (paying parties may be tests / crawlers).
- Not live-tested: see below.

## Tests
`python3 test_chain_readonly.py` — 19/19 mock checks green
(2026-10-27, synthetic RPC responses only; no network).

## Honest limit: live latency NOT measured
A live call to the public Base RPC (https://mainnet.base.org,
eth_blockNumber) from this background research run was denied by
the run's own preparation policy — not by Base, and not a Base
outage. So real latency / failure rate against the live chain is
still unmeasured. That check needs a normal (non-background) run
before anyone quotes a live latency number or puts this online.

## Next decisions, all George's, none taken here
1. Whether to put this online at all, and at what price.
2. Whether it or the already-local paid YouTube search ($0.005)
   goes live first — paid search still needs a fresh Fly token,
   and George's standing decision is "wait for a real buyer,
   do not recharge."
