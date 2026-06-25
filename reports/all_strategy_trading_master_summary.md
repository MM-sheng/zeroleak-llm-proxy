# 策略交易资料总汇总

生成时间：2026-06-25T23:57:51 Asia/Shanghai。  
范围：本机 Codex 工作区里已经找到的 PM/Polymarket 与非 PM 策略交易资料、数据、代码、API、经验文档和实盘边界。没有输出任何 `.env`、私钥、API secret 或账户凭证内容。

## 一句话结论

本机最有价值的交易研究资产分成三层：

1. **可立即继续研究的策略资料**：Binance 多策略回测、PM reward/做市扫描、BTC/PM Up/Down 缓存、crypto risk research、mean-reversion 回测骨架。
2. **可作为数据源/API 的工具**：Binance Spot/Futures、Polymarket Gamma/CLOB/Data/WebSocket、Dune、Birdeye、Coinbase candles、TradingView、IBKR/TWS。
3. **必须人工处理的实盘边界**：Binance `451 restricted location`、PM 私钥/签名凭证、IBKR/TradingView 数据订阅与交易权限。

## 总数量

| 类别 | PM/Polymarket | 非 PM | 合计 |
|---|---:|---:|---:|
| 数据/结果条目 | 24 | 77 | 101 |
| 经验/文档条目 | 45 | 56 | 101 |
| API/数据源条目 | 15 | 16 | 31 |
| 代码模块条目 | - | 105 | 105 |

## 最高优先级

### 1. Binance 策略线

- 最完整的非 PM 交易项目在 `/Users/m/Documents/Codex/2026-06-04/biance`。
- 已有 95 个多币种 OHLCV 缓存、48 个策略/扫描/回测 JSON、7 个回测表格、当前状态与阈值报告。
- 当前报告结论：BCHUSDT、TRXUSDT、UNIUSDT 是主要观察对象；ETH/DOT/AVAX/NEAR/XRP/SOL/LINK 被降级或淘汰。
- 当前不能实盘：Binance Futures 账户读取遇到 `451 restricted location`，且 live scan 没有合格入场信号。

### 2. Polymarket / PM 策略线

- 主要资产：reward/opportunity 扫描、BTC/PM Up/Down 回测缓存、做市奖励 dry-run/backtest 模块、reward scanner 观测和 paper simulation。
- 主要 API：Gamma 用于市场发现，CLOB 用于盘口/价格/交易，Data API 用于 trades/activity/positions，WebSocket 用于实时盘口和个人订单事件。
- 当前凭证边界：没有找到真实可用 PM 私钥文件；已有 `.env` 变量多为占位符形态。真实 live 必须重新人工确认签名凭证。

### 3. 风险与数据增强

- `crypto_risk_research`：funding、open interest、liquidation、volume、volatility 特征，以及 signal engine、paper executor、risk limits。
- `Dune/Birdeye API Kit`：链上聪明钱、token liquidity、价格、SQL 查询结果。
- `mean-reversion-strategy`：通用事件驱动回测骨架，适合新策略快速接入。
- `CPI/IBKR/TradingView`：宏观事件观察和跨资产 reaction screen。

## 实盘安全边界

- **不要从缓存结果直接实盘**：cache-only 只能做研究，不能通过 live gate。
- **Binance**：必须先解决 `451 restricted location`，恢复账户读取并确认旧仓位/保护单；然后才考虑 5 USDT 门槛测试。
- **PM/Polymarket**：必须先确认真实签名私钥、funder/Safe、API key、L1/L2 auth；先 backtest/paper/live preflight，再考虑任何交易。
- **IBKR/TradingView**：市场数据订阅、交易权限、身份声明和下单都需要人工处理。

## 输出文件索引

| 文件 | 用途 |
|---|---|
| `polymarket_experience_data_and_api_inventory.md` | PM/Polymarket 完整总结 |
| `non_pm_strategy_trading_inventory.md` | 非 PM 完整总结 |
| `polymarket_data_inventory.csv` | PM 数据/缓存明细 |
| `polymarket_documents_inventory.csv` | PM 文档/经验明细 |
| `polymarket_api_inventory.csv` | PM API 明细 |
| `non_pm_strategy_data_inventory.csv` | 非 PM 数据/结果明细 |
| `non_pm_strategy_documents_inventory.csv` | 非 PM 文档/经验明细 |
| `non_pm_strategy_code_inventory.csv` | 非 PM 代码模块明细 |
| `non_pm_strategy_api_inventory.csv` | 非 PM API/数据源明细 |

---

## Part A - Polymarket / PM 资料

生成时间：2026-06-25T23:47:24 Asia/Shanghai 本机时间。

## 结论

- 本机 Polymarket 相关经验数据主要来自四条线：reward/opportunity 扫描、BTC/Polymarket Up/Down 回测缓存、做市奖励 dry-run/backtest 模块、今天生成的 reward scanner 观测与 paper simulation。
- 当前后续最常用 API 是 Gamma API 做市场发现，CLOB API 做盘口/价格/交易，Data API 做 trades/activity/positions，WebSocket 做实时盘口与个人订单事件。
- 本清单没有输出任何私钥或 API secret；`.env` 只作为配置文件路径记录，真实 live 前仍需要单独人工确认凭证。

## 数据根目录

- `/Users/m/Documents/Codex/2026-06-07/polymarket`
- `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt/outputs/btc_pm_strategy`
- `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy`
- `/Users/m/Documents/Codex/2026-06-16/files-mentioned-by-the-user-txt`
- `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner`
- `/Users/m/Documents/Codex/2026-06-25/ni/outputs/polymarket-reward-scanner`

## 数据类别汇总

