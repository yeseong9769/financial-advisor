---
name: financial-analyst
description: Complete financial analysis guide and Python calculation scripts for investment analysis
license: MIT
compatibility: opencode
metadata:
  audience: financial analysts
  category: finance
  purpose: investment analysis
  version: 5.0
---

# Financial Analyst Skill

LLM drives analysis and judgment; scripts are used for precision calculations only.

**Data Fidelity (summarized from `finance-advisor` agent):**
- All numerical market data must come from `market_data_fetcher.py`. Do not use memorized or web-scraped figures for current metrics.
- Cross-check `quote.price` vs `overview.regularMarketPrice` (±5%) and `quote.peRatio` vs `overview.trailingPE` (±10%). Flag discrepancies.
- Beware of suspicious zeros: `revenueGrowth: 0.0`, `profitMargins: 0.0` etc. are often yfinance defaults for missing data, not actual zeros.
- State source and timestamp for every numerical figure. If data is missing, say so explicitly rather than substituting.

All script paths below are relative to the OpenCode working directory (project root).

## Tools

### 1. Market Data Fetcher (`scripts/market_data_fetcher.py`)
Fetches market data via yfinance engine (no API key needed). Supports quote, overview, income, balance, cashflow, daily, and news endpoints with file-based caching.

```bash
echo '{"symbol": "AAPL", "endpoint": "quote"}' | python skills/financial-analyst/scripts/market_data_fetcher.py --stdin
echo '{"symbol": "AAPL", "endpoint": "overview"}' | python skills/financial-analyst/scripts/market_data_fetcher.py --stdin
```

**Cache TTL:**
| Endpoint | TTL | Description |
|----------|-----|-------------|
| `quote` | 5 min | Current price, change, volume |
| `daily` | 1 hour | Daily OHLCV time series |
| `overview` | 1 day | Company fundamentals |
| `income` | 1 day | Income statement |
| `balance` | 1 day | Balance sheet |
| `cashflow` | 1 day | Cash flow statement |
| `news` | 30 min | News articles |

**Features:**
- yfinance data engine — no API key needed, no rate limiting
- File-based caching in `~/.cache/financial-advisor/`

**Instructions for LLM:**
1. Fetch only the data requested — do not fetch additional data beyond what was asked
2. Return raw API response — do not interpret, summarize, or add commentary during the data fetch step
3. Format for clarity — if response is verbose, trim to relevant fields only
4. No analysis during fetch — interpretation is done in the analysis step

### 2. Ratio Calculator (`scripts/ratio_calculator.py`)
Financial ratio calculation (profitability, liquidity, leverage, efficiency, valuation) with benchmark-based interpretation.

```bash
echo '{"income_statement": {...}, "balance_sheet": {...}, "cash_flow": {...}, "market_data": {...}}' | python skills/financial-analyst/scripts/ratio_calculator.py --stdin
```

### 3. DCF Valuation (`scripts/dcf_valuation.py`)
Discounted Cash Flow enterprise valuation with WACC, terminal value, and 2-way sensitivity analysis.

```bash
echo '{"historical": {...}, "assumptions": {...}}' | python skills/financial-analyst/scripts/dcf_valuation.py --stdin
```

## Analysis Guides

### Stock Analysis (Basic)

**When triggered:**
- "삼성전자 어때?", "AAPL 현재가", "종목 분석해줘"
- Any stock query without Deep keywords

**Data to fetch:**
```bash
echo '{"symbol": "AAPL", "endpoint": "quote"}' | python skills/financial-analyst/scripts/market_data_fetcher.py --stdin
echo '{"symbol": "AAPL", "endpoint": "overview"}' | python skills/financial-analyst/scripts/market_data_fetcher.py --stdin
```

**Analysis:**
- LLM calculates: P/E relative to 20 (typical), dividend yield relative to 2% (typical)
- No external scripts needed
- Return 3-4 bullet points

