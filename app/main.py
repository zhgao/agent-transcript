"""Agent transcript API (0-cost exploration build).

One purpose: a machine can call this with a YouTube URL and get a
structured transcript back, no account, no signup. Free caption tiers
only. Payment spec: /x402.json reads the pay-to address ONLY from the
X402_PAY_TO_ADDRESS environment variable. The address is never
hard-coded in this repo and never written to memory. Without that
variable the endpoint returns a draft (payment_enabled=false).
"""

import os
import re

from fastapi import FastAPI, Header, Query
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

from .free_transcript import (
    NoCaptionsError,
    get_transcript_free,
    is_youtube_url,
)
from .youtube_search import search_youtube
from .x402_verify import (challenge_header, payment_requirements,
                          settle, standard_challenge, verify_only)

# openapi_url is disabled so our hand-built OpenAPI 3.1 document below
# is the one served at /openapi.json (FastAPI's auto-generated spec
# would otherwise shadow it). The pay-to address is injected at
# request time from X402_PAY_TO_ADDRESS only, never hard-coded here.
app = FastAPI(title="agent-transcript", version="0.1.0",
              openapi_url=None, docs_url=None, redoc_url=None)


def _payment_required(pay_to: str, amount: str, resource: str):
    """402 with both the standard x402 challenge header and the legacy
    body, so directory checkers and existing callers both read it."""
    challenge = standard_challenge(pay_to, amount, resource)
    content = dict(challenge)
    content["payment_requirements"] = payment_requirements(pay_to, amount)
    return JSONResponse(
        status_code=402, content=content,
        headers={"PAYMENT-REQUIRED": challenge_header(
            pay_to, amount, resource)},
    )


@app.get("/health")
def health():
    return {"status": "ok", "paid_transcription": False,
            "cost_per_call_usd": 0, "paid_fallback_exists": False}


@app.get("/agent/v1/transcript")
def transcript(url: str = Query(...), lang: str = Query("auto")):
    if not is_youtube_url(url):
        return JSONResponse(
            status_code=400,
            content={"error": "not_youtube",
                     "detail": "only YouTube URLs are supported in this free tier"},
        )
    try:
        result = get_transcript_free(url, lang=lang)
    except NoCaptionsError as e:
        return JSONResponse(
            status_code=404,
            content={"error": "no_captions",
                     "detail": str(e),
                     "paid_fallback": False,
                     "paid_fallback_attempted": False},
        )
    except ValueError as e:
        return JSONResponse(status_code=400,
                            content={"error": "bad_url", "detail": str(e)})
    return result


@app.get("/agent/v1/youtube-search")
def youtube_search(q: str = Query(""), max_results: int = Query(5)):
    """Free YouTube search for agents, $0, no API key. Added 2026-10-26
    from the overnight hunt: agents paid for search far more than transcript."""
    try:
        return search_youtube(q, max_results)
    except ValueError as e:
        return JSONResponse(status_code=400,
                            content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=502,
                            content={"error": "search_failed",
                                     "detail": str(e)[:200]})


@app.get("/agent/v1/youtube-search-paid")
def youtube_search_paid(q: str = Query(""), max_results: int = Query(5),
                        x_payment: str | None = Header(default=None,
                                                       alias="X-PAYMENT")):
    """Paid YouTube search, $0.005 per call, USDC on Base via x402.
    Price chosen by George 2026-10-26. Same conservative flow as
    transcript-paid: verify first, search second, settle only after
    results exist, so a failed search never charges."""
    pay_to = os.getenv("X402_PAY_TO_ADDRESS", "").strip()
    if not re.fullmatch(r"0x[0-9a-fA-F]{40}", pay_to):
        return JSONResponse(
            status_code=503,
            content={"error": "payment_not_configured",
                     "detail": "no valid X402_PAY_TO_ADDRESS is set"})
    if not x_payment:
        return _payment_required(
            pay_to, "0.005", "/agent/v1/youtube-search-paid")
    ok, detail = verify_only(x_payment, pay_to, "0.005")
    if not ok:
        return JSONResponse(status_code=402,
                            content={"error": "payment_invalid",
                                     "detail": detail})
    try:
        result = search_youtube(q, max_results)
    except ValueError as e:
        return JSONResponse(status_code=400,
                            content={"error": str(e),
                                     "payment_settled": False})
    except Exception as e:
        return JSONResponse(status_code=502,
                            content={"error": "search_failed",
                                     "detail": str(e)[:200],
                                     "payment_settled": False})
    if not result.get("results"):
        return JSONResponse(status_code=502,
                            content={"error": "no_results",
                                     "payment_settled": False})
    ok, detail = settle(x_payment, pay_to, "0.005")
    if not ok:
        return JSONResponse(status_code=402,
                            content={"error": "settle_failed",
                                     "detail": detail})
    result["paid"] = True
    result["payment"] = detail
    return result