| 类别 | 条目数 | 大小 | 说明 |
|---|---:|---:|---|
| `backtest` | 3 | 7.1 KB | 历史回测指标、交易日志、样例 tick |
| `btc_price_history` | 10 | 135.8 KB | BTC OHLCV 或 candles 数据 |
| `json_data` | 1 | 313 B | 其他 JSON 数据 |
| `manifest` | 1 | 449 B | 训练/数据生成 manifest |
| `reward_market_scan` | 4 | 393.9 KB | Polymarket reward/做市候选市场扫描结果 |
| `tabular_data` | 1 | 66.6 KB | 其他 CSV 数据 |
| `trade_journal` | 1 | 351 B | 策略交易/纸面执行日志 |
| `updown_event_metadata_cache` | 1 | 792.0 KB | BTC Up/Down Gamma event JSON 缓存目录 |
| `updown_price_history_cache` | 1 | 27.4 KB | BTC Up/Down outcome token 的 CLOB price history JSON 缓存目录 |
| `updown_trades_cache` | 1 | 25.1 MB | BTC Up/Down Data API trades JSON 缓存目录 |

## 重点数据文件

| 类别 | 路径 | 记录/文件数 | 字段/说明 |
|---|---|---:|---|
| `backtest` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt/outputs/btc_pm_strategy/data/backtest/backtest_metrics.json` | 1 object | total_return, CAGR_if_applicable, win_rate, average_win, average_loss, max_drawdown, sharpe, sortino, brier_score, log_loss, ROI_per_trade, profit_factor, calibration_quality, turnover, exposure, largest_loss, losing_streak, sensitivity_to_ |
| `backtest` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt/outputs/btc_pm_strategy/data/backtest/backtest_trades.csv` | 54 | timestamp, question, action, model_probability, market_price, edge, stake, resolved, pnl |
| `backtest` | `/Users/m/Documents/Codex/2026-06-16/files-mentioned-by-the-user-txt/outputs/sample_backtest_ticks.csv` | 4 | timestamp, mid, spread_pct, volume_24h, rewards_weight, competition_score, liquidity_gap |
| `btc_price_history` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/candles/coinbase_1782304500_1782308100.json` | 61 | close, open, timestamp_utc |
| `btc_price_history` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/candles/coinbase_1782304800_1782308400.json` | 61 | close, open, timestamp_utc |
| `btc_price_history` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/candles/coinbase_1782305100_1782308700.json` | 61 | close, open, timestamp_utc |
| `btc_price_history` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/candles/coinbase_1782305700_1782309300.json` | 61 | close, open, timestamp_utc |
| `btc_price_history` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/candles/coinbase_1782306900_1782307800.json` | 16 | close, open, timestamp_utc |
| `btc_price_history` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/candles/coinbase_1782348900_1782359700.json` | 181 | close, open, timestamp_utc |
| `btc_price_history` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/candles/coinbase_1782349500_1782360300.json` | 180 | close, open, timestamp_utc |
| `btc_price_history` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/candles/coinbase_1782356700_1782360300.json` | 61 | close, open, timestamp_utc |
| `btc_price_history` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/candles/coinbase_1782382800_1782393600.json` | 180 | close, open, timestamp_utc |
| `btc_price_history` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt/outputs/btc_pm_strategy/data/raw/btc_ohlcv_1h_365d.csv` | 1000 | timestamp, open, high, low, close, volume |
| `manifest` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt/outputs/btc_pm_strategy/data/processed/training_manifest.json` | 1 object | status, message, required_columns, live_trading |
| `reward_market_scan` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/data/paper_sim_results.csv` | 2 | simulated_at, sample_index, market_id, slug, classification, token_id, bid_quote, ask_quote, quote_spread, mid, order_size, post_only_safe, reward_spread_eligible, depth_sufficient, queue_depth_ratio, fill_frequency_proxy, exit_difficulty_s |
| `reward_market_scan` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/data/polymarket_reward_markets.csv` | 161 | rank, classification, overall_score, capital_efficiency_score, daily_reward_score, spread_score, volume_score, liquidity_score, fee_risk_score, data_quality_score, risk_flags, id, question, slug, conditionId, marketMakerAddress, active, clo |
| `reward_market_scan` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/data/top_market_observations.csv` | 2 | observed_at, sample_index, rank, classification, market_id, slug, question, token_id, best_bid, best_ask, spread, mid, bid_depth, ask_depth, rewards_daily_rate, rewards_min_size, rewards_max_spread, eligible_spread, ... |
| `reward_market_scan` | `/Users/m/Documents/Codex/2026-06-25/ni/outputs/polymarket-reward-scanner/data/polymarket_reward_markets.csv` | 156 | rank, classification, overall_score, capital_efficiency_score, daily_reward_score, spread_score, volume_score, liquidity_score, fee_risk_score, data_quality_score, risk_flags, id, question, slug, conditionId, marketMakerAddress, active, clo |
| `trade_journal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt/outputs/btc_pm_strategy/data/processed/trade_journal.csv` | 1 | timestamp, market_id, question, action, side, entry_price, model_probability, edge, size, rationale, current_mark_to_market, final_resolution, pnl, lesson |
| `updown_event_metadata_cache` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/events/` | 117 files | examples: /Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/events/btc-updown-15m-1782359100.json; /Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/d |
| `updown_price_history_cache` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/prices/` | 134 files | examples: /Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/prices/47583710713395556441703082222776588147624220622971949106371370547627672350400_1782358200_1782359100.json; /Users/m/Docu |
| `updown_trades_cache` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/trades/` | 36 files | examples: /Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/data/updown_cache/trades/0x2fe32f71fc5bd65bdab7d613ce89f35311c513016a24203eaa9c6400dbdb7156.json; /Users/m/Documents/Codex/2026-06-07/files-ment |

完整数据 CSV：`polymarket_data_inventory.csv`。

## 本机代码中发现的 API

| API/源 | URL | 权限 | 用途 |
|---|---|---|---|
| Binance public market data | `https://api.binance.com/api/v3/ticker/price` | public read | BTC price/klines fallback |
| Coinbase Exchange API | `https://api.exchange.coinbase.com/products/BTC-USD/candles` | public read | BTC-USD candles for up/down backtests |
| Polymarket CLOB API | `https://clob.polymarket.com` | public read for book/prices; auth for trading | orderbook, prices, price history, order management |
| Polymarket CLOB API | `https://clob.polymarket.com/prices-history` | public read for book/prices; auth for trading | orderbook, prices, price history, order management |
| Binance public market data | `https://data-api.binance.vision/api/v3/klines` | public read | BTC price/klines fallback |
| Polymarket Data API | `https://data-api.polymarket.com/trades` | public read for used endpoints | trades/activity/positions/analytics style data |
| Polymarket docs | `https://docs.polymarket.com/api-reference/markets/list-markets` | public | reference documentation |
| Polymarket docs | `https://docs.polymarket.com/market-data/fetching-markets` | public | reference documentation |
| Polymarket docs | `https://docs.polymarket.com/market-data/overview` | public | reference documentation |
| Polymarket docs | `https://docs.polymarket.us/fees` | public | reference documentation |
| Polymarket Gamma API | `https://gamma-api.polymarket.com` | public read | market/event/tag/sports discovery and metadata |
| Polymarket Gamma API | `https://gamma-api.polymarket.com/events` | public read | market/event/tag/sports discovery and metadata |
| Polymarket Gamma API | `https://gamma-api.polymarket.com/markets` | public read | market/event/tag/sports discovery and metadata |

