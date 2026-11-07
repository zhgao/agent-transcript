# 卖给 Agent 探索计划（0元开局）

- 目标：2026-10-25 至 2026-12-25，卖给 agent 而非只卖给人
- 硬约束：新增支出 $0，净收入 ≥ 0；$1000 仅为冲刺目标，不强求
- 成功标准（探索成立）：有非本人的真实付费/调用、有复购、期满能说清哪类服务、什么价位、成本多少、继续/转向/停掉

## 为什么第一个商品是 YouTube 转写（免费字幕层）

Transcriptly 已有现成链路 `backend/app/extractor.py`：
1. youtube-transcript-api（免费，约5秒）
2. yt-dlp 字幕轨（免费）
3. Deepgram AI 转写（付费）

0元开局只做 1+2，**硬关第3层**：无字幕视频返回干净的 `no_captions`，绝不自动 fallback 到付费转写。
这正好撞上实测卖出去的东西：别人第一天 18 次付费调用里 16 次是 YouTube 搜索、1 次是 YouTube 转写，单价 $0.005-$0.01。

## 第一个商品规格（草稿，不改现有 Transcriptly 人用功能）

- 独立 agent 接口，不动现有 `/api/extract` 和人用前端
- 输入：`GET /agent/v1/transcript?url=<YouTube URL>&lang=auto`
- 输出：结构化 JSON：`video_id, title?, transcript, segments[{start, end, text}], source: captions_api|ytdlp, cost: 0`
- 无字幕：`{error: no_captions, source: none}`，不扣费、不走付费层
- 拟议价（待钱包决定后才生效）：$0.01/次；探索期先以免费调用验证“被发现、被调用”
- 机器可发现：`/llms.txt`、MCP 工具描述、`/x402.json` 价格说明（草稿，付费未开通前不宣称可收款）

## 第1周行动（0元，不擅自建定时任务、不花钱、不公开上架）

1. 本地抽出独立 agent 接口 + 硬关付费层开关，测试：3 个有字幕视频通过、1 个无字幕视频干净返回
2. 写好 llms.txt / MCP 描述 / 上架文案
3. 列出免费上架目录清单（x402scan、Agent402、MCP Registry、AgentMart 等），文案备好、暂不上架
4. 下一个请示点：钱包归谁管、走哪个收款平台（AgentMart/Obolo 等代收，还是自建 x402 钱包），定好再公开上架和开通收费

## 成本账本

见 LEDGER.md。当前新增支出：$0。

## 止损 / 转向规则

- 11月25日（30天）：无真实调用 → 砍微支付，只试高价值任务（研究报告、代码审查分包）
- 任何一步要花钱 → 先停，先请示，不追加
- 12月25日：凭账本和调用数据出结论：继续 / 转向 / 停掉