@app.get("/agent/v1/transcript-paid")
def transcript_paid(url: str = Query(""), lang: str = Query("auto"),
                    x_payment: str | None = Header(default=None,
                                                   alias="X-PAYMENT")):
    """Paid variant. Free endpoint is untouched; this one never serves
    a transcript without a verified + settled $0.01 Base USDC payment.
    url defaults to '' so a bare probe (no url, no payment) gets 402,
    not 422 — directories probe the bare route first."""
    pay_to = os.getenv("X402_PAY_TO_ADDRESS", "").strip()
    if not re.fullmatch(r"0x[0-9a-fA-F]{40}", pay_to):
        return JSONResponse(
            status_code=503,
            content={"error": "payment_not_configured",
                     "detail": "no valid X402_PAY_TO_ADDRESS is set"})
    if not x_payment:
        return _payment_required(
            pay_to, "0.01", "/agent/v1/transcript-paid")
    ok, detail = verify_only(x_payment, pay_to)
    if not ok:
        return JSONResponse(status_code=402,
                            content={"error": "payment_invalid",
                                     "detail": detail})
    if not is_youtube_url(url):
        return JSONResponse(
            status_code=400,
            content={"error": "not_youtube",
                     "detail": "only YouTube URLs are supported"})
    try:
        result = get_transcript_free(url, lang=lang)
    except NoCaptionsError as e:
        # Verified but NOT settled: a no-caption video never charges.
        return JSONResponse(
            status_code=404,
            content={"error": "no_captions", "detail": str(e),
                     "payment_settled": False})
    ok, detail = settle(x_payment, pay_to)
    if not ok:
        return JSONResponse(status_code=402,
                            content={"error": "settle_failed",
                                     "detail": detail})
    result["paid"] = True
    result["payment"] = detail
    return result


