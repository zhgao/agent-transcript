"""x402 payment verification skeleton for the paid transcript endpoint.

Design, deliberately conservative:
- The free endpoint /agent/v1/transcript is untouched. Paid calls use
  /agent/v1/transcript-paid only, so a payment bug can never break free use.
- Without an X-PAYMENT header, the endpoint returns HTTP 402 with the
  payment requirements (network=base, asset=USDC, amount=0.01, payTo from
  X402_PAY_TO_ADDRESS). It does NOT return a transcript.
- With a header, it asks the x402 facilitator to verify, then settle.
  Facilitator URL defaults to https://x402.org/facilitator and can be
  overridden with X402_FACILITATOR_URL. No facilitator API key is used.
- MOCK MODE (local tests only): X402_VERIFY_MOCK=1 makes the header
  value "mock-valid" pass verification and settlement. This mode must
  NEVER be set on a public deployment; production runs without it, so a
  mock header is rejected by the real facilitator.

Real end-to-end proof still requires: a deployed public URL, a buyer
wallet holding Base USDC, and one real $0.01 payment verified + settled
through the facilitator. Until that run exists, do not claim live
charging, even though this code path exists.
"""

import base64
import json
import os

import requests

PRICE_USD = "0.01"
NETWORK = "base"
ASSET = "USDC"
# Circle USDC on Base (well-known contract; verify against Circle docs
# before a real paid launch if this value is ever changed).
USDC_BASE_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
FACILITATOR_TIMEOUT = 20


def payment_requirements(pay_to: str, amount: str = PRICE_USD) -> dict:
    return {
        "scheme": "exact",
        "network": NETWORK,
        "asset": USDC_BASE_CONTRACT,
        "currency": ASSET,
        "amount": amount,
        "payTo": pay_to,
        "maxTimeoutSeconds": 60,
    }


def standard_challenge(pay_to: str, amount: str = PRICE_USD,
                       resource: str = "") -> dict:
    """Standard x402 v1 challenge, as directories check it.

    Earlier builds returned only a custom ``payment_requirements`` body,
    which 402index and PayAPI both rejected as 'not an x402 challenge'
    (2026-10-28). The standard form uses an ``accepts`` array, network
    ``eip155:8453`` (Base), amount in USDC micro-units ($0.01 -> 10000),
    and ``extra.name`` = 'USD Coin'. The legacy body is kept alongside
    it for existing callers; the header below is what checkers read.
    """
    from decimal import Decimal
    micro = str(int(Decimal(amount) * 1_000_000))
    challenge = {
        "x402Version": 1,
        "error": "payment_required",
        "accepts": [{
            "scheme": "exact",
            "network": "eip155:8453",
            "maxAmountRequired": micro,
            "asset": USDC_BASE_CONTRACT,
            "payTo": pay_to,
            "maxTimeoutSeconds": 60,
            "extra": {"name": "USD Coin", "version": "2"},
        }],
    }
    if resource:
        challenge["resource"] = resource
    return challenge


def challenge_header(pay_to: str, amount: str = PRICE_USD,
                     resource: str = "") -> str:
    return base64.b64encode(
        json.dumps(standard_challenge(pay_to, amount, resource)).encode()
    ).decode()


def _decode_header(header: str):
    try:
        raw = base64.b64decode(header).decode("utf-8")
        return json.loads(raw)
    except Exception:
        return None


def _facilitator_call(path: str, payload, reqs):
    facilitator = os.getenv("X402_FACILITATOR_URL",
                            "https://x402.org/facilitator").rstrip("/")
    resp = requests.post(f"{facilitator}{path}",
                         json={"paymentPayload": payload,
                               "paymentRequirements": reqs},
                         timeout=FACILITATOR_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def verify_only(header: str, pay_to: str, amount: str = PRICE_USD):
    """Verify without settling, so a no-caption video never charges."""
    if os.getenv("X402_VERIFY_MOCK") == "1":
        if header.strip() == "mock-valid":
            return True, {"mock": True}
        return False, {"error": "invalid_mock_payment"}
    payload = _decode_header(header)
    if payload is None:
        return False, {"error": "bad_payment_header"}
    try:
        data = _facilitator_call("/verify", payload,
                                 payment_requirements(pay_to, amount))
    except requests.RequestException as e:
        return False, {"error": "facilitator_unreachable", "detail": str(e)}
    if not data.get("isValid"):
        return False, {"error": "payment_not_valid", "facilitator": data}
    return True, {}


def settle(header: str, pay_to: str, amount: str = PRICE_USD):
    if os.getenv("X402_VERIFY_MOCK") == "1":
        if header.strip() == "mock-valid":
            return True, {"mock": True, "tx": "mock-settlement"}
        return False, {"error": "invalid_mock_payment"}
    payload = _decode_header(header)
    if payload is None:
        return False, {"error": "bad_payment_header"}
    try:
        data = _facilitator_call("/settle", payload,
                                 payment_requirements(pay_to, amount))
    except requests.RequestException as e:
        return False, {"error": "facilitator_unreachable", "detail": str(e)}
    if not data.get("success"):
        return False, {"error": "settle_failed", "facilitator": data}
    return True, {"tx": data.get("transaction") or data.get("txHash"),
                  "network": NETWORK}


def verify_and_settle(header: str, pay_to: str, amount: str = PRICE_USD):
    """Return (ok, detail). ok=False means: do not serve the transcript."""
    ok, detail = verify_only(header, pay_to, amount)
    if not ok:
        return False, detail
    return settle(header, pay_to, amount)
