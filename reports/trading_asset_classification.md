# 交易研究资产分类总表

生成时间：2026-06-26 Asia/Shanghai。  
来源：`reports/all_strategy_trading_master_summary.md`。

这份文件把本机已经盘点到的交易研究资料按用途和后续处理方式重新分类。它不是实盘信号清单，也不是投资建议；所有 live/trading 动作都必须先通过人工确认、账户权限、凭证和风控门槛。

## 总体结论

当前资产可以分成 7 类：

| 类别 | 名称 | 价值 | 当前动作 |
|---|---|---|---|
| A | 核心策略研究线 | 最高 | 继续研究和回测，禁止直接实盘 |
| B | Polymarket / PM 资产线 | 高 | 继续 paper/backtest，live 需要凭证和 preflight |
| C | 数据与 API 工具线 | 高 | 作为基础设施复用 |
| D | 风控与增强特征线 | 中高 | 接到策略前作为过滤器和风险层 |
| E | 通用回测框架线 | 中高 | 新策略优先复用 |
| F | 宏观/跨资产观察线 | 中 | 只做观察和事件记录 |
| G | 实盘边界与人工事项 | 必须处理 | 不满足前不得下单 |

## A. 核心策略研究线

### A1. Binance 多策略研究

**定位**：当前最完整的非 PM 交易研究资产。

**主要路径**：

- `/Users/m/Documents/Codex/2026-06-04/biance`
- `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot`

**已有资产**：

- 95 个多币种 OHLCV 缓存。
- 48 个策略/扫描/回测 JSON。
- 7 个多周期回测表格。
- 当前状态、阈值敏感性、live gate、futures readiness 等报告。

**当前结论**：

- 主要观察：`BCHUSDT`、`TRXUSDT`、`UNIUSDT`。
- 降级或淘汰：`ETH`、`DOT`、`AVAX`、`NEAR`、`XRP`、`SOL`、`LINK`。
- `eligible_entry_count=0`、`live_eligible_entry_count=0` 时不应下新单。
- Binance Futures 账户读取存在 `451 restricted location` 阻塞。

**下一步**：

1. 继续把 Binance 线作为回测/研究主线。
2. 不把 cache-only 结果当 live gate。
3. 先解决账户读取与区域限制，再谈小额实盘。

### A2. BTC / Polymarket Up/Down 研究

**定位**：当前最完整的 PM/BTC 方向纸面研究系统。

**主要路径**：

- `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy`
- GitHub: `https://github.com/MM-sheng/zeroleak-llm-proxy/tree/btc-pm-strategy`

**已有资产**：

- BTC Up/Down event metadata cache。
- CLOB price-history cache。
- Data API trades cache。
- Price-history backtest report。
- 194 个测试覆盖当前系统。

**当前结论**：

- Phase 9 完成。
- Phase 10 live trading 锁定。
- 项目只能 paper/backtest/read-only，不能接钱包或下单。

**下一步**：

1. 保持 `btc-pm-strategy` 分支可复现。
2. 若要长期发展，应迁到独立仓库 `MM-sheng/btc-pm-strategy`。
3. 新增真实交易前必须先完成 Phase 10 解锁条件。

## B. Polymarket / PM 资产线

### B1. Reward / 做市机会扫描

**定位**：PM reward 市场发现和纸面模拟资产。

**主要路径**：

- `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner`
- `/Users/m/Documents/Codex/2026-06-25/ni/outputs/polymarket-reward-scanner`

**已有资产**：

- `polymarket_reward_markets.csv`
- `paper_sim_results.csv`
- `top_market_observations.csv`
- reward report / paper sim report / top market observation report。

**用途**：

- 找 reward/做市候选市场。
- 观察 bid/ask、spread、depth、reward eligibility。
- 做 paper simulation，不做真实挂单。

**下一步**：

1. 和 BTC Up/Down 系统分开管理。
2. 把 reward scanner 作为独立工具项目整理。
3. live 前必须先做 CLOB auth、post-only、cancel safety、资金上限和 dry-run。

### B2. MM Rewards / 做市模块

**定位**：PM 做市奖励 dry-run/backtest 模块。

**主要路径**：

- `/Users/m/Documents/Codex/2026-06-16/files-mentioned-by-the-user-txt`

**用途**：

- 做 market-maker rewards 回测。
- 做 sample ticks、runbook、dry-run 到 live test 的流程设计。

**下一步**：

1. 暂时只作为参考模块。
2. 不和 BTC Up/Down 项目混在一个仓库主线里。
3. 如果继续做，独立成 `polymarket-reward-scanner` 或 `pm-mm-rewards` 仓库。

## C. 数据与 API 工具线

### C1. Polymarket API

**定位**：PM 系统的主要外部数据面。

**分类**：

| API | 权限 | 用途 |
|---|---|---|
| Gamma API | public | market/event/tag/sports discovery |
| CLOB API | read public, trading auth required | orderbook, prices, price history, orders |
| Data API | mostly public reads | trades, activity, positions, analytics |
| Market WebSocket | public | real-time orderbook and prices |
| User WebSocket | auth required | personal order/trade lifecycle |
| Sports WebSocket | public | sports score/status |
| RTDS | optional auth | comments, crypto/equity prices |