完整 API CSV：`polymarket_api_inventory.csv`。

## 经验/研究文档

这些是可读的 Polymarket 经验沉淀：研究报告、prompt、runbook、恢复说明、项目 README 和协作记录。完整 CSV：`polymarket_documents_inventory.csv`。

| 类别 | 路径 | 标题/说明 |
|---|---|---|
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/.collab/board.md` | Collaboration Board |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/.collab/decisions.md` | Decisions |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/.collab/handoffs/claude.md` | Claude Code Handoff |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/.collab/handoffs/codex.md` | Codex Handoff |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/DECISIONS.md` | DECISIONS.md |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-16/files-mentioned-by-the-user-txt/.collab/board.md` | Collaboration Board |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-16/files-mentioned-by-the-user-txt/.collab/decisions.md` | Decisions |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-16/files-mentioned-by-the-user-txt/.collab/handoffs/claude.md` | Claude Code Handoff |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-16/files-mentioned-by-the-user-txt/.collab/handoffs/codex.md` | Codex Handoff |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/.collab/board.md` | Collaboration Board |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/.collab/decisions.md` | Decisions |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/.collab/handoffs/claude.md` | Claude Code Handoff |
| `collaboration_notes` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/.collab/handoffs/codex.md` | Codex Handoff |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/AGENTS.md` | AGENTS.md |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/CLAUDE.md` | Codex + Claude Code Collaboration |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/CONTEXT.md` | CONTEXT.md |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/PROJECT_SPEC.md` | PROJECT_SPEC.md |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/REPOSITORY.md` | Repository Notes |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/TASKS.md` | TASKS.md |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/requirements.txt` | pandas |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt/outputs/btc_pm_strategy/requirements.txt` | pandas>=2.0 |
| `doc` | `/Users/m/Documents/Codex/2026-06-16/files-mentioned-by-the-user-txt/requirements.txt` | httpx>=0.27 |
| `doc` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/AGENTS.md` | Codex + Claude Code Collaboration |
| `doc` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/requirements.txt` | requests>=2.32.0 |
| `doc` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/src/polymarket_reward_scanner.egg-info/SOURCES.txt` | README.md |
| `doc` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/src/polymarket_reward_scanner.egg-info/dependency_links.txt` |  |
| `doc` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/src/polymarket_reward_scanner.egg-info/requires.txt` | requests>=2.32.0 |
| `doc` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/src/polymarket_reward_scanner.egg-info/top_level.txt` | polymarket_reward_scanner |
| `doc` | `/Users/m/Documents/Codex/2026-06-25/ni/outputs/polymarket-reward-scanner/requirements.txt` | requests>=2.32.0 |
| `live_runbook` | `/Users/m/Documents/Codex/2026-06-16/files-mentioned-by-the-user-txt/outputs/live_test_runbook.md` | MM Rewards Backtest to Live Test Runbook |
| `project_readme` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/README.md` | BTC Polymarket Probability & Paper Trading Research System |
| `project_readme` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt/outputs/btc_pm_strategy/README.md` | BTC Probability + Polymarket Strategy Research System |
| `project_readme` | `/Users/m/Documents/Codex/2026-06-16/files-mentioned-by-the-user-txt/mm_rewards/README.md` | Polymarket Market Maker Rewards Optimizer |
| `project_readme` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/README.md` | polymarket-reward-scanner |
| `project_readme` | `/Users/m/Documents/Codex/2026-06-25/ni/outputs/polymarket-reward-scanner/README.md` | polymarket-reward-scanner |
| `prompt_pack` | `/Users/m/Downloads/polymarket_mm_prompt.md` | Polymarket Weather Market-Making Bot — Claude Code Prompt |
| `recovery_notes` | `/Users/m/Documents/Codex/2026-06-25/ni/outputs/polymarket_full_ui_recovery.md` | Polymarket full UI recovery |
| `recovery_notes` | `/Users/m/Documents/Codex/2026-06-25/ni/outputs/polymarket_project_recovery.md` | Polymarket project recovery note |
| `research_report` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-2/btc_pm_strategy/reports/updown_price_history_backtest_report.md` | BTC Up/Down Price-History Backtest Report |
| `research_report` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt/outputs/btc_pm_strategy/data/processed/daily_report.md` | BTC Polymarket Daily Research Report |
| `research_report` | `/Users/m/Documents/Codex/2026-06-07/polymarket/outputs/polymarket_profit_strategy_research.md` | Polymarket 暴利策略研究 |
| `research_report` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/reports/paper_sim_report_zh.md` | 纸面模拟报告 |
| `research_report` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/reports/polymarket_reward_report_zh.md` | Polymarket 奖励型做市市场扫描报告 |
| `research_report` | `/Users/m/Documents/Codex/2026-06-25/files-mentioned-by-the-user-polymarket/outputs/polymarket-reward-scanner/reports/top_market_observation_report_zh.md` | Top 市场只读观察报告 |
| `research_report` | `/Users/m/Documents/Codex/2026-06-25/ni/outputs/polymarket-reward-scanner/reports/polymarket_reward_report_zh.md` | Polymarket 奖励型做市市场扫描报告 |

