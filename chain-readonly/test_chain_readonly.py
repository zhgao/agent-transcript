"""Mock tests only — synthetic RPC responses, no network, no spend.

Run: python3 test_chain_readonly.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chain_readonly import (
    build_request,
    get_balance_eth,
    get_gas_price_gwei,
    get_latest_block,
    get_snapshot,
    measure_call,
    parse_hex_quantity,
    validate_address,
)

PASSED = 0


def check(name, cond):
    global PASSED
    assert cond, f"FAILED: {name}"
    PASSED += 1
    print(f"ok: {name}")


def fake_transport_factory(responses):
    """Return a transport that answers from a method->result map and
    records every method it was asked for."""
    seen = []

    def transport(request):
        seen.append(request["method"])
        result = responses[request["method"]]
        if isinstance(result, dict) and "error" in result:
            return result
        return {"jsonrpc": "2.0", "id": 1, "result": result}

    transport.seen = seen
    return transport


def expect_raises(name, exc, fn, *args):
    global PASSED
    try:
        fn(*args)
    except exc:
        PASSED += 1
        print(f"ok: {name}")
        return
    raise AssertionError(f"FAILED (no {exc.__name__}): {name}")


def main():
    # 1. Block number: 0x12345678 = 305,419,896
    t = fake_transport_factory({"eth_blockNumber": "0x12345678"})
    check("block number parses hex", get_latest_block(t) == 305419896)
    check("only eth_blockNumber called", t.seen == ["eth_blockNumber"])

    # 2. Gas: 1,000,000,000 wei = 1.0 gwei
    t = fake_transport_factory({"eth_gasPrice": "0x3b9aca00"})
    check("gas 1e9 wei = 1.0 gwei", get_gas_price_gwei(t) == 1.0)

    # 3. Balance: 1 ETH = 10^18 wei
    t = fake_transport_factory({"eth_getBalance": "0xde0b6b3a7640000"})
    addr = "0x0000000000000000000000000000000000000000"
    check("balance 1e18 wei = 1.0 ETH", get_balance_eth(t, addr) == 1.0)

    # 4. Snapshot combines all three, latency fields present
    t = fake_transport_factory(
        {
            "eth_blockNumber": "0x10",
            "eth_gasPrice": "0x3b9aca00",
            "eth_getBalance": "0x0",
        }
    )
    snap = get_snapshot(t, addr)
    check("snapshot block", snap["latest_block"] == 16)
    check("snapshot gas", snap["gas_price_gwei"] == 1.0)
    check("snapshot balance zero", snap["balance_eth"] == 0.0)
    check("snapshot latency keys", set(snap["latency_ms"]) == {"block", "gas", "balance"})

    # 5. Snapshot without address: balance None, no balance call
    t = fake_transport_factory(
        {"eth_blockNumber": "0x10", "eth_gasPrice": "0x3b9aca00"}
    )
    snap = get_snapshot(t)
    check("snapshot no-address balance None", snap["balance_eth"] is None)
    check("no balance call without address", "eth_getBalance" not in t.seen)

    # 6. Refusals and bad inputs raise, never return a wrong number
    expect_raises("write method refused", ValueError, build_request, "eth_sendTransaction")
    expect_raises("bad hex refused", ValueError, parse_hex_quantity, "123")
    expect_raises("bad hex digits refused", ValueError, parse_hex_quantity, "0xzz")
    expect_raises("short address refused", ValueError, validate_address, "0x1234")
    expect_raises("non-hex address refused", ValueError, validate_address, "0x" + "g" * 40)
    expect_raises(
        "balance with bad address refused",
        ValueError,
        get_balance_eth,
        fake_transport_factory({"eth_getBalance": "0x0"}),
        "not-an-address",
    )

    # 7. RPC error propagates (countable as a failure, not hidden)
    t = fake_transport_factory({"eth_blockNumber": {"error": {"code": -32000, "message": "x"}}})
    expect_raises("RPC error propagates", RuntimeError, get_latest_block, t)

    # 8. measure_call returns result + non-negative ms
    result, ms = measure_call(lambda: 42)
    check("measure_call result", result == 42)
    check("measure_call ms non-negative", ms >= 0)

    print(f"\nAll {PASSED} mock checks passed.")


if __name__ == "__main__":
    main()
