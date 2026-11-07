# 手动目录上架调研（2026-10-27，未建新号、未提交）

结论：Bazaar / Agentic.Market 无提交表单，需一笔真实 facilitator 结算后才收录，
且各索引独立；上架不等于需求（有爬取称 CDP 索引 77% 资源 30 天内付款者 ≤2 人）。

可提交、无需先建号（待 George 点头后才提交）：
- 402index：POST https://402index.io/api/v1/register，字段 url、name、protocol="x402"，
  可选 description、category、price、contact email；对方会探测端点并排队审核，
  域名验证（按对方给的 token 文件部署）可即时通过。
- PayAPI Market：payapi.market/list，免费上架、无按次费、无分成、卖家拿 100%，
  但“结算验证”徽章需对方自己付一笔真钱测通才给；仅上架不等同于验证。
- PayAPI 实测失败（2026-10-28 06:35-06:40，两次提交均被拒，No row was created）：
  裸付费链接回的不是 402（因缺 url 参数）；带示例参数的链接回 402 且金额/网络/币种/payTo
  均与表单一致，但 PayAPI 仍判“不是 x402 挑战”。根因与 402index 相同：咱们的 402 是
  自定义 JSON，未带标准 x402 挑战头/extra.name 等字段，需改付费端点为标准 x402 格式
  后才能重投，填表本身解决不了。
- 标准 x402 修复已本地完成并测通（2026-10-28，George 采纳建议后开工，未部署公网）：
  app/x402_verify.py 新增 standard_challenge / challenge_header；app/main.py 的
  transcript-paid 与 youtube-search-paid 无付款时回标准挑战：头 PAYMENT-REQUIRED、
  体 x402Version=1、accepts 含 scheme exact、network eip155:8453、金额微单位
  （$0.01→10000、$0.005→5000）、asset 为 Base USDC 合约、extra.name=USD Coin；
  旧 payment_requirements 体同时保留；transcript-paid 的 url 改为默认空值，裸探
  针回 402 不再回 422。本地实测：裸转写付费 402、坏付款头 402 不出转写、付费搜索
  402，全部通过。公网部署仍需 George 再贴一次 Fly token（旧 token 未存档），
  部署后才能重投两个目录。
- 公网部署完成（2026-10-28 07:01 左右，George 新贴的 Fly token 用完即弃、未存档）：
  走 Fly Machines API 更新现有机器（sin 区、python:3.12-slim、/srv/start.sh），
  只替换了 main.py 与 x402_verify.py 两个文件，其余配置与收款环境变量原样保留；
  更新后机器版本已变，start 接口回 412（机器正在替换），但公网请求自动拉起新版，
  实测 health 正常、裸转写付费回 402 且带标准头与标准体。
- 402index 重投成功（2026-10-28）：服务已注册、状态 pending review，健康 healthy、
  可探测，校验回 402、标准 accepts、资产已知；域名验证可即时通过，暂未做，
  等人工审核即可。
- PayAPI Market 重投成功（2026-10-28 07:02）：已提交一次，确认页称 listing 仍 pending，
  待对方 24 小时内审核并做一次付费实测（对方付费、上限 $0.10）通过后才上线，
  每一步会发邮件到 zhgao1981@gmail.com；提交时付费报价已从表单默认 $0.005 修正
  为 $0.01，钱包地址系从公网 402 现场读取；未建号、未登录、未签钱包、未宣称
  settlement-verified，上线链接尚未发放。
- Proxies.sx marketplace：按 agents.proxies.sx/marketplace/submit 的 manifest 提交，
  团队 24 小时内审核；付款直接进卖家钱包、无中间费（此条为搜索结果，未实测表单）。
  **2026-10-28 新查纠正：Proxies.sx 2026-10-02 公告称第三方上架已停用、不再接受
  新服务，该渠道已死，不要再追。**
- x402.new：x402 服务目录，称索引数千个端点；上架方式不是手动提交，而是注册进
  Bazaar 发现网络后自动收录——即仍需一笔真实 CDP facilitator 结算，当前不可直接投。
- x402scan 新细节（2026-10-28 搜索）：需每个域名下有 OpenAPI 3.1 文档
  （/openapi.json，付费操作带 x-payment-info、输入 schema、402 响应定义），
  注册是钱包签名的 SIWX API 调用、非表单；无 schema 的端点会被跳过。咱们目前
  无 openapi.json，需先补该文件并部署，再由 George 本人签名，Muse 不代签。
- openapi.json 已本地建成并测通（2026-10-28，George 点选“先补 openapi.json”后开工，
  未部署公网）：app/main.py 内建 OpenAPI 3.1 文档，7 条路径（health、免费搜索、
  免费转写、付费搜索、付费转写、/openapi.json、/x402.json），两个付费操作均带
  x-payment-info（scheme exact、network eip155:8453、Base USDC 合约、$0.005→5000、
  $0.01→10000）与 402 响应定义，输入参数与真实代码一致；收款地址仅在请求时从
  环境变量注入、代码里未硬编码；本地实测 health、/openapi.json、付费裸探 402
  标准头均通过，测试用假地址、未用 George 真地址。/.well-known/x402 本就存在，
  无需新增。公网部署仍需 George 再贴一次 Fly token（上次 token 用完即弃），
  部署后才能由他本人做 x402scan 的钱包签名注册。
