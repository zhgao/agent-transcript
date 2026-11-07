"""Apify Actor: YouTube transcript (free caption tiers only).

Same scope limit as the standalone agent API:
- youtube-transcript-api (free) then yt-dlp caption tracks (free)
- NO paid transcription code exists in this Actor.
- A video with no captions is NOT charged and NOT pushed as data;
  it is recorded as an error item so the run is auditable, not silent.

Pricing is NOT hard-coded here. Apify charges by event name; the price
for `transcript-delivered` is set in the Apify Console pricingInfos
(PAY_PER_EVENT, draft $0.05 per delivered transcript, to confirm at
publish time). Charge BEFORE push_data, inside the handler, so the
charge cannot vanish when the run closes.
"""

from apify import Actor

from .free_transcript import NoCaptionsError, get_transcript_free


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        url = (actor_input.get("videoUrl") or "").strip()
        lang = actor_input.get("lang") or "auto"
        if not url:
            Actor.log.error("videoUrl is required")
            await Actor.push_data(
                {"error": "missing_videoUrl", "charged": False})
            return
        try:
            result = get_transcript_free(url, lang=lang)
        except NoCaptionsError as exc:
            # No charge on failure. Do not fall back to anything paid.
            Actor.log.warning("no captions: %s", exc)
            await Actor.push_data(
                {"video_id": None, "url": url, "error": "no_captions",
                 "charged": False, "detail": str(exc)[:500]})
            return
        except ValueError as exc:
            await Actor.push_data(
                {"url": url, "error": "bad_url", "charged": False,
                 "detail": str(exc)[:500]})
            return
        # Charge only on a delivered transcript, before pushing data.
        await Actor.charge("transcript-delivered")
        await Actor.push_data({
            "video_id": result["video_id"],
            "url": url,
            "transcript": result["transcript"],
            "segments": result["segments"],
            "source": result["source"],
            "cost_usd": 0,
            "charged": True,
            "charge_event": "transcript-delivered",
        })


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