## 官方当前 API 面（2026-06-25 核对）

| 名称 | 地址/包 | 权限 | 什么时候用 |
|---|---|---|---|
| Gamma API | `https://gamma-api.polymarket.com` | Public | Markets, events, tags, series, comments, sports, search, public profiles. Primary discovery/browsing API. |
| Data API | `https://data-api.polymarket.com` | Mostly public for used data reads | User positions, trades, activity, holder data, open interest, leaderboards, builder analytics. |
| CLOB API | `https://clob.polymarket.com` | Read endpoints public; trading/auth endpoints require L1/L2 auth | Orderbook, prices, price history, spreads, balances/allowances, orders/cancels. |
| Market WebSocket | `wss://ws-subscriptions-clob.polymarket.com/ws/market` | Public | Real-time orderbook, price changes, last trades, best bid/ask, new/resolved markets. |
| User WebSocket | `wss://ws-subscriptions-clob.polymarket.com/ws/user` | Authenticated API credentials | Real-time personal order and trade lifecycle updates. |
| Sports WebSocket | `wss://sports-api.polymarket.com/ws` | Public | Live sports results, scores, periods, status. |
| RTDS | `wss://ws-live-data.polymarket.com` | Optional auth for some streams | Real-time comments, crypto prices, equity prices. |
| Official SDKs | `@polymarket/clob-client-v2 / py-clob-client-v2 / Rust SDK` | Depends on method | Preferred clients for CLOB V2 market data, order management, and auth. |

## 建议使用顺序

1. 市场发现/候选池：先用 Gamma `/markets`、`/events/keyset`，保留 `clobTokenIds`、`conditionId`、volume、rewards/enableOrderBook 字段。
2. 盘口和价差：用 CLOB `/book`、`/midpoint`、`/spread`、`/prices-history`，或 market WebSocket 订阅 token IDs。
3. 历史验证：用现有 `data/updown_cache/`、`polymarket_reward_markets.csv`、`paper_sim_results.csv`，不要直接覆盖；新抓取数据按日期另存。
4. 交易前门槛：先 dry-run/backtest，再 live preflight；交易和取消订单必须走 CLOB V2 SDK + L1/L2 auth，且私钥只放本地 `chmod 600` 的 env 文件。
5. 实时监控：盘口用 market WebSocket，个人订单/成交用 user WebSocket，体育状态用 sports WebSocket，评论/外部实时价格可用 RTDS。

## 官方资料

- Polymarket API Introduction: https://docs.polymarket.com/api-reference/introduction
- Quickstart: https://docs.polymarket.com/quickstart
- Authentication: https://docs.polymarket.com/api-reference/authentication
- Rate limits: https://docs.polymarket.com/api-reference/rate-limits
- WebSocket overview: https://docs.polymarket.com/market-data/websocket/overview
- CLOB orderbook: https://docs.polymarket.com/api-reference/market-data/get-order-book
- CLOB V2 migration: https://docs.polymarket.com/v2-migration


---

## Part B - 非 PM 策略交易资料

生成时间：2026-06-25T23:54:38 Asia/Shanghai。范围：排除 Polymarket/PM 相关目录与文件。

## 最高价值结论

- **Binance current gate**：当前 Binance Futures 账户读取返回 451 restricted location；不能确认账户仓位，不能做任何实盘测试。
- **Binance live signal**：2026-06-25 BCHUSDT/UNIUSDT/ETHUSDT 实时扫描：eligible_entry_count=0, live_eligible_entry_count=0，不下新单。
- **Binance 15m/90d ranking**：15m/90d refined 回测：BCHUSDT 第一，TRXUSDT 第二，UNIUSDT 第三；ETH/DOT/AVAX/NEAR/XRP/SOL/LINK 淘汰或降级。
- **Threshold gate**：研究扫描阈值 0.30；更严格实盘门槛建议 0.40；0.20 太松，0.50 待分批补跑。
- **Crypto risk research**：有独立 crypto_risk_research 框架：funding/open interest/liquidation/volume/volatility 特征，signal engine、paper executor、risk limits。
- **Mean reversion framework**：有通用事件驱动回测骨架：Strategy、NextBarOpenFillModel、RegimeDetector、RiskManager、PositionSizer、sample OHLCV。
- **Dune/Birdeye**：已有 Dune + Birdeye API kit，可用于链上聪明钱、token 价格/流动性、查询结果抓取。
- **Macro/CPI**：有 CPI 事件交易监控配置：TradingView + IBKR/TWS、ES/NQ/treasury/FX/ETF watchlist 和数据订阅清单。

## 主要资料根目录

- `/Users/m/Documents/Codex/2026-06-04/biance`
- `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research`
- `/Users/m/Documents/Codex/2026-06-10/8-30-cpi`
- `/Users/m/Documents/Codex/2026-06-10/ibkr-tws-mosaic-cpi-6-k`
- `/Users/m/Documents/Codex/2026-06-21/dune-birdeye`
- `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy`
- `/Users/m/Downloads/smartmoney_backtest_claudecode_prompt.md`
- `/Users/m/Downloads/M0_pit_price_panel_spec.md`

## 数据/结果类别汇总

| 类别 | 条目数 | 大小 | 说明 |
|---|---:|---:|---|
| `binance_backtest_table` | 7 | 99.9 KB | 多策略回测表格输出 |
| `binance_ohlcv_multi_cache` | 1 | 14.1 MB | Binance 多币种多周期 OHLCV CSV 缓存，15m/1h/4h/90d/180d 等 |
| `binance_ohlcv_single_cache` | 4 | 130.3 KB | 单币种 OHLCV 或 live/smoke CSV |
| `binance_result_json` | 48 | 182.0 KB | 策略参数、候选排名、live scan、模型/回测 JSON 输出 |
| `config_yaml` | 1 | 612 B | 配置文件 |
| `crypto_risk_config` | 3 | 583 B | crypto risk research 的 symbols/settings/risk limits 配置 |
| `dune_birdeye_sample_output` | 3 | 1.2 KB | Dune/Birdeye API 样例输出 |
| `json_data` | 8 | 37.9 KB | 其他 JSON |
| `macro_event_watchlist` | 1 | 566 B | CPI/IBKR 跨资产观察清单 |
| `mean_reversion_sample_data` | 1 | 377 B | 通用均值回归框架样例 OHLCV |

