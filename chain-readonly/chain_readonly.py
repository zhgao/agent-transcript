"""Chain read-only prototype — LOCAL ONLY, $0, no deployment, no spend.

Built 2026-10-27 as the next step named in the 2026-10-27 daily
earning report: "locally build a chain read-only interface prototype
and record latency / failure rate, then ask George whether to put
it online and at what price."

What it does (Base mainnet, read-only JSON-RPC only):
- latest block number: eth_blockNumber
- gas price in gwei: eth_gasPrice
- ETH balance of one address: eth_getBalance (address is public input;
  no wallet is created, no key is held, nothing is signed)

What it does NOT do:
- No deployment: nothing on https://agent-transcript.fly.dev changed.
- No spending, no account, no post, no price set.
- No write / send / sign call anywhere in this file.
- The transport is injected, so tests run on synthetic responses and
  never touch the network. A live public-RPC check is a separate,
  optional step and is NOT required for the mock tests to pass.

Hex helpers are strict: a malformed hex quantity or address raises
ValueError instead of silently returning a wrong number.
"""

import re
import time

_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")

# Methods this prototype is allowed to call. Anything else is refused
# by build_request(), so a write method can never slip through here.
READ_ONLY_METHODS = {"eth_blockNumber", "eth_gasPrice", "eth_getBalance"}


def build_request(method, params=None):
    """Build one JSON-RPC request dict, or raise for a non-read method."""
    if method not in READ_ONLY_METHODS:
        raise ValueError(f"refused non-read-only method: {method}")
    return {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}


def parse_hex_quantity(value):
    """Parse a '0x...' quantity into an int; raise on anything else."""
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"not a hex quantity: {value!r}")
    try:
        return int(value, 16)
    except ValueError:
        raise ValueError(f"not a hex quantity: {value!r}") from None


def validate_address(address):
    if not isinstance(address, str) or not _ADDRESS_RE.match(address):
        raise ValueError(f"not a valid 0x address: {address!r}")
    return address.lower()


def get_latest_block(transport):
    """transport(request_dict) -> response_dict; returns block number int."""
    resp = transport(build_request("eth_blockNumber"))
    if "error" in resp:
        raise RuntimeError(f"RPC error: {resp['error']}")
    return parse_hex_quantity(resp["result"])


def get_gas_price_gwei(transport):
    """Returns gas price in gwei (float, wei / 1e9)."""
    resp = transport(build_request("eth_gasPrice"))
    if "error" in resp:
        raise RuntimeError(f"RPC error: {resp['error']}")
    return parse_hex_quantity(resp["result"]) / 1_000_000_000


def get_balance_eth(transport, address):
    """Returns ETH balance of a public address as a float."""
    validate_address(address)
    resp = transport(build_request("eth_getBalance", [address, "latest"]))
    if "error" in resp:
        raise RuntimeError(f"RPC error: {resp['error']}")
    return parse_hex_quantity(resp["result"]) / 10**18


def measure_call(fn, *args):
    """Run fn(*args); return (result, elapsed_ms). Failure propagates,
    so a failure rate can be counted by the caller, not hidden here."""
    start = time.monotonic()
    result = fn(*args)
    return result, (time.monotonic() - start) * 1000.0


def get_snapshot(transport, address=None):
    """One small snapshot dict. balance_eth is None when no address
    is given; every field is measured separately so one failing call
    does not silently zero the others (it raises instead)."""
    block, block_ms = measure_call(get_latest_block, transport)
    gas, gas_ms = measure_call(get_gas_price_gwei, transport)
    snapshot = {
        "chain": "base",
        "latest_block": block,
        "gas_price_gwei": gas,
        "latency_ms": {"block": round(block_ms, 2), "gas": round(gas_ms, 2)},
    }
    if address is not None:
        balance, bal_ms = measure_call(get_balance_eth, transport, address)
        snapshot["balance_eth"] = balance
        snapshot["latency_ms"]["balance"] = round(bal_ms, 2)
    else:
        snapshot["balance_eth"] = None
    return snapshot
