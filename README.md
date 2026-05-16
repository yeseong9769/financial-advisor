# Financial Advisor — OpenCode Multi-Agent System

AI-powered financial assistant for individual investors. Provides portfolio analysis, market data retrieval, and asset rebalancing recommendations.

## Quick Install

```bash
git clone https://github.com/yeseong9769/financial-advisor.git
cd financial-advisor
bash install.sh
```

Installation supports global (`~/.config/opencode/`) or project (`.opencode/`) targets.

### Global Install (Recommended)
```bash
bash install.sh -g
```
Available in all projects via `@finance-advisor`.

### Project Install
```bash
cd my-portfolio-project
bash /path/to/financial-advisor/install.sh -p
```
Only available in the current project.

## Prerequisites

- [OpenCode](https://opencode.ai) installed
- Python 3.x

## Usage

```bash
opencode
```
```
Analyze my portfolio
Suggest asset rebalancing
Show me AAPL current price
@stock-analyzer Deep dive on TSLA
```

## Features

| Task | Agent | Mode |
|------|-------|------|
| Portfolio statistics / Rebalancing | `@portfolio-manager` | Basic / Deep |
| Market data (raw) | `@market-researcher` | — |
| Stock overview | `@stock-analyzer` | Basic |
| Stock deep-dive / DCF / PDF | `@stock-analyzer` | Deep |

## Architecture

```
financial-advisor/
├── install.sh              ← Install script
├── AGENTS.md               ← Development rules
├── opencode.json.example   ← Config template (MCP not required)
├── requirements.txt        ← Python dependencies (yfinance, openpyxl)
├── agents/                 ← OpenCode agent definitions
│   ├── finance-advisor.md  ← Primary orchestrator
│   ├── market-researcher.md
│   ├── portfolio-manager.md
│   └── stock-analyzer.md
└── skills/financial-analyst/
    ├── SKILL.md
    └── scripts/
        ├── market_data_fetcher.py  ← Data engine (yfinance)
        ├── dcf_valuation.py
        └── ratio_calculator.py
```

## License

MIT