## 重点数据/结果文件

| 类别 | 路径 | 记录/文件数 | 字段/说明 |
|---|---|---:|---|
| `binance_backtest_table` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_15m_1000.csv` | 60 | symbol, interval, quote_risk_fraction, candles, start_utc, end_utc, buy_hold_return_pct, validation_return_pct, validation_max_drawdown_pct, validation_sharpe, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades, score, params |
| `binance_backtest_table` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_1h_1000.csv` | 60 | symbol, interval, quote_risk_fraction, candles, start_utc, end_utc, buy_hold_return_pct, validation_return_pct, validation_max_drawdown_pct, validation_sharpe, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades, score, params |
| `binance_backtest_table` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_1h_7d.csv` | 4 | symbol, interval, quote_risk_fraction, candles, start_utc, end_utc, buy_hold_return_pct, validation_return_pct, validation_max_drawdown_pct, validation_sharpe, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades, score, params |
| `binance_backtest_table` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_1h_90d.csv` | 60 | symbol, interval, quote_risk_fraction, candles, start_utc, end_utc, buy_hold_return_pct, validation_return_pct, validation_max_drawdown_pct, validation_sharpe, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades, score, params |
| `binance_backtest_table` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_1h_90d_mvd12_custom.csv` | 6 | symbol, interval, quote_risk_fraction, candles, start_utc, end_utc, buy_hold_return_pct, validation_return_pct, validation_max_drawdown_pct, validation_sharpe, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades, score, params |
| `binance_backtest_table` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_4h_1000.csv` | 60 | symbol, interval, quote_risk_fraction, candles, start_utc, end_utc, buy_hold_return_pct, validation_return_pct, validation_max_drawdown_pct, validation_sharpe, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades, score, params |
| `binance_backtest_table` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_4h_180d.csv` | 60 | symbol, interval, quote_risk_fraction, candles, start_utc, end_utc, buy_hold_return_pct, validation_return_pct, validation_max_drawdown_pct, validation_sharpe, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades, score, params |
| `binance_ohlcv_multi_cache` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/data/multi/` | 95 files | symbol/timeframe OHLCV CSV cache |
| `binance_ohlcv_single_cache` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/data/btcusdt_1h.csv` | 1000 | open_time, open, high, low, close, volume, close_time |
| `binance_ohlcv_single_cache` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/data/btcusdt_1h_500.csv` | 500 | open_time, open, high, low, close, volume, close_time |
| `binance_ohlcv_single_cache` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/data/smoke.csv` | 25 | open_time, open, high, low, close, volume, close_time |
| `binance_ohlcv_single_cache` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/data/trxusdt_4h_live.csv` | 300 | open_time, open, high, low, close, volume, close_time |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_model_15m_1000.json` | 1 object | symbol, interval, quote_risk_fraction, params, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_model_1h_1000.json` | 1 object | symbol, interval, quote_risk_fraction, params, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_model_1h_7d.json` | 1 object | symbol, interval, quote_risk_fraction, params, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_model_1h_90d.json` | 1 object | symbol, interval, quote_risk_fraction, params, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_model_1h_90d_mvd12_custom.json` | 1 object | symbol, interval, quote_risk_fraction, params, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_model_4h_1000.json` | 1 object | symbol, interval, quote_risk_fraction, params, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_model_4h_180d.json` | 1 object | symbol, interval, quote_risk_fraction, params, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_model_extended_samples.json` | 1 object | highest_return, more_robust |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_model_overall.json` | 1 object | symbol, interval, quote_risk_fraction, params, full_return_pct, full_max_drawdown_pct, full_sharpe, full_trades, search_space |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_params_btcusdt_1h.json` | 1 object | fast_ema, slow_ema, trend_sma, rsi_period, rsi_buy_max, rsi_sell_min, volatility_period, max_volatility, stop_loss_pct, take_profit_pct |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/best_params_btcusdt_1h_1000.json` | 1 object | fast_ema, slow_ema, trend_sma, rsi_period, rsi_buy_max, rsi_sell_min, volatility_period, max_volatility, stop_loss_pct, take_profit_pct |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/continue_key_candidates_scan_2026-06-07.json` | 1 object | mode, min_confidence, entry_count, eligible_entry_count, live_eligible_entry_count, long_entry_count, short_entry_count, live_eligible_opportunities, eligible_opportunities, opportunities, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/current_key_candidates_backtest_2026-06-25.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/current_key_candidates_scan_2026-06-25.json` | 1 object | mode, min_confidence, entry_count, eligible_entry_count, live_eligible_entry_count, long_entry_count, short_entry_count, live_eligible_opportunities, eligible_opportunities, opportunities, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/live_bch_strategy_scan.json` | 1 object | mode, min_confidence, entry_count, eligible_entry_count, long_entry_count, short_entry_count, eligible_opportunities, opportunities, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/live_multi_strategy_scan.json` | 1 object | mode, entry_count, long_entry_count, short_entry_count, opportunities, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/live_multi_strategy_scan_followup.json` | 1 object | mode, min_confidence, entry_count, eligible_entry_count, long_entry_count, short_entry_count, eligible_opportunities, opportunities, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/live_multi_strategy_scan_latest.json` | 1 object | mode, min_confidence, entry_count, eligible_entry_count, long_entry_count, short_entry_count, eligible_opportunities, opportunities, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/live_signal_scan.json` | 1 object | mode, tradable_count, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_ada_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_avax_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_backtest_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_bch_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_bnb_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_doge_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_dot_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_eth_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_link_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_ltc_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_near_1h_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_sol_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_uni_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_xrp_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/near_1h_active_params.json` | 1 object | fast_ema, slow_ema, trend_sma, rsi_period, rsi_buy_max, rsi_sell_min, volatility_period, max_volatility, stop_loss_pct, take_profit_pct |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/near_1h_high_return_params.json` | 1 object | fast_ema, slow_ema, trend_sma, rsi_period, rsi_buy_max, rsi_sell_min, volatility_period, max_volatility, stop_loss_pct, take_profit_pct |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/proxy_key_candidates_backtest_2026-06-07.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/proxy_key_candidates_scan_2026-06-07.json` | 1 object | mode, min_confidence, entry_count, eligible_entry_count, live_eligible_entry_count, long_entry_count, short_entry_count, live_eligible_opportunities, eligible_opportunities, opportunities, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/refined_all_15m_cache_backtest_2026-06-07.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/refined_key_candidates_live_scan.json` | 1 object | mode, min_confidence, entry_count, eligible_entry_count, long_entry_count, short_entry_count, eligible_opportunities, opportunities, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/refined_key_candidates_scan_2026-06-07.json` | 1 object | mode, min_confidence, entry_count, eligible_entry_count, long_entry_count, short_entry_count, eligible_opportunities, opportunities, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/refined_key_candidates_scan_safe_2026-06-07.json` | 1 object | mode, min_confidence, entry_count, eligible_entry_count, live_eligible_entry_count, long_entry_count, short_entry_count, live_eligible_opportunities, eligible_opportunities, opportunities, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/refined_strategy_bch_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/refined_strategy_eth_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/refined_strategy_key_candidates_2026-06-07.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/refined_strategy_key_candidates_90d_or_cache.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/refined_strategy_uni_15m_90d_conf030.json` | 1 object | mode, min_confidence, candidate_count, eligible_count, best, eligible, results |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/robust_model_analysis.json` | 1 object | filters, highest_return, constrained_return, robust |
| `binance_result_json` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/trx_futures_params.json` | 1 object | fast_ema, slow_ema, trend_sma, rsi_period, rsi_buy_max, rsi_sell_min, volatility_period, max_volatility, stop_loss_pct, take_profit_pct |
| `crypto_risk_config` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/config/risk_limits.yaml` | config |  |
| `crypto_risk_config` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/config/settings.yaml` | config |  |
| `crypto_risk_config` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/config/symbols.yaml` | config |  |
| `dune_birdeye_sample_output` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/out/birdeye_networks.json` | 1 object | data, success |
| `dune_birdeye_sample_output` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/out/birdeye_sol_price.json` | 1 object | data, success |
| `dune_birdeye_sample_output` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/out/dune_select_1.json` | 1 object | execution_id, is_execution_finished, state, submitted_at, expires_at, execution_started_at, execution_ended_at, result |
| `macro_event_watchlist` | `/Users/m/Documents/Codex/2026-06-10/ibkr-tws-mosaic-cpi-6-k/outputs/ibkr-cpi-watchlist.csv` | 11 | Symbol, Instrument Type, Preferred Route/Exchange, Use |
| `mean_reversion_sample_data` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/data/sample_ohlcv.csv` | 6 | timestamp, symbol, open, high, low, close, volume, funding_rate |