- openapi.json 公网部署完成（2026-10-28 08:54 左右，George 再贴的 Fly token
  用完即弃、未存档）：同法更新现有机器（main.py + x402_verify.py），新版本
  已启动；公网实测 health 正常、/openapi.json 为 3.1.0、7 条路径，两个付费
  操作均带 x-payment-info 与 402，裸转写付费仍回标准 402。
- 402scan 代签（2026-10-28 George 明确授权“代签”）：仍未代签——签名需钱包私钥，
  Muse 没有、也不持有 George 的私钥/助记词，这是他定的钱包红线，授权也不能
  凭空变出私钥；切勿把私钥/助记词贴给 Muse。唯一安全做法是 George 本人在自己
  的钱包 App/浏览器里点签名，Muse 只能备好材料与步骤、并在签名那步把浏览器
  交给他。
- x402scan 注册首试失败（2026-10-28 09:00，George 点头走“表单走到签名步、交浏览器
  给他”后开工）：未提交、未上架、未连钱包、未签名。表单只问 base URL，
  填 agent-transcript.fly.dev 后自动从 /openapi.json 认出名字与描述，无邮箱栏、
  未填邮箱；仅建议在 openapi.json 加 info.contact.email（非阻塞，未加）与
  /favicon.ico。校验报 0 valid resources、Add 按钮禁用，7 条路径均报需回 402
  挑战（含免费与发现路径，付费两条也报 No valid x402 response found，[405]；
  咱们 curl 实测付费裸探确为标准 402，探测失败的确切探法/原因未证实，不排除
  冷启动超时或探法与 GET 不符）。x402scan 自身建议：免费路径加 security: []
  以排除探测、标注必需参数。
- x402scan 修复已本地完成、未部署（2026-10-28）：openapi.json 里免费与发现
  5 条路径加 security: []，付费两条参数加示例（转写示例为 Rick Astley 官方
  视频链接、搜索示例为 Rick Astley），付费端点仍先回 402 再校验输入；本地
  测通 security 与示例均在位。公网部署仍需 George 再贴一次 Fly token，部署
  后重跑 x402scan 注册，Add 按钮可用后才到他本人签名的那一步。
- x402-list 新细节（2026-10-28 搜索）：普通表单（名字、base URL、邮箱、分类、
  端点路径）+ 人工审核；拒绝根路径 /（须如 /v1/resource），拒绝免费托管域名
  （如 vercel.app、workers.dev）；咱们路径符合，但 fly.dev 子域是否被当作免费
  托管待实测，邮箱需 George 另行批准（PayAPI 的邮箱授权不自动复用）。
- Toll402（toll402.dev）：付费上架，basic $1、featured $5/30 天，破 $0 上限，
  未经 George 批准不得投。
- Vermarco（vermarco.com）：垂直市场，称上架免费，$20-$49,999.99 销售额卖家
  拿 95%、$20 以下平台费 $0，Stripe Connect 自动打款；需注册 API key 与 Stripe
  打款账户，是否适合 $0.01 单价、是否需身份验证待核实，未盲投。
- x402 Arena 混淆：此前记的 core.x402arena.gg 与新查到的 arenapay.ai（AVAX 链）
  可能是不同产品，勿凭名字盲投，需核实。
- STX402：Stacks 链（STX/sBTC/USDCx），非 Base USDC，与咱们端点不匹配，跳过。
- MCP 目录（Smithery、Glama、官方 MCP Registry 等）：均面向 MCP 服务器，不是
  REST API 目录；agent-transcript 目前是 REST x402 API、无 MCP 包装，直接投
  不上，需先做 MCP 包装才有意义，属额外开发而非免费上架。
- 其他未核实线索：Circle Agent Marketplace（仅见他人提及已提交，无提交细节）、
  RapidAPI（面向人类的 API 集市、卡支付，与智能体付费不是同一渠道）。

需 George 亲自操作、Muse 不代做：
- x402scan：注册需钱包签名（Sign-In-With-X 式挑战），涉及钱包授权，不代签。
- x402 Arena：POST core.x402arena.gg/register，据称只需健康检查，无需链上证明（未实测）。

未核实：
- x402-list.com 的 /submit 表单本次搜索未返回可信细节，需直接打开核对后再投。
- awesome-x402 具体仓库本次搜索未定位，不要凭名字猜仓库、不要盲目提 PR。

已备好的上架文案（见上一条聊天）：
agent-transcript — YouTube search + transcript API for AI agents. Free search, no account,
no API key, JSON out. Paid transcript $0.01/call, USDC on Base via x402.
Endpoints: /agent/v1/youtube-search, /agent/v1/transcript, /agent/v1/transcript-paid.
Discovery: /llms.txt, /.well-known/agent.json, /x402.json.
