---
name: financial-analyst
description: Collection of Python calculation scripts for financial analysis
license: MIT
compatibility: opencode
metadata:
  audience: financial analysts
  category: finance
  purpose: investment analysis
  version: 4.0
---

# Financial Analyst Skill

LLM drives analysis and judgment; scripts are used for precision calculations only.

## Tools

### 1. Ratio Calculator (`scripts/ratio_calculator.py`)
Financial ratio calculation (profitability, liquidity, leverage, efficiency, valuation) with benchmark-based interpretation.

```bash
echo '{"income_statement": {...}, "balance_sheet": {...}, "cash_flow": {...}, "market_data": {...}}' | python scripts/ratio_calculator.py --stdin
```

### 2. DCF Valuation (`scripts/dcf_valuation.py`)
Discounted Cash Flow enterprise valuation with WACC, terminal value, and 2-way sensitivity analysis.

```bash
echo '{"historical": {...}, "assumptions": {...}}' | python scripts/dcf_valuation.py --stdin
```

## Principles
- All scripts are stdin/stdout based (no file creation)
- LLM performs most analysis directly; scripts handle complex calculations (DCF, multi-ratio analysis)
- Simple calculations (allocation %, returns, HHI) are handled directly by LLM agents