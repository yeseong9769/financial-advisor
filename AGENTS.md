# AGENTS.md — Financial Advisor

## Project Type

OpenCode multi-agent system for investment portfolio analysis. No build, no tests, no package manager — just agent definitions, Python analysis scripts, and an MCP config.

## Entry Points

- **Primary agent**: `agents/finance-advisor.md` — orchestrates other agents, handles user-facing questions
- **Subagents**: `agents/portfolio-analyzer.md`, `agents/market-researcher.md`, `agents/rebalancing-engine.md`, `agents/stock-analyzer.md`
- **Skill**: `skills/financial-analyst/SKILL.md` — financial modeling toolkit with Python scripts
- **Config**: `opencode.json` — registers Alpha Vantage MCP server

## MCP Dependency

Alpha Vantage MCP is pre-configured in `opencode.json`. Agents that do market data or stock analysis **must call `alphavantage*` tools directly** — they are listed as `true` in `tools:` front matter for a reason. The server is remote; do not attempt to install it. Example: `TIME_SERIES_DAILY` with `{"symbol": "AAPL", "outputsize": "compact"}`.

## Skills

Only one skill: `financial-analyst`. Load with `skill(name="financial-analyst")`. It bundles 5 pure-standard-library Python scripts in `skills/financial-analyst/scripts/`:
- `ratio_calculator.py`
- `dcf_valuation.py`
- `budget_variance_analyzer.py`
- `forecast_builder.py`
- `rebalancing_calculator.py`

All scripts use **Python standard library only** — no numpy, pandas, scipy, etc. Don’t assume you can `pip install` extras.

## File & Output Conventions

- **Default: print to screen only.** Do not write intermediate files to disk.
- **PDF only on explicit request** (keywords: "PDF로", "PDF 생성", "리포트 파일로", "인쇄용").
- PDF workflow: generate in `/tmp/`, convert with `pandoc` + `xelatex`, move to `reports/` (or `/mnt/samba/Documents/Investment/reports/`), clean up `/tmp/`.
- Temporary data: keep in memory or `/tmp/`, delete after use.

## Common Paths

- Portfolio Excel example: `/mnt/samba/Documents/Investment/자산현황.xlsx`
- PDF output: `/mnt/samba/Documents/Investment/reports/[종목명]_분석_[날짜].pdf`

## When to Delegate

Follow the agent routing defined in the primary agent:
- Portfolio stats → `@portfolio-analyzer`
- Market data/research → `@market-researcher`
- Rebalancing → `@rebalancing-engine`
- Individual stock deep-dive or PDF report → `@stock-analyzer`

## Language

User-facing output is **Korean** for most agents; internal reasoning and analysis summaries can remain in English unless the user context is Korean.