def _openapi_spec():
    """OpenAPI 3.1 document for agent-transcript.

    Built for x402scan-style discovery: every payable operation
    declares its input schema, an ``x-payment-info`` block, and a
    402 response. Amounts are USDC micro-units on Base (eip155:8453).
    The pay-to address comes only from the environment at request
    time; when it is absent the payment blocks carry the network,
    asset and amount but no pay-to, so the document never invents
    an address.
    """
    from .x402_verify import USDC_BASE_CONTRACT

    pay_to = os.getenv("X402_PAY_TO_ADDRESS", "").strip()
    valid_pay_to = pay_to if re.fullmatch(
        r"0x[0-9a-fA-F]{40}", pay_to) else None

    def payment_info(amount_usd: str, micro: str):
        info = {
            "scheme": "exact",
            "network": "eip155:8453",
            "asset": USDC_BASE_CONTRACT,
            "currency": "USDC",
            "amount": amount_usd,
            "maxAmountRequired": micro,
            "maxTimeoutSeconds": 60,
        }
        if valid_pay_to:
            info["payTo"] = valid_pay_to
        return info

    def payment_402(amount_usd: str, micro: str):
        accepts = {
            "scheme": "exact",
            "network": "eip155:8453",
            "maxAmountRequired": micro,
            "asset": USDC_BASE_CONTRACT,
            "maxTimeoutSeconds": 60,
            "extra": {"name": "USD Coin", "version": "2"},
        }
        if valid_pay_to:
            accepts["payTo"] = valid_pay_to
        example = {
            "x402Version": 1,
            "error": "payment_required",
            "accepts": [accepts],
        }
        media = {
            "schema": {"$ref": "#/components/schemas/PaymentRequired"},
            "example": example,
        }
        content = {"application/json": media}
        return {
            "description": "Payment required. Retry with an X-PAYMENT "
                           "header carrying a verified x402 payment.",
            "content": content,
        }

    spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "agent-transcript",
            "version": "0.1.0",
            "description": "YouTube search + transcript API for AI agents. "
                           "Free search and free transcript, no account, "
                           "no API key, JSON out. Paid transcript "
                           "$0.01/call and paid search $0.005/call, "
                           "USDC on Base via x402.",
        },
        "servers": [{"url": "https://agent-transcript.fly.dev"}],
        "tags": [
            {"name": "free", "description": "No payment, no account."},
            {"name": "paid", "description": "x402 pay-per-call, USDC on Base."},
            {"name": "discovery", "description": "Health and machine-readable specs."},
        ],
        "paths": {
            "/health": {
                "get": {
                    "tags": ["discovery"], "operationId": "health",
                    "summary": "Health check",
                    "responses": {"200": {"description": "Service is up.",
                        "content": {"application/json": {"schema": {
                            "type": "object",
                            "properties": {"status": {"type": "string"}},
                        }}}},
                },
            },
            },
            "/agent/v1/youtube-search": {
                "get": {
                    "tags": ["free"], "operationId": "youtubeSearch",
                    "summary": "Free YouTube search",
                    "description": "Returns structured video results. "
                                   "Cost $0, no API key.",
                    "parameters": [
                        {"name": "q", "in": "query", "required": True,
                         "schema": {"type": "string"},
                         "description": "Search query."},
                        {"name": "max_results", "in": "query",
                         "required": False,
                         "schema": {"type": "integer", "default": 5,
                                    "minimum": 1},
                         "description": "Max results to return."},
                    ],
                    "responses": {
                        "200": {"description": "Search results.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/SearchResponse"}}}},
                        "400": {"description": "Missing or invalid query.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/Error"}}}},
                        "502": {"description": "Search failed.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/Error"}}}},
                    },
                },
            },
            "/agent/v1/transcript": {
                "get": {
                    "tags": ["free"], "operationId": "getTranscript",
                    "summary": "Free YouTube transcript",
                    "description": "Free caption tiers only. A video with "
                                   "no captions returns 404 and never "
                                   "falls back to a paid service.",
                    "parameters": [
                        {"name": "url", "in": "query", "required": True,
                         "schema": {"type": "string", "format": "uri"},
                         "description": "YouTube URL."},
                        {"name": "lang", "in": "query", "required": False,
                         "schema": {"type": "string", "default": "auto",
                                    "enum": ["auto", "en", "zh"]},
                         "description": "Caption language."},
                    ],
                    "responses": {
                        "200": {"description": "Structured transcript.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/TranscriptResponse"}}}},
                        "400": {"description": "Not a YouTube URL or bad URL.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/Error"}}}},
                        "404": {"description": "Video has no captions.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/Error"}}}},
                    },
                },
            },
            "/agent/v1/youtube-search-paid": {
                "get": {
                    "tags": ["paid"], "operationId": "youtubeSearchPaid",
                    "summary": "Paid YouTube search ($0.005/call)",
                    "description": "Same search as the free endpoint, "
                                   "paid per call. Payment is verified "
                                   "first, results are fetched second, "
                                   "and settlement happens only after "
                                   "results exist, so a failed search "
                                   "never charges.",
                    "x-payment-info": payment_info("0.005", "5000"),
                    "parameters": [
                        {"name": "q", "in": "query", "required": True,
                         "schema": {"type": "string"},
                         "description": "Search query."},
                        {"name": "max_results", "in": "query",
                         "required": False,
                         "schema": {"type": "integer", "default": 5,
                                    "minimum": 1}},
                        {"name": "X-PAYMENT", "in": "header",
                         "required": False,
                         "schema": {"type": "string"},
                         "description": "x402 payment header. Omit it and "
                                        "the endpoint returns 402 with "
                                        "the payment challenge."},
                    ],
                    "responses": {
                        "200": {"description": "Search results, paid.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/SearchResponse"}}}},
                        "400": {"description": "Invalid query; not settled.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/Error"}}}},
                        "402": payment_402("0.005", "5000"),
                        "502": {"description": "Search failed; not settled.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/Error"}}}},
                    },
                },
            },
            "/agent/v1/transcript-paid": {
                "get": {
                    "tags": ["paid"], "operationId": "getTranscriptPaid",
                    "summary": "Paid YouTube transcript ($0.01/call)",
                    "description": "Never serves a transcript without a "
                                   "verified and settled $0.01 Base "
                                   "USDC payment. A no-caption video is "
                                   "verified but never settled, so it "
                                   "never charges.",
                    "x-payment-info": payment_info("0.01", "10000"),
                    "parameters": [
                        {"name": "url", "in": "query", "required": False,
                         "schema": {"type": "string", "format": "uri"},
                         "description": "YouTube URL. May be omitted on a "
                                        "bare probe, which returns 402."},
                        {"name": "lang", "in": "query", "required": False,
                         "schema": {"type": "string", "default": "auto",
                                    "enum": ["auto", "en", "zh"]}},
                        {"name": "X-PAYMENT", "in": "header",
                         "required": False,
                         "schema": {"type": "string"},
                         "description": "x402 payment header. Omit it and "
                                        "the endpoint returns 402 with "
                                        "the payment challenge."},
                    ],
                    "responses": {
                        "200": {"description": "Structured transcript, paid.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/TranscriptResponse"}}}},
                        "400": {"description": "Not a YouTube URL.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/Error"}}}},
                        "402": payment_402("0.01", "10000"),
                        "404": {"description": "No captions; not settled.",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/Error"}}}},
                    },
                },
            },
            "/openapi.json": {
                "get": {
                    "tags": ["discovery"], "operationId": "openapiSpec",
                    "summary": "This OpenAPI 3.1 document",
                    "responses": {"200": {"description": "OpenAPI document."}},
                },
            },
            "/x402.json": {
                "get": {
                    "tags": ["discovery"], "operationId": "x402Spec",
                    "summary": "x402 payment spec",
                    "responses": {"200": {"description": "Payment spec."}},
                },
            },
        },
        "components": {
            "schemas": {
                "Segment": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "number"},
                        "end": {"type": "number"},
                        "text": {"type": "string"},
                    },
                },
                "TranscriptResponse": {
                    "type": "object",
                    "properties": {
                        "video_id": {"type": "string"},
                        "transcript": {"type": "string"},
                        "segments": {"type": "array",
                                     "items": {"$ref": "#/components/schemas/Segment"}},
                        "source": {"type": "string"},
                        "cost_usd": {"type": "number"},
                    },
                },
                "SearchResult": {
                    "type": "object",
                    "properties": {
                        "video_id": {"type": "string"},
                        "title": {"type": ["string", "null"]},
                    },
                },
                "SearchResponse": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "results": {"type": "array",
                                    "items": {"$ref": "#/components/schemas/SearchResult"}},
                        "count": {"type": "integer"},
                        "source": {"type": "string"},
                        "cost_usd": {"type": "number"},
                    },
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "detail": {"type": "string"},
                    },
                },
                "PaymentRequired": {
                    "type": "object",
                    "properties": {
                        "x402Version": {"type": "integer"},
                        "error": {"type": "string"},
                        "accepts": {"type": "array", "items": {
                            "type": "object",
                            "properties": {
                                "scheme": {"type": "string"},
                                "network": {"type": "string"},
                                "maxAmountRequired": {"type": "string"},
                                "asset": {"type": "string"},
                                "payTo": {"type": "string"},
                                "maxTimeoutSeconds": {"type": "integer"},
                                "extra": {"type": "object"},
                            },
                        }},
                        "resource": {"type": "string"},
                    },
                },
            },
        },
    }
    # x402scan probes every operation unless it is explicitly excluded:
    # mark free/discovery operations as security-free so its probe only
    # checks the paid operations, which are the ones that return 402.
    # This is x402scan's own advice from its 2026-10-28 registration
    # check, which reported 0 valid resources and probed all 7 paths.
    for _path in ("/health", "/agent/v1/youtube-search",
                  "/agent/v1/transcript", "/openapi.json", "/x402.json"):
        spec["paths"][_path]["get"]["security"] = []
    # Example inputs so a prober can build a valid call for the paid
    # operations; the endpoints still return 402 before validating
    # the input, so a probe never gets charged or served data.
    spec["paths"]["/agent/v1/transcript-paid"]["get"]["parameters"][0][
        "example"] = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    spec["paths"]["/agent/v1/youtube-search-paid"]["get"]["parameters"][0][
        "example"] = "Rick Astley"
    return spec


