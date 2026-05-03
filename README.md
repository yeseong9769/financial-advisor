# Financial Advisor — OpenCode Multi-Agent System

A personal investment portfolio analysis agent powered by OpenCode. Provides portfolio analysis, market research, and rebalancing recommendations using Excel/CSV portfolio data and Alpha Vantage market data.

## Architecture

```
financial-advisor/
├── AGENTS.md                    ← Project rules & conventions
├── opencode.json.example        ← MCP config template
├── .gitignore                   ← excludes opencode.json, xlsx, pdf
├── agents/
│   ├── finance-advisor.md       ← Primary agent (orchestrator)
│   ├── portfolio-analyzer.md    ← Subagent: asset analysis & ratios
│   ├── market-researcher.md     ← Subagent: real-time market data
│   ├── rebalancing-engine.md    ← Subagent: LLM-driven rebalancing
│   └── stock-analyzer.md        ← Subagent: individual stock deep-dive
└── skills/financial-analyst/
    ├── SKILL.md                 ← Financial modeling toolkit
    ├── scripts/                  ← Python analysis scripts
    ├── references/               ← Industry guides & methodologies
    └── assets/                   ← Templates & sample data
```

## Prerequisites

- [OpenCode](https://opencode.ai) installed
- Alpha Vantage API key ([get one free](https://www.alphavantage.co/support/#api-key))
- Python 3.x (for optional skill scripts)

## Quick Start

### 1. Set up environment variable

```bash
export ALPHAVANTAGE_API_KEY="your_api_key_here"
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

### 2. Copy MCP configuration

```bash
cp opencode.json.example opencode.json
```

### 3. Run OpenCode

```bash
cd /path/to/your/portfolio/files
opencode
```

### 4. Start using it

Drop your portfolio Excel file into the working directory and ask:

```
포트폴리오 분석해줘
자산 재배분 제안해줘
AAPL 현재가 알려줘
```

## Features

### Portfolio Analysis (→ `@portfolio-analyzer`)
- Read Excel/CSV portfolio data
- Calculate allocations, P&L, ROI
- Performance metrics and risk assessment

### Market Research (→ `@market-researcher`)
- Real-time stock prices (Alpha Vantage MCP)
- Technical indicators (RSI, MACD, Bollinger Bands)
- News sentiment and economic data

### Rebalancing (→ `@rebalancing-engine`)
- LLM-driven: understands user goals, risk tolerance, and market context
- Korean tax considerations (capital gains tax, dividend tax)
- Multi-option recommendations with tradeoff analysis
- Calculator script for precise numbers when needed

### Stock Analysis (→ `@stock-analyzer`)
- Company fundamentals (financial statements, ratios)
- Technology and competitive position assessment
- PDF report generation on request

## Configuration

The only configuration file is `opencode.json` (generated from `opencode.json.example`). It configures the Alpha Vantage MCP server:

```json
{
  "mcp": {
    "alphavantage": {
      "type": "remote",
      "url": "https://mcp.alphavantage.co/mcp?apikey={env:ALPHAVANTAGE_API_KEY}"
    }
  }
}
```

> `opencode.json` is excluded from Git via `.gitignore`. Use `opencode.json.example` as a template.

## Data Input

Portfolio data is provided as Excel (.xlsx, .xls) or CSV files. The agent reads files from the current working directory — no fixed path is assumed. Simply tell the agent the file path during conversation:

```
포트폴리오 파일이 여기 있습니다: ./내_포트폴리오.xlsx
```

## Skills

Load the financial-analyst skill when needed:

```
skill(name="financial-analyst")
```

Available scripts:

| Script | Purpose |
|--------|---------|
| `ratio_calculator.py` | Financial ratio calculation |
| `dcf_valuation.py` | DCF company valuation |
| `budget_variance_analyzer.py` | Budget variance analysis |
| `forecast_builder.py` | Revenue/cash flow forecasting |
| `rebalancing_calculator.py` | Portfolio rebalancing (stdin/file) |

## Agent Routing

| Task | Agent |
|------|-------|
| Portfolio statistics | `@portfolio-analyzer` |
| Market data/research | `@market-researcher` |
| Rebalancing | `@rebalancing-engine` |
| Stock deep-dive / PDF | `@stock-analyzer` |

## Language

User-facing output is in Korean. Internal analysis can be in English.

## License

MIT
