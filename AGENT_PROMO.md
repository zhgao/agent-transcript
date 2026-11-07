# agent-transcript — agent圈上架文案（朋友圈版）

公网：https://agent-transcript.fly.dev
状态（2026-10-25 实测，诚实口径）：免费端点已上线并实测通过；
付费端点 $0.01/次、Base USDC、x402 已建成并本地 mock 测通，
真付款结算验证尚未做（George 已选先不充值、等真实买家），
因此不要对外宣称“已结算验证”或“Bazaar 已收录”。

## 英文版（给 agent 目录 / agent 搜索用）

> agent-transcript — YouTube transcript API for AI agents.
> Send a YouTube URL, get a structured transcript back as JSON:
> full text plus timed segments.
>
> Free: GET /agent/v1/transcript?url=<YouTube URL>&lang=en
> No account, no API key, no signup. Free caption tiers only.
> No captions? Returns error=no_captions (404), never a paid fallback.
>
> Paid: GET /agent/v1/transcript-paid?url=<YouTube URL>
> $0.01 per call, USDC on Base via x402. No payment -> HTTP 402
> with payment requirements. Pay, retry with X-PAYMENT, get the transcript.
>
> Discovery: /llms.txt, /agent/v1/descriptor,
> /.well-known/agent.json, /.well-known/x402, /x402.json, /health
> Example: https://agent-transcript.fly.dev/agent/v1/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&lang=en

## 中文版（给人看的说明）

> 给 agent 用的 YouTube 转文字接口：给个 YouTube 链接，
> 返回结构化转写 JSON（全文 + 带时间戳的分段）。
> 免费版不用账号、不用 key；付费版 $0.01/次，Base 链 USDC、走 x402，
> 没付款先回 402 告诉你价格，付完再拿结果。没字幕的视频回 404，
> 不会偷偷走付费转写。

## 目录真相（发之前必须知道）

- Coinbase x402 Bazaar / Agentic.Market：没有提交表单。
  只有一笔真实付款经 facilitator 结算后，才会被收录，
  而且每个目录独立。所以在真付款之前，不可能“上 Bazaar”。
  这也是 George 选先不充值后，Bazaar 这条路暂时走不通的原因。
- 手动目录（可提交、免费、但需人工审核/探测）：
  - 402index：POST /api/v1/register，带 url、name、protocol=x402
  - x402-list.com：/submit 表单
  - PayAPI Market：/list 表单，免费、卖家拿 100%，
    但“结算验证”徽章要他们自己付一笔真钱测通才给
  - awesome-x402：GitHub PR
- agent 自己不逛目录、会做网络搜索，所以本站的
  landing 页、/.well-known/agent.json、/.well-known/x402、
  /llms.txt 本身就是最重要的发现面。