完整数据 CSV：`non_pm_strategy_data_inventory.csv`。

## API / 数据源

| 类型 | 地址 | 权限 | 用途 |
|---|---|---|---|
| Local proxy | `http://127.0.0.1:1082` | local | required proxy path observed for Binance access |
| Binance Spot/Public REST | `https://api.binance.com` | public for klines/ticker; signed for account/order | spot market data, account, order endpoints |
| Dune API | `https://api.dune.com/api/v1` | API key | SQL/query results for on-chain analytics |
| Binance public data mirror | `https://data-api.binance.vision` | public | historical/public klines fallback |
| Binance USD-M Futures REST | `https://fapi.binance.com` | public for ping/time/market; signed for account/order | futures market data, account/preflight, order endpoints |
| Binance USD-M Futures REST | `https://fapi.binance.com/fapi/v1/ping` | public for ping/time/market; signed for account/order | futures market data, account/preflight, order endpoints |
| Binance USD-M Futures REST | `https://fapi.binance.com/fapi/v1/time` | public for ping/time/market; signed for account/order | futures market data, account/preflight, order endpoints |
| Birdeye API | `https://public-api.birdeye.so` | API key | token price/liquidity/network data |
| Binance Spot Testnet | `https://testnet.binance.vision` | testnet keys | sandbox spot testing |
| Binance Futures Testnet | `https://testnet.binancefuture.com` | testnet keys for signed endpoints | paper/sandbox futures testing |
| IBKR docs/platform | `https://www.interactivebrokers.com/campus/trading-lessons/subscribing-to-data/` | account login/data subscription | TWS/data subscription setup |
| IBKR docs/platform | `https://www.interactivebrokers.com/en/pricing/market-data-pricing.php` | account login/data subscription | TWS/data subscription setup |
| IBKR docs/platform | `https://www.interactivebrokers.com/en/trading/download-tws.php` | account login/data subscription | TWS/data subscription setup |
| TradingView docs/app | `https://www.tradingview.com/data-coverage/` | account/subscription | charts and real-time market data setup |
| TradingView docs/app | `https://www.tradingview.com/desktop/` | account/subscription | charts and real-time market data setup |
| TradingView docs/app | `https://www.tradingview.com/support/solutions/43000471705-how-to-purchase-additional-market-data/` | account/subscription | charts and real-time market data setup |

完整 API CSV：`non_pm_strategy_api_inventory.csv`。

## 经验文档