**下一步**：

1. 市场发现先用 Gamma。
2. 盘口/价格用 CLOB。
3. 历史验证优先用已缓存数据。
4. live 只能走 official SDK + L1/L2 auth。

### C2. Binance API

**定位**：非 PM 策略主数据面。

**分类**：

| API | 权限 | 用途 |
|---|---|---|
| Binance Spot/Public REST | public/signed | klines, ticker, account, order |
| Binance Futures REST | public/signed | futures market/account/preflight/order |
| Binance public mirror | public | historical klines fallback |
| Spot Testnet | testnet key | spot sandbox |
| Futures Testnet | testnet key | futures sandbox |

**当前问题**：

- Futures account read 存在 `451 restricted location`。
- 在账户读取恢复前，禁止任何 live path。

### C3. Dune / Birdeye API Kit

**定位**：链上数据增强工具。

**主要路径**：

- `/Users/m/Documents/Codex/2026-06-21/dune-birdeye`

**用途**：

- Dune SQL/query results。
- Birdeye token price/liquidity/network data。
- 聪明钱、holder、wallet、token liquidity 方向的数据增强。

**下一步**：

1. 作为独立数据工具保留。
2. API key 只放本地 env。
3. 不直接和交易执行逻辑耦合。

### C4. Coinbase Candles

**定位**：BTC Up/Down 回测的公开价格源。

**用途**：

- 用 Coinbase `BTC-USD` candles 做 resolution/price-history 辅助。
- 适合 read-only 回测，不适合替代交易所执行价格。

## D. 风控与增强特征线

### D1. Crypto Risk Research

**定位**：高风险 crypto 策略的二级风险过滤器。

**主要路径**：

- `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research`

**已有模块**：

- funding features。
- open interest features。
- liquidation features。
- volume/volatility features。
- signal engine。
- paper executor。
- risk limits。
- kill switch / liquidation price / position sizing。

**下一步**：

1. 不作为独立交易入口。
2. 作为 Binance/PM 研究线的风控增强层。
3. 先把特征质量和风险阈值做成离线测试。

## E. 通用回测框架线

### E1. Mean-Reversion Strategy Framework

**定位**：通用事件驱动回测骨架。

**主要路径**：

- `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy`

**已有模块**：

- Strategy。
- NextBarOpenFillModel。
- RegimeDetector。
- RiskManager。
- PositionSizer。
- sample OHLCV。

**下一步**：

1. 新策略优先复用这个骨架。
2. 保持 next-bar fill 和 no-lookahead。
3. 不直接接入真实下单。

## F. 宏观/跨资产观察线

### F1. CPI / IBKR / TradingView

**定位**：宏观事件观察和跨资产 reaction screen。

**主要路径**：

- `/Users/m/Documents/Codex/2026-06-10/8-30-cpi`
- `/Users/m/Documents/Codex/2026-06-10/ibkr-tws-mosaic-cpi-6-k`

**用途**：

- CPI 事件 watchlist。
- TradingView 图表和数据覆盖。
- IBKR/TWS 数据订阅、权限、跨资产观察。

**边界**：

- 账户、订阅、交易权限都需要人工处理。
- 当前只做观察和记录，不做自动交易。

## G. 实盘边界与人工事项

这些不是项目资产，而是必须先处理的 gates。

| Gate | 当前状态 | 未满足时的规则 |
|---|---|---|
| Binance 区域/账户读取 | `451 restricted location` | 禁止 futures live |
| Binance live signal | 当前无合格 live entry | 不下新单 |
| PM 私钥/API key | 未确认真实可用 | 禁止签名和下单 |
| PM funder/Safe | 未确认 | 禁止 live preflight 之后的动作 |
| CLOB L1/L2 auth | 未确认 | 禁止 order/cancel |
| IBKR/TradingView 权限 | 需人工订阅/确认 | 只观察不执行 |
| cache-only 结果 | 只能研究 | 不能当 live gate |

## 建议仓库拆分

| 未来仓库 | 应放内容 | 不应放内容 |
|---|---|---|
| `btc-pm-strategy` | BTC/PM UpDown research, backtest, paper reports | PM reward scanner, Binance live bot |
| `polymarket-reward-scanner` | reward/opportunity scan, paper sim, top market observations | wallet/private keys |
| `crypto-strategy-bot` | Binance multi-strategy backtests and reports | PM-specific code |
| `crypto-risk-research` | funding/OI/liquidation/risk filters | live execution |
| `dune-birdeye-kit` | API client and sample outputs | strategy execution |
| `mean-reversion-strategy` | reusable event-driven backtest framework | exchange-specific credentials |

## 当前优先级

1. **先保存和整理资料**：本文件和原始总汇总已进入 `btc-pm-strategy` 分支的 `reports/`。
2. **先分仓库，不急实盘**：不同资产线不要继续混在一个仓库分支里。
3. **先回测再 paper，再 preflight**：任何 live 之前都要有可重复验证链路。
4. **先处理人工 gate**：凭证、区域、账户权限、订阅和签名都不是代码能自动跳过的事。

