# AGENTS.md — Financial Advisor

## Project Type

OpenCode multi-agent system (config only, no build/test).

## Key Architecture

- **Source repo**: This repo is the source for agents/skills. `install.sh` copies them to the user's OpenCode config.
- **Directory layout**:
  - `agents/` — Primary agent (`finance-advisor.md`) and subagents (portfolio-analyzer, market-researcher, rebalancing-engine, stock-analyzer)
  - `skills/financial-analyst/` — Python calculation scripts (`scripts/*.py`) and `SKILL.md`
  - `install.sh` — Installation script
- **Config**: `opencode.json` is gitignored. Use `opencode.json.example` as template.

## Installation / Development Setup

- **Global install**: `bash install.sh -g` (installs to `~/.config/opencode/`)
- **Project install**: `bash install.sh -p` (installs to `$(pwd)/.opencode/`)
- **Python deps**: `pip install -r requirements.txt` (openpyxl; CSV-only users can skip)
- **Alpha Vantage API key**: Set `ALPHAVANTAGE_API_KEY` env var before use.

## Agent Definitions

Each agent is defined in `agents/*.md` with YAML front matter:

```yaml
---
description: Agent description
mode: primary|subagent
temperature: 0.1
permission:
  read: allow
  edit: deny|allow
  write: deny|allow
  bash: allow
  alphavantage*: allow
---
```

**Key agents**:
- `finance-advisor.md` — Primary orchestrator (can write files)
- `portfolio-analyzer.md` — Reads Excel/CSV, calculates portfolio metrics
- `market-researcher.md` — Fetches Alpha Vantage data, analyzes economic news
- `rebalancing-engine.md` — Generates rebalancing recommendations
- `stock-analyzer.md` — Deep-dive stock analysis, optional PDF generation

## Python Scripts

All scripts are located in `skills/financial-analyst/scripts/` and support `--stdin`:

| Script | Purpose |
|--------|---------|
| `ratio_calculator.py` | Financial ratios (profitability, liquidity, leverage, efficiency, valuation) |
| `dcf_valuation.py` | DCF valuation with WACC, terminal value, sensitivity analysis |
| `rebalancing_calculator.py` | Rebalancing trade math (simple method only, no numpy) |
| `portfolio_metrics.py` | Portfolio-level return, allocation, and concentration analysis |

**Script conventions**:
- All scripts use `--stdin` and stdout only (no temp files)
- Input format: JSON via stdin
- Output format: Text or JSON (use `--format json`)

## Development Guidelines (Andrej Karpathy Principles)

Source: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)

### 1. Think Before Coding
- **State assumptions explicitly**: In financial analysis, clearly state assumptions like "Assuming 10% revenue growth based on historical trends".
- **Stop when confused**: If API responses are unclear, pause and ask for clarification.

### 2. Simplicity First
- **No features beyond what was asked**: Don't add extra financial metrics unless requested.
- **No abstractions for single-use code**: Python scripts are simple calculators, not frameworks.

### 3. Surgical Changes
- **Don't "improve" adjacent code**: Match existing style exactly.
- **Don't refactor things that aren't broken**: Only modify code directly related to the current task.

### 4. Goal-Driven Execution
- **Define success criteria**: Transform "Analyze portfolio" → "Calculate allocation, returns, and concentration, then present findings".
- **Verify each step**: For multi-step tasks, verify outputs before proceeding.
