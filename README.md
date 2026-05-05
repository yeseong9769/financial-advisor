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
- Alpha Vantage API key ([get one free](https://www.alphavantage.co/support/#api-key))
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

| Task | Agent |
|------|-------|
| Portfolio statistics | `@portfolio-analyzer` |
| Market data/research | `@market-researcher` |
| Rebalancing | `@rebalancing-engine` |
| Stock deep-dive / PDF | `@stock-analyzer` |

## Architecture

```
financial-advisor/
├── install.sh              ← Install script
├── AGENTS.md               ← Development rules
├── opencode.json.example   ← MCP config template
├── requirements.txt        ← Python dependencies (openpyxl)
├── agents/                 ← OpenCode agent definitions
│   ├── finance-advisor.md
│   ├── portfolio-analyzer.md
│   ├── market-researcher.md
│   ├── rebalancing-engine.md
│   └── stock-analyzer.md
└── skills/financial-analyst/
    ├── SKILL.md
    └── scripts/
        ├── ratio_calculator.py
        ├── dcf_valuation.py
        ├── rebalancing_calculator.py
        └── portfolio_metrics.py
```

## License

MIT