@app.get("/openapi.json")
def openapi_json():
    return _openapi_spec()


LANDING_HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>agent-transcript: YouTube transcript API for AI agents</title>
<meta name="description" content="Give an AI agent a YouTube URL, get a structured transcript back as JSON: full text plus timed segments. Free endpoint, no account, no API key. Paid endpoint $0.01 per call in USDC on Base via x402."></head>
<body><h1>agent-transcript</h1>
<p>For AI agents: send a YouTube URL, get its transcript as structured JSON
(full text plus timed segments). No account, no API key, no signup.</p>
<h2>Free tool</h2>
<pre>GET /agent/v1/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&amp;lang=en</pre>
<p>Returns <code>video_id, transcript, segments[{start, end, text}], source, cost_usd</code>.
Free caption tiers only. If a video has no captions, it returns
<code>error=no_captions</code> (HTTP 404) and never falls back to a paid service.</p>
<h2>Paid tool (x402)</h2>
<pre>GET /agent/v1/transcript-paid?url=&lt;YouTube URL&gt;</pre>
<p>Without payment it returns HTTP 402 with the payment requirements:
$0.01 per call, USDC on Base, via the x402 facilitator. Pay, retry with
the <code>X-PAYMENT</code> header, get the transcript. A no-caption video is
verified but never settled, so it never charges.</p>
<h2>Machine-readable discovery</h2>
<ul><li><a href="/llms.txt">/llms.txt</a></li>
<li><a href="/agent/v1/descriptor">/agent/v1/descriptor</a></li>
<li><a href="/.well-known/agent.json">/.well-known/agent.json</a></li>
<li><a href="/.well-known/x402">/.well-known/x402</a> and <a href="/x402.json">/x402.json</a></li>
<li><a href="/openapi.json">/openapi.json</a></li>
<li><a href="/health">/health</a></li></ul>
</body></html>"""


@app.get("/", response_class=HTMLResponse)
def landing():
    return LANDING_HTML


@app.get("/tools/youtube-transcript", response_class=HTMLResponse)
def tool_page():
    return LANDING_HTML


def _agent_manifest():
    pay_to = os.getenv("X402_PAY_TO_ADDRESS", "").strip()
    manifest = {
        "name": "agent-transcript",
        "version": "0.1.0",
        "description": "YouTube transcript API for AI agents: URL in, "
                       "structured transcript JSON out.",
        "tools": [
            {
                "name": "get_youtube_transcript",
                "endpoint": "GET /agent/v1/transcript",
                "params": {"url": "YouTube URL (required)",
                           "lang": "auto|en|zh (default auto)"},
                "returns": "video_id, transcript, segments, source, "
                           "cost_usd",
                "auth": "none",
                "cost_usd_per_call": 0,
            },
            {
                "name": "get_youtube_transcript_paid",
                "endpoint": "GET /agent/v1/transcript-paid",
                "params": {"url": "YouTube URL (required)",
                           "lang": "auto|en|zh (default auto)"},
                "auth": "x402, X-PAYMENT header",
                "cost_usd_per_call": 0.01,
                "network": "base",
                "currency": "USDC",
            },
        ],
        "discovery": ["/llms.txt", "/agent/v1/descriptor",
                      "/.well-known/agent.json", "/.well-known/x402",
                      "/x402.json", "/openapi.json", "/health"],
    }
    if re.fullmatch(r"0x[0-9a-fA-F]{40}", pay_to):
        manifest["x402"] = {"payment_enabled": True, "network": "base",
                            "currency": "USDC",
                            "price_usd_per_call": 0.01, "pay_to": pay_to}
    return manifest


@app.get("/.well-known/agent.json")
def well_known_agent():
    return _agent_manifest()


@app.get("/.well-known/x402")
def well_known_x402():
    return x402_spec()


@app.get("/llms.txt", response_class=PlainTextResponse)
def llms_txt():
    return (
        "# agent-transcript\n\n"
        "YouTube transcript API for AI agents. URL in, structured "
        "transcript JSON out. No account, no API key, no signup.\n\n"
        "## Tools\n\n"
        "- GET /agent/v1/transcript?url=<YouTube URL>&lang=auto|en|zh\n"
        "  Returns JSON: video_id, transcript, segments[{start, end, text}], "
        "source, cost_usd.\n"
        "  Free caption tiers only.\n"
        "  If a video has no captions, the API returns error=no_captions "
        "(HTTP 404) and never falls back to a paid service.\n"
        "- GET /agent/v1/transcript-paid?url=<YouTube URL>&lang=auto|en|zh\n"
        "  Paid variant, $0.01 per call, USDC on Base via x402. Without "
        "payment it returns HTTP 402 with payment requirements; pay and "
        "retry with the X-PAYMENT header.\n"
        "- GET /agent/v1/youtube-search?q=<query>&max_results=5\n"
        "  Free YouTube search, returns structured video results JSON, "
        "no API key, cost_usd 0.\n\n"
        "## Discovery\n\n"
        "- /agent/v1/descriptor\n"
        "- /.well-known/agent.json\n"
        "- /.well-known/x402 and /x402.json\n"
        "- /health\n"
    )


@app.get("/agent/v1/descriptor")
def descriptor():
    return {
        "name": "agent-transcript",
        "version": "0.1.0",
        "tools": [{
            "name": "get_youtube_transcript",
            "endpoint": "GET /agent/v1/transcript",
            "params": {"url": "YouTube URL (required)",
                       "lang": "auto|en|zh (default auto)"},
            "returns": "video_id, transcript, segments, source, cost_usd",
            "auth": "none",
            "cost_usd_per_call": 0,
        }],
    }


@app.get("/x402.json")
def x402_spec():
    # Live spec ONLY when a valid pay-to address is supplied via env.
    # This spec alone does not verify a payment: facilitator verification
    # for a real paid call is still pending, so do not present this as
    # proven live charging until that step is done and deployed.
    pay_to = os.getenv("X402_PAY_TO_ADDRESS", "").strip()
    if re.fullmatch(r"0x[0-9a-fA-F]{40}", pay_to):
        return {
            "payment_enabled": True,
            "network": "base",
            "currency": "USDC",
            "price_usd_per_call": 0.01,
            "pay_to": pay_to,
            "note": "Spec points to the supplied address on Base. "
                    "Paid endpoint /agent/v1/transcript-paid verifies via "
                    "facilitator; a real $0.01 payment test is still pending.",
        }
    return {
        "payment_enabled": False,
        "draft_price_usd_per_call": 0.01,
        "currency": "USDC",
        "note": "Draft price for review. No payment is collected by this build.",
    }