| 类别 | 路径 | 标题/说明 |
|---|---|---|
| `coordination` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/CLAUDE.md` | 项目说明 for Codex |
| `coordination` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/.collab/board.md` | Collaboration Board |
| `coordination` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/.collab/decisions.md` | Decisions |
| `coordination` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/.collab/handoffs/claude.md` | Claude Code Handoff |
| `coordination` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/.collab/handoffs/codex.md` | Codex Handoff |
| `coordination` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/AGENTS.md` | AGENTS.md |
| `coordination` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/CLAUDE.md` | Codex + Claude Code Collaboration |
| `coordination` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit 2/CLAUDE.md` | Claude Code Handoff |
| `coordination` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/CLAUDE.md` | Claude Code Handoff |
| `coordination` | `/Users/m/Downloads/smartmoney_backtest_claudecode_prompt.md` | Claude Code Prompt — 链上聪明钱信号系统：规划 + 回测框架 |
| `doc` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/api_proxy_diagnosis_and_retest_2026-06-07.md` | API/代理诊断与重新回测 |
| `doc` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/backtest_improvement_summary.md` | 回测改进总结 |
| `doc` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/extended_sample_summary.md` | 扩展样本回测总结 |
| `doc` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_15m_1000.md` | 多币种回测报告 |
| `doc` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_1h_1000.md` | 多币种回测报告 |
| `doc` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_1h_7d.md` | 多币种回测报告 |
| `doc` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_1h_90d.md` | 多币种回测报告 |
| `doc` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_1h_90d_mvd12_custom.md` | 多币种回测报告 |
| `doc` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_4h_1000.md` | 多币种回测报告 |
| `doc` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_backtest_4h_180d.md` | 多币种回测报告 |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/CONTEXT.md` | CONTEXT.md |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/DECISIONS.md` | DECISIONS.md |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/TASKS.md` | TASKS.md |
| `doc` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/requirements.txt` | httpx>=0.27.0 |
| `doc` | `/Users/m/Documents/Codex/2026-06-10/8-30-cpi/outputs/cpi-watchlist-symbols.md` | CPI Watchlist Symbols |
| `doc` | `/Users/m/Documents/Codex/2026-06-10/ibkr-tws-mosaic-cpi-6-k/outputs/ibkr-cpi-reaction-screen.md` | IBKR TWS / Mosaic CPI Reaction Research Screen |
| `plan_spec_guide` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/binance_strategy_deployment_guide.md` | Binance 策略模型部署说明 |
| `plan_spec_guide` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/claude_guided_completion_2026-06-25.md` | CLAUDE.md 指导项执行报告 |
| `plan_spec_guide` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/futures_test_plan.md` | Futures 实盘测试准备 |
| `plan_spec_guide` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/profit_frequency_improvement_plan.md` | 收益与订单频率改进方案 |
| `plan_spec_guide` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/PROJECT_SPEC.md` | PROJECT_SPEC.md |
| `plan_spec_guide` | `/Users/m/Documents/Codex/2026-06-10/8-30-cpi/outputs/institutional-market-data-setup.md` | CPI Event Market Data Setup |
| `plan_spec_guide` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/BUILD_PLAN.md` | BUILD_PLAN.md - Institutional Mean-Reversion Strategy Execution Plan |
| `plan_spec_guide` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/INTEGRATION.md` | Phase 0 Integration |
| `plan_spec_guide` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/PROGRESS.md` | Progress |
| `plan_spec_guide` | `/Users/m/Downloads/M0_pit_price_panel_spec.md` | 里程碑 0 — Point-in-Time 价格面板 · 执行 Spec |
| `readme` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/README.md` | Binance Crypto Strategy Bot |
| `readme` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/README.md` | Crypto High-Risk Strategy Research System |
| `readme` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit 2/README.md` | Dune + Birdeye API Kit |
| `readme` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/README.md` | Dune + Birdeye API Kit |
| `readme` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/README.md` | Mean Reversion Strategy |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/backtest_analysis_improvement_2026-06-07.md` | 回测、分析、改进报告 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/backtest_analysis_improvement_decision.md` | 回测分析与改进决策 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/backtest_report_btcusdt_1h_1000.md` | BTCUSDT 1h 回测报告 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/continue_report_2026-06-07.md` | 继续跟进报告 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/current_situation_2026-06-25.md` | 当前情况分析 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/followup_status_2026-06-06.md` | 跟进状态报告 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/futures_readiness_report.md` | Futures 实盘测试就绪报告 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/live_trade_analysis.md` | 实盘测试分析与改进 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/live_trade_current_analysis.md` | 当前实盘测试分析 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_backtest_live_gate_report.md` | 多策略回测与 5 USDT 实盘接入判断 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/multi_strategy_short_learning_report.md` | 多策略与空单学习报告 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/refined_all_15m_90d_report_2026-06-25.md` | Refined 多策略 15m / 90 天全币种回测 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/reflection_refined_strategy_report.md` | 策略反思、改进与继续回测 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/robust_model_analysis.md` | 回测分析与改进排序 |
| `report_analysis` | `/Users/m/Documents/Codex/2026-06-04/biance/outputs/threshold_sensitivity_report_2026-06-25.md` | 阈值敏感性回测报告 |

完整文档 CSV：`non_pm_strategy_documents_inventory.csv`。

## 代码模块

