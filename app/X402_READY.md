# x402 第二轨：接入就绪说明（本地规格已接通，未公网、未真收款验证）

2026-10-25 更新：George 已贴公开地址（格式校验通过：0x + 40 位十六进制，
与截图缩写首尾一致；地址本身不写进本文件、代码仓库或记忆，只走环境变量）。
本地实测：带 `X402_PAY_TO_ADDRESS` 启动后，`GET /x402.json` 返回
`payment_enabled=true, network=base, currency=USDC, price_usd_per_call=0.01,
pay_to=<该地址>`，`/health` 正常。本地服务测完已停。
2026-10-25 续干：公网部署包已备好（`fly.toml`，应用名 agent-transcript，
新加坡区，无数据卷、无数据库；`app/Dockerfile` + `app/requirements.txt`），
付费端点已建成并本地 mock 测通：`GET /agent/v1/transcript-paid` 无付款头
返回 402 + Base USDC $0.01 付款要求，坏头返回 402，mock-valid 头返回
200 且 paid=true（Rick Astley 实测转写正常）；免费端点未动；无字幕视频
只验不结算、不收费。mock 模式仅本地，公网绝不开启。
2026-10-25 晚公网已上线：https://agent-transcript.fly.dev
- 远程构建部署失败（沙箱连 Fly 构建机 TLS 失败，老毛病），改走 machine run
  路线成功：python:3.12-slim 机器（新加坡区，512MB，autostop=stop，
  注意 --autostop 必须用 =stop 写法，否则 stop 会被误当成启动命令导致
  exit_code=2；第一台机器因此报废已销毁，第二台正常）。
- 公网实测全通：/health 正常；/x402.json 返回 payment_enabled=true、
  network=base、USDC、$0.01、pay_to 为 George 的地址；免费转写实测
  Rick Astley 经 captions_api 成功（2089 字符、61 段、cost 0，沙箱里被
  YouTube 封的 captions_api 层在 Fly IP 上通了）。
仍未做：facilitator 真 $0.01 付款验证（需钱包有少量 Base USDC，George
已点选先不充值、等真实买家）、公开上架——在那之前不宣称已开通真收款。

## George 到达后才做的三步（地址一到即做，不需他再操作钱包）

1. George 在手机上新建一个仅用于本实验的 Base 钱包（建议 Coinbase Wallet，
   Base 是它的原生链），备份助记词离线、绝不截图、绝不贴出。
2. George 只贴公开收款地址（`0x…`，42 字符）到聊天。
3. Muse 把该地址放进 `X402_PAY_TO_ADDRESS` 环境变量（不进代码仓库、不进记忆），
   把 `/x402.json` 的 `payment_enabled` 改为 true、`pay_to` 改为该地址，
   再用 x402 facilitator（Coinbase）做一次 $0.01 的端到端验证，
   验证前不公开宣称已开通。

## 绝不做的事

- Muse 不创建钱包、不生成助记词/私钥、不持有、不存储任何私钥材料。
- 地址未到之前，不把草稿价当成真实收费宣传。
- USDC 余额只当实验余额，不攒大额；出金路径由 George 另行决定。
