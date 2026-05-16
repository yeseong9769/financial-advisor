# AGENTS.md — Financial Advisor

## Project Type

OpenCode multi-agent system config. No build/test pipeline. Changes to `agents/*.md` and `scripts/*.py` take effect after `install.sh` copies them to the target OpenCode config directory.

## Architecture

This repo is the **source** for agents/skills. `install.sh` copies them to the user's OpenCode config (`~/.config/opencode/` or `./.opencode/`).

**4 agents** (defined in `agents/*.md` with YAML front matter):

| Agent | Role | Mode |
|-------|------|------|
| `finance-advisor.md` | Orchestrator. Routes queries to subagents. Simple quotes delegated to `@market-researcher`. | — |
| `market-researcher.md` | **Raw data fetch only** via yfinance engine. Returns data with zero interpretation/summarization. | — |
| `portfolio-manager.md` | Portfolio allocation, returns, concentration, rebalancing. Basic (summary) vs Deep (scenarios + Korean tax). | basic/deep |
| `stock-analyzer.md` | Stock overview. Basic (price + 4 metrics) vs Deep (DCF + ratio calc + optional PDF). | basic/deep |

**3 Python scripts** (`skills/financial-analyst/scripts/`), stdin/stdout only:

| Script | Used When |
|--------|-----------|
| `market_data_fetcher.py` | **All market data fetching** via yfinance. Caching + no rate limits. |
| `dcf_valuation.py` | Deep stock analysis. DCF enterprise valuation + WACC + 2-way sensitivity (5×5 table). |
| `ratio_calculator.py` | Deep stock analysis. 20 financial ratios + benchmark-based interpretation. |

**Deleted** (no longer exist): `portfolio-analyzer.md`, `rebalancing-engine.md`, `portfolio_metrics.py`, `rebalancing_calculator.py`.

## Design Decisions

- **Basic vs Deep split**: `/finance-advisor.md` triggers Deep mode on keywords like "자세히", "심층", "분석", "리밸런싱", "DCF", "PDF". Default is Basic (3-5 bullet points, fast).
- **Raw data fetcher**: `market-researcher` does not analyze. It returns trimmed API responses. The caller (`finance-advisor` or `stock-analyzer`) decides what to do with the data.
- **No script for simple math**: Allocation %, HHI, rebalancing trade amounts — agents calculate directly. Scripts are only for complex multi-step calculations (DCF 5-year projection, 20-ratio analysis).
- **Economic context OFF by default**: `finance-advisor` skips `@market-researcher` for news sentiment unless Deep mode specifically benefits from it (e.g. DCF WACC adjustment, rebalancing in volatile markets).

## Orchestrator Pattern

`finance-advisor` follows the official OpenCode orchestrator pattern:

**Permissions (enforced delegation):**
```yaml
permission:
  read: allow      # Routing decisions
  edit: deny       # Implementation → @fixer
  bash: deny       # Commands → @fixer
  write: deny      # File creation → @fixer
  glob: allow      # File discovery
  grep: allow      # Pattern search
  task: allow      # Subagent delegation (no MCP — data via @market-researcher)
```

**Delegation rules:**
| Task | Handler | Reason |
|------|---------|--------|
| Simple price query | `@market-researcher` | Fast data fetch |
| Portfolio analysis | `@portfolio-manager` | Complex calculation |
| Stock deep dive | `@stock-analyzer` | DCF + ratios |
| File edits | `@fixer` | Implementation |
| Code/scripts | `@fixer` | Implementation |

## Data Fetching & Caching

All market data goes through `market_data_fetcher.py`:

**Data engine:** yfinance (Python library) — no API key, no rate limits.

**Cache TTL by endpoint:**
| Endpoint | TTL | Use Case |
|----------|-----|----------|
| `quote` | 5 min | Current price, change, volume |
| `daily` | 1 hour | Daily OHLCV time series |
| `overview` | 1 day | Company fundamentals |
| `income`/`balance`/`cashflow` | 1 day | Financial statements |
| `news` | 30 min | News sentiment |

**Cache location:** `~/.cache/financial-advisor/`

## Korean Tax Default

`portfolio-manager` Deep mode applies Korean tax rules by default:
- Capital gains tax: 22% on annual gains exceeding KRW 2.5M basic deduction
- Dividend withholding: 15.4%
- ISA account tax-exempt benefits, loss offsetting

Adjust for non-Korean users when requested.

## Setup

```bash
# Install to global OpenCode config (~/.config/opencode/)
bash install.sh -g

# Install Python deps (yfinance + openpyxl)
pip install -r requirements.txt
```

No API key required. `opencode.json` is gitignored. Minimal stub at `opencode.json.example` (MCP not required).

## Script Conventions

All scripts accept `--stdin` and write to stdout. No temp files.
- Input: JSON via stdin
- Output: Text or JSON via `--format json`

## Style (Tightly Applied)

- Simplicity first: scripts are calculators, not frameworks. No abstractions for single-use code.
- Surgical changes: match the exact existing style. Do not "improve" adjacent code.
- Goal-driven: define success criteria explicitly before analysis. Verify outputs at each step.

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

## Validation Examples

### DCF Edge Cases

**Case 1: WACC <= Terminal Growth Rate**
```
Input: WACC 0.03, terminal_growth 0.04
Expected: Perpetuity method disabled, Exit multiple method only
Output contains: "Warning: WACC (3.00%) <= terminal growth rate (4.00%). Perpetuity method disabled."
```

**Case 2: Zero Historical Revenue**
```
Input: historical.revenue = []
Expected: ValueError("Historical revenue data is required")
```

**Case 3: Negative FCF in All Years**
```
Input: fcf_margins = [-0.05, -0.03, -0.01, 0.01, 0.03]
Expected: Valid calculation, negative enterprise value possible
Note: Document clearly if all scenarios negative
```

### Ratio Calculator Edge Cases

**Case 1: Zero Denominator**
```
Input: total_equity = 0
Expected: ROE = 0.0 (safe_divide returns default)
Interpretation: "Insufficient data to calculate"
```

**Case 2: Missing Optional Fields**
```
Input: income_statement without "ebitda" field
Expected: EV/EBITDA = 0.0, interpretation "Insufficient data"
```

### Portfolio Calculation Checks

**Sanity Check 1: Allocation Sum**
```
Verify: sum(allocation_percentages) ≈ 100% (±0.1% tolerance)
If not: Check for missing assets or data parsing error
```

**Sanity Check 2: HHI Range**
```
HHI should be: 100 (equal weight) to 10000 (single asset)
If HHI > 5000: Flag as "Extreme concentration"
If HHI < 500: Flag as "Over-diversified"
```