**Output format:**
```
[{Symbol} Overview]
- Price: $XXX (+X.X% today)
- Market Cap: $XB
- P/E: XX (vs typical 20 = [high/low/fair])
- Dividend: X.X%
- Quick take: [2-3 sentence assessment]
```

### Stock Deep Dive / DCF (Deep)

**When triggered:**
- "심층 분석", "자세한 분석", "DCF", "밸류에이션", "리포트"
- User explicitly asks for comprehensive analysis

**Data to fetch:**
```bash
echo '{"symbol": "AAPL", "endpoint": "overview"}' | python skills/financial-analyst/scripts/market_data_fetcher.py --stdin
echo '{"symbol": "AAPL", "endpoint": "income"}' | python skills/financial-analyst/scripts/market_data_fetcher.py --stdin
echo '{"symbol": "AAPL", "endpoint": "balance"}' | python skills/financial-analyst/scripts/market_data_fetcher.py --stdin
echo '{"symbol": "AAPL", "endpoint": "cashflow"}' | python skills/financial-analyst/scripts/market_data_fetcher.py --stdin
```

**Analysis steps:**
1. Run DCF valuation with scenarios using `dcf_valuation.py --stdin`:
   - Define 3 explicit scenarios in the JSON input
   - Base: current trajectory with reasonable assumptions
   - Bull: revenue growth +3~5pp, terminal multiple +2~3x, WACC -1%
   - Bear: revenue growth -3~5pp, terminal multiple -2~3x, WACC +1%
   - Document each assumption change explicitly
2. Calculate key ratios using `ratio_calculator.py --stdin`
3. Compare to sector averages
4. Generate sensitivity table analysis (Base scenario only)

**DCF Input format (multi-scenario):**
```json
{
  "historical": {
    "revenue": [100, 110, 121, 133],
    "net_debt": 50,
    "shares_outstanding": 1000
  },
  "assumptions": {
    "projection_years": 5,
    "scenarios": {
      "base": {
        "revenue_growth_rates": [0.10, 0.08, 0.07, 0.06, 0.05],
        "fcf_margins": [0.12, 0.13, 0.14, 0.14, 0.15],
        "wacc_inputs": {
          "risk_free_rate": 0.04,
          "equity_risk_premium": 0.06,
          "beta": 1.2,
          "cost_of_debt": 0.05,
          "tax_rate": 0.25,
          "debt_weight": 0.30,
          "equity_weight": 0.70
        },
        "terminal_growth_rate": 0.025,
        "exit_ev_ebitda_multiple": 12.0
      },
      "bull": {
        "revenue_growth_rates": [0.15, 0.12, 0.10, 0.08, 0.06],
        "fcf_margins": [0.15, 0.16, 0.17, 0.17, 0.18],
        "wacc_inputs": {
          "risk_free_rate": 0.04,
          "equity_risk_premium": 0.06,
          "beta": 1.1,
          "cost_of_debt": 0.05,
          "tax_rate": 0.25,
          "debt_weight": 0.25,
          "equity_weight": 0.75
        },
        "terminal_growth_rate": 0.03,
        "exit_ev_ebitda_multiple": 15.0
      },
      "bear": {
        "revenue_growth_rates": [0.05, 0.03, 0.02, 0.01, 0.00],
        "fcf_margins": [0.10, 0.09, 0.08, 0.08, 0.07],
        "wacc_inputs": {
          "risk_free_rate": 0.04,
          "equity_risk_premium": 0.06,
          "beta": 1.4,
          "cost_of_debt": 0.06,
          "tax_rate": 0.25,
          "debt_weight": 0.40,
          "equity_weight": 0.60
        },
        "terminal_growth_rate": 0.015,
        "exit_ev_ebitda_multiple": 9.0
      }
    }
  }
}
```

Legacy single-scenario format (without `scenarios` key) is still fully supported.

