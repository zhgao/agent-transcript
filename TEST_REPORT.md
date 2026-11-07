# Agent 转写接口本地测试报告（2026-10-25）

代码：`~/workspace/agent-sales-exploration/app/`（`main.py` + `free_transcript.py`）
本地运行：`~/workspace/agent-sales-exploration/.venv` + uvicorn 127.0.0.1:8765（测试后已停）
成本：$0。模块内无付费转写代码（grep 验证无 Deepgram 相关代码），无数据库、无账号。

## 通过

- `GET /health`：`paid_transcription=false, cost_per_call_usd=0`
- `GET /agent/v1/transcript?url=...dQw4w9WgXcQ&lang=en`（Rick Astley）：
  成功，`source=ytdlp`，转写 2089 字符，61 段，首段为歌词。
- `GET /agent/v1/descriptor`：工具描述正常返回，无需 auth，`cost_usd_per_call=0`
- `GET /x402.json`：`payment_enabled=false`，草稿价 $0.01 USDC，明确标注本构建不收款
- 非 YouTube URL：HTTP 400 `not_youtube`
- 无字幕路径：HTTP 404 `no_captions`，且 `paid_fallback=false, paid_fallback_attempted=false`
  （Big Buck Bunny `aqz-KE-bpKQ` 走此路径）

## 过程中修掉的两个真问题

1. 沙箱 MITM 证书：venv 的 certifi 不信任 Hatch 代理 CA，yt-dlp 报 SSL 失败。
   修法（仅本地测试 venv，不改生产代码）：把 Hatch CA 追加进 venv 的 certifi bundle。
2. 超时太短：沙箱出口代理慢，12 秒超时导致 YouTube 失败。
   修法：`CAPTION_TIMEOUT` 改为 60 秒，之后 yt-dlp 层成功。

## 仍有限制（诚实说明）

- `youtube-transcript-api` 层在沙箱被 YouTube 以 IP 封禁（云厂商出口 IP），
  本地成功走的是 yt-dlp 层。生产环境（Fly.io）IP 不同，需在部署后复验两层。
- 本次只做了本地测试，未部署、未上架、未收款。
- 公网部署目前被另一件事卡住：George 2026-10-25 贴的两个 Fly token 经实测均被拒，
  需他重新生成全权限 token 后才能部署（勿再试旧 token）。

## 下一步（需 George 拍板，暂不擅自做）

1. 钱包/收款平台：走代收平台，还是自建 x402 钱包、钱包归谁管
2. 公网部署：重新生成 Fly token 后再部署，或另选免费托管
3. 公开上架目录：文案已备好，定好 1、2 再提交
