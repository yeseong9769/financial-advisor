# Financial Advisor — OpenCode Skill-Backed Agent

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
@finance-advisor Analyze my portfolio
@finance-advisor Suggest asset rebalancing
@finance-advisor Show me AAPL current price
@finance-advisor Deep dive on TSLA
```

## Features

| Task | Mode |
|------|------|
| Current price / quote | Basic |
| Portfolio statistics | Basic |
| Stock overview | Basic |
| Full portfolio analysis / Rebalancing | Deep |
| Stock deep-dive / DCF / PDF | Deep |

## Architecture

```
financial-advisor/
├── install.sh              ← Install script
├── AGENTS.md               ← Development rules
├── opencode.json.example   ← Config template (MCP not required)
├── requirements.txt        ← Python dependencies (yfinance, openpyxl)
├── agents/                 ← OpenCode agent definition
│   └── finance-advisor.md  ← Single agent
└── skills/
    ├── financial-analyst/
    │   ├── SKILL.md        ← Analysis guides + tool definitions
    │   └── scripts/
    │       ├── market_data_fetcher.py  ← Data engine (yfinance)
    │       ├── dcf_valuation.py
    │       └── ratio_calculator.py
    └── pdf-report/
        ├── SKILL.md
        └── scripts/
            └── html_to_pdf.py
```

## License

MIT