**Output format (Deep):**
```
[{Symbol} Deep Analysis]

1. Valuation (DCF — Scenario Comparison)
   - Base:  $XXX/share (Exit) | $XXX/share (Perp)
   - Bull:  $XXX/share (Exit) | $XXX/share (Perp)
   - Bear:  $XXX/share (Exit) | $XXX/share (Perp)
   - Current price: $XXX → [Overvalued/Undervalued/Fair] relative to Base
   - Sensitivity range (Base only): $XXX (best) ~ $XXX (worst)

2. Key Metrics
   - ROE: X.X%, ROA: X.X%
   - Gross Margin: X.X%, Net Margin: X.X%
   - Debt/Equity: X.X, Interest Coverage: X.Xx

3. Summary
   - [2-3 sentence investment thesis]
```

### Portfolio Analysis (Basic)

**When triggered:**
- "내 포폴 보여줘", "포트폴리오 분석해줘", "비중 확인해줘"
- Simple allocation/return queries

**Analysis steps:**
1. Parse user Excel/CSV file (openpyxl/csv)
2. Calculate directly (no external scripts):
   - Total value = sum of all asset values
   - Allocation % = asset_value / total_value × 100
   - Returns % = (current_value - cost_basis) / cost_basis × 100
   - Weighted avg return = sum(return_pct × weight) / 100
   - HHI = sum(weight²) × 10000
   - Top 3 concentration = sum of top 3 asset weights
3. Return concise summary (3-5 bullet points max)

**Output format (Basic):**
```
[Portfolio Summary]
- Total: $XXX,XXX
- Top holdings: AAPL 25%, MSFT 18%, GOOGL 12%
- Returns: +X.X% (weighted avg)
- Concentration: HHI XXXX (label)
- [Optional] Sector breakdown if relevant
```

### Portfolio Rebalancing (Deep)

**When triggered:**
- "리밸런싱 해줘", "리밸런싱 분석해줘", "포트폴리오 평가"
- Keywords: 상세, 심층, 분석, 평가, 세금, 세무, 시나리오

**Analysis steps:**
1. Load portfolio data (same as Basic)
2. Calculate current allocation + target allocation based on user's goal/risk profile
3. Calculate trades needed:
   - trade_amount = target_weight × total_value - current_value
   - transaction_cost = sum(|trade_amounts|) × 0.001
   - turnover_rate = total_trade_volume / total_value
4. Generate 2-3 rebalancing scenarios (conservative/balanced/aggressive)
5. Apply Korean tax rules by default (adjust for non-Korean users upon request):
   - Capital gains tax: 22% on annual gains exceeding KRW 2,500,000
   - Dividend withholding: 15.4%
   - Check ISA account eligibility
   - Loss offsetting: net losses can offset gains in same year
6. Apply Tax-Aware Rebalancing Rules (execution priority):
   - **Priority 1**: Rebalance in tax-advantaged accounts first (ISA, pension) — no tax consequences
   - **Priority 2**: In taxable accounts, avoid selling positions with unrealized short-term gains (< 1 year)
   - **Priority 3**: Harvest tax losses where possible while rebalancing (offset gains)
   - **Priority 4**: Consider directing new cash contributions to underweight assets instead of selling winners
   - **Wash sale rule**: Avoid repurchasing same/similar security within 30 days of loss harvesting
7. Present trade recommendations with pros/cons

**Output format (Deep):**
```
[Rebalancing Recommendation]

Scenario A (Conservative):
- Trade: SELL X / BUY Y
- Cost: $XXX
- Tax impact: $XXX saved
- Pros: ...
- Cons: ...

Scenario B (Balanced): ...
Scenario C (Aggressive): ...

Recommendation: [Best option] with reasoning
```

## Principles
- All scripts are stdin/stdout based (no file creation)
- LLM performs most analysis directly; scripts handle complex calculations (DCF, multi-ratio analysis)
- Simple calculations (allocation %, returns, HHI) are handled directly by LLM
- No economic context gathering in Basic mode
- DCF assumptions: document them clearly (WACC, terminal growth, projection period)
