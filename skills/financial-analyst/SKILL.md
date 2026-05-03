---
name: financial-analyst
description: Collection of Python calculation scripts for portfolio analysis
license: MIT
compatibility: opencode
metadata:
  audience: financial analysts
  category: finance
  purpose: investment portfolio analysis
  version: 3.0
---

# Financial Analyst Skill

LLM drives analysis and judgment; scripts are used only when precision calculations are needed.

## Tools

### 1. Ratio Calculator (`scripts/ratio_calculator.py`)
Financial ratio calculation. stdin input → stdout output.

```bash
echo '{"income_statement": {...}, "balance_sheet": {...}}' | python scripts/ratio_calculator.py --stdin
```

### 2. DCF Valuation (`scripts/dcf_valuation.py`)
DCF enterprise valuation + sensitivity analysis.

```bash
echo '{"historical_data": {...}, "assumptions": {...}}' | python scripts/dcf_valuation.py --stdin
```

### 3. Rebalancing Calculator (`scripts/rebalancing_calculator.py`)
Rebalancing precision calculation.

```bash
echo '{"assets": [...], "target_weights": {...}}' | python scripts/rebalancing_calculator.py --stdin
```

### 4. Portfolio Metrics (`scripts/portfolio_metrics.py`)
Portfolio-level return, allocation, and concentration analysis.

```bash
echo '{"assets": [...], "cost_basis": ...}' | python scripts/portfolio_metrics.py --stdin
```

## Principles
- All scripts are stdin/stdout based (no file creation)
- LLM performs most analysis directly; scripts are supplementary tools
