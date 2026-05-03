# AGENTS.md — Financial Advisor

## Project Type

OpenCode multi-agent system (config only, no build/test). 5 agents + 1 skill + 4 Python scripts + 1 install script.

## Key Architecture

- This repo is the **source** for agents/skills. `install.sh` copies them to the user's OpenCode config.
- `opencode.json` is gitignored. Use `opencode.json.example` as template.
- Agents live in `agents/` (dev source). Skills live in `skills/financial-analyst/`.
- Install targets: `~/.config/opencode/` (global) or `.opencode/` (project-local).

## Installation / Distribution

- `install.sh -g` — global install to `~/.config/opencode/`
- `install.sh -p` — project install to `$(pwd)/.opencode/`
- `add_mcp_config()` in install.sh merges Alpha Vantage MCP into existing `opencode.json` without overwriting other config.
- Requirements: `pip install -r requirements.txt` (openpyxl for Excel; CSV-only users can skip).

## Alpha Vantage MCP

- Calls go through `alphavantage_TOOL_LIST` / `_GET` / `_CALL`. Do NOT call raw HTTP.
- API key: shell env var `ALPHAVANTAGE_API_KEY`, referenced as `{env:ALPHAVANTAGE_API_KEY}` in `opencode.json`.
- Key must NOT be hardcoded in any file.
- Remote URL: `https://mcp.alphavantage.co/mcp?apikey={env:ALPHAVANTAGE_API_KEY}`

## Agent Conventions

- Primary: `finance-advisor` (orchestrator). Subagents: `portfolio-analyzer`, `market-researcher`, `rebalancing-engine`, `stock-analyzer`.
- Agents are LLM-driven — Python scripts are precision calculators, NOT the core logic.
- Subagents have `edit: false, write: false` (read-only). Only primary agent can write files.
- User-facing output: **Korean**. Code/output/comments: **English**.

## Design Philosophy

- **Token efficiency first**: Minimize intermediate steps. LLM analyzes raw API responses directly instead of piping through Python scripts (e.g., `NEWS_SENTIMENT` → LLM reasoning, not `NEWS_SENTIMENT` → script → LLM).
- **Scripts are calculators, not business logic**: Python scripts handle deterministic math (ratios, DCF, rebalancing). Economic judgment, sentiment analysis, and investment recommendations are LLM-driven.
- **Economic context before analysis**: `@finance-advisor` must gather current economic conditions from `@market-researcher` before DCF valuation, ratio analysis, or rebalancing. Assumptions (WACC, growth rates) are adjusted based on the macro environment.
- **No intermediate files**: All scripts use `--stdin` and stdout only. No temp files or disk writes.
- **Config over code**: This repo contains agent/skill definitions and calculation scripts. No build step, no tests, no CI. Install via `install.sh`.

## Economic Environment & News

- `@market-researcher` fetches news via Alpha Vantage `NEWS_SENTIMENT` API.
- The market-researcher **analyzes the raw API response directly with LLM**. No intermediate Python script is involved.
- This direct analysis minimizes token usage.
- `@finance-advisor` must request an economic context summary **before** specialized analysis (DCF, rebalancing, ratios) to ensure recommendations reflect current conditions.
- Based on the summary (e.g., rate hikes, high inflation), `@finance-advisor` adjusts assumptions like WACC or terminal growth rate.

## Python Scripts (skills/financial-analyst/scripts/)

All support `--stdin` for pipe input. Never write intermediate files to disk.

| Script | Purpose |
|--------|---------|
| `ratio_calculator.py` | Financial ratios (profitability, liquidity, leverage, efficiency, valuation) |
| `dcf_valuation.py` | DCF valuation with WACC, terminal value, sensitivity analysis |
| `rebalancing_calculator.py` | Rebalancing trade math (simple method only, no numpy) |
| `portfolio_metrics.py` | Portfolio-level return, allocation, and concentration analysis |

## Data Input

- No fixed paths. User provides file path conversationally during opencode session.
- Formats: Excel (.xlsx via openpyxl), CSV (standard library).
- Load skill: `skill(name="financial-analyst")`

## PDF Reports

- Only on explicit user request (keywords: "PDF report", "generate PDF", etc.)
- Workflow: `/tmp/report.md` → `pandoc` + `xelatex` → `$PWD/filename.pdf` → cleanup `/tmp/`
