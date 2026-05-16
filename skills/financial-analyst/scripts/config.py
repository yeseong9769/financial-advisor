#!/usr/bin/env python3
"""
Configuration constants for financial analysis scripts.
Simple constants file - no classes, no logic.
"""
# NOTE: When updating defaults below, also update fallback values in:
# - dcf_valuation.py (lines 32-37)
# - ratio_calculator.py (lines 24-45)

# Korean Tax Rules (default)
KOREAN_CAPITAL_GAINS_TAX_RATE = 0.22
KOREAN_CAPITAL_GAINS_BASIC_DEDUCTION = 2_500_000  # KRW
KOREAN_DIVIDEND_WITHHOLDING_RATE = 0.154

# DCF Defaults
DEFAULT_WACC = 0.10
DEFAULT_TERMINAL_GROWTH_RATE = 0.025
DEFAULT_PROJECTION_YEARS = 5
DEFAULT_EXIT_EV_EBITDA_MULTIPLE = 12.0
DEFAULT_EBITDA_MARGIN = 0.20

# Ratio Benchmarks (low, typical, high)
BENCHMARKS = {
    "roe": (0.08, 0.15, 0.25),
    "roa": (0.03, 0.06, 0.12),
    "gross_margin": (0.25, 0.40, 0.60),
    "operating_margin": (0.05, 0.15, 0.25),
    "net_margin": (0.03, 0.10, 0.20),
    "current_ratio": (1.0, 1.5, 3.0),
    "quick_ratio": (0.8, 1.0, 2.0),
    "cash_ratio": (0.2, 0.5, 1.0),
    "debt_to_equity": (0.3, 0.8, 2.0),
    "interest_coverage": (2.0, 5.0, 10.0),
    "dscr": (1.0, 1.5, 2.5),
    "asset_turnover": (0.5, 1.0, 2.0),
    "inventory_turnover": (4.0, 8.0, 12.0),
    "receivables_turnover": (6.0, 10.0, 15.0),
    "dso": (30.0, 45.0, 60.0),
    "pe_ratio": (10.0, 20.0, 35.0),
    "pb_ratio": (1.0, 2.5, 5.0),
    "ps_ratio": (1.0, 3.0, 8.0),
    "ev_ebitda": (6.0, 12.0, 20.0),
    "peg_ratio": (0.5, 1.0, 2.0),
}

# Validation Thresholds
MAX_DCF_PRICE_DEVIATION = 10.0  # DCF result vs current price (multiple)
MAX_REBALANCING_COST_RATIO = 0.10  # Transaction cost / expected benefit
MIN_DATA_POINTS_FOR_DCF = 3  # Minimum historical revenue years
