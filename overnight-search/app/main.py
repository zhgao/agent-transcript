from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from app.youtube_search import search_youtube

app = FastAPI(title="youtube-search (overnight draft, free)")

@app.get("/health")
def health():
    return {"status": "ok", "service": "youtube-search", "cost_per_call_usd": 0}

@app.get("/agent/v1/youtube-search")
def youtube_search(q: str = Query(""), max_results: int = 5):
    try:
        return search_youtube(q, max_results)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": "search_failed", "detail": str(e)[:200]}, status_code=502)