| 类别 | 路径 | 大小 |
|---|---|---:|
| `api_client_data` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/binance_client.py` | 2.1 KB |
| `api_client_data` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/futures_client.py` | 7.5 KB |
| `api_client_data` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/market_data.py` | 4.6 KB |
| `api_client_data` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/data/binance_public_client.py` | 1.2 KB |
| `api_client_data` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/data/market_data_loader.py` | 276 B |
| `api_client_data` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit 2/dune_birdeye/client.py` | 8.3 KB |
| `api_client_data` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/dune_birdeye/client.py` | 8.3 KB |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/backtest.py` | 4.6 KB |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/multi_backtest.py` | 8.0 KB |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/multi_strategy_backtest.py` | 6.8 KB |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/backtest/__init__.py` | 81 B |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/backtest/cascade_backtester.py` | 254 B |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/backtest/event_backtester.py` | 175 B |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/backtest/metrics.py` | 311 B |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/scripts/run_trivial_backtest.py` | 2.3 KB |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/backtest/__init__.py` | 633 B |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/backtest/fill_model.py` | 1.5 KB |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/backtest/models.py` | 2.0 KB |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/backtest/runner.py` | 7.7 KB |
| `backtest_engine` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/backtest/strategy.py` | 614 B |
| `dune_birdeye_tooling` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit 2/dune_birdeye/__init__.py` | 111 B |
| `dune_birdeye_tooling` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit 2/dune_birdeye/cli.py` | 5.4 KB |
| `dune_birdeye_tooling` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit 2/pyproject.toml` | 356 B |
| `dune_birdeye_tooling` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit 2/scripts/setup_local.sh` | 331 B |
| `dune_birdeye_tooling` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit 2/scripts/verify_apis.sh` | 910 B |
| `dune_birdeye_tooling` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/dune_birdeye/__init__.py` | 111 B |
| `dune_birdeye_tooling` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/dune_birdeye/cli.py` | 5.4 KB |
| `dune_birdeye_tooling` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/pyproject.toml` | 356 B |
| `dune_birdeye_tooling` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/scripts/setup_local.sh` | 331 B |
| `dune_birdeye_tooling` | `/Users/m/Documents/Codex/2026-06-21/dune-birdeye/outputs/dune_birdeye_api_kit/scripts/verify_apis.sh` | 910 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/__init__.py` | 40 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/data/__init__.py` | 76 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/data/funding_loader.py` | 104 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/data/liquidation_loader.py` | 103 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/data/open_interest_loader.py` | 104 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/features/__init__.py` | 49 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/features/cascade_features.py` | 394 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/features/funding_features.py` | 252 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/features/oi_features.py` | 254 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/features/volatility_features.py` | 288 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/features/volume_features.py` | 584 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/main.py` | 1.1 KB |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/paper/__init__.py` | 68 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/paper/journal.py` | 493 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/paper/paper_executor.py` | 289 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/reports/__init__.py` | 33 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/reports/daily_report.py` | 378 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/risk/__init__.py` | 63 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/risk/kill_switch.py` | 463 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/risk/leverage_simulator.py` | 489 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/risk/liquidation_price.py` | 1010 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/risk/position_sizing.py` | 345 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/risk/risk_limits.py` | 1020 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/utils/__init__.py` | 23 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/utils/logger.py` | 133 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/utils/math_utils.py` | 216 B |
| `risk_sizing` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/utils/time_utils.py` | 154 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/fill_api_keys.sh` | 829 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/pyproject.toml` | 554 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/__init__.py` | 93 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/analyze_results.py` | 5.9 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/cli.py` | 34.6 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/config.py` | 2.6 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/indicators.py` | 2.2 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/multi_strategy.py` | 6.0 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/risk.py` | 4.1 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/strategy.py` | 2.7 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-04/biance/work/crypto_strategy_bot/src/crypto_strategy_bot/trader.py` | 2.3 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/signals/__init__.py` | 97 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/signals/altcoin_momentum_signal.py` | 494 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/signals/funding_extreme_signal.py` | 475 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/signals/liquidation_cascade_signal.py` | 497 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/signals/signal_engine.py` | 883 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/strategy/__init__.py` | 62 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/strategy/entry_rules.py` | 241 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/strategy/exit_rules.py` | 269 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/strategy/no_trade_rules.py` | 291 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/src/strategy/trade_decision.py` | 347 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/pyproject.toml` | 314 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/__init__.py` | 72 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/config/__init__.py` | 168 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/config/schema.py` | 2.8 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/data/__init__.py` | 95 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/data/loader.py` | 1.1 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/examples/__init__.py` | 55 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/examples/trivial_strategy.py` | 2.0 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/regime/__init__.py` | 158 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/regime/detector.py` | 3.7 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/risk/__init__.py` | 154 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/risk/manager.py` | 4.0 KB |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/sizing/__init__.py` | 116 B |
| `strategy_signal` | `/Users/m/Documents/Codex/2026-06-23/build-plan-md-phase-0-integration/outputs/mean-reversion-strategy/src/mean_reversion_strategy/sizing/sizer.py` | 4.5 KB |
| `tests` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/tests/test_binance_public_client.py` | 413 B |
| `tests` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/tests/test_feature_smoke.py` | 502 B |
| `tests` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/tests/test_leverage_simulator.py` | 395 B |
| `tests` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/tests/test_liquidation_price.py` | 488 B |
| `tests` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/tests/test_research_module_smoke.py` | 2.4 KB |
| `tests` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/tests/test_risk_limits.py` | 503 B |
| `tests` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/tests/test_signal_engine.py` | 725 B |
| `tests` | `/Users/m/Documents/Codex/2026-06-07/files-mentioned-by-the-user-txt-3/crypto_risk_research/tests/test_volume_features.py` | 342 B |

完整代码 CSV：`non_pm_strategy_code_inventory.csv`。

## 使用顺序建议

1. **先看 Binance 当前状态**：`current_situation_2026-06-25.md`、`refined_all_15m_90d_report_2026-06-25.md`、`threshold_sensitivity_report_2026-06-25.md`。
2. **研究回测**：用 `work/crypto_strategy_bot` 和 outputs JSON/CSV，不要把 cache-only 结果当 live gate。
3. **风险信号扩展**：把 `crypto_risk_research` 的 funding/OI/liquidation/volume 特征作为二级过滤器。
4. **链上数据**：用 Dune/Birdeye kit 做聪明钱、token liquidity、wallet/holder 查询；API key 只放本地 env。
5. **通用框架**：需要新策略时用 mean-reversion 项目的事件驱动回测骨架，保持 next-bar fill/no-lookahead。
6. **宏观事件**：CPI/IBKR/TradingView 资料只用于观察和记录；任何实盘仍要账户权限、数据订阅和人工确认。

## 安全边界

- 没有输出任何 `.env`、API key、private key、secret 的内容。
- Binance live 目前仍被 `451 restricted location` 和无实时合格信号挡住。
- 真正下单前必须满足：账户读取成功、仓位确认、live_eligible_opportunities 来源为 live public/signed path、5 USDT 小额门槛明确。

