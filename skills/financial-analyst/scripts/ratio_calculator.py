#!/usr/bin/env python3
"""
Financial Ratio Calculator

Calculates and interprets financial ratios across 5 categories:
profitability, liquidity, leverage, efficiency, and valuation.

Usage:
    python ratio_calculator.py financial_data.json
    python ratio_calculator.py financial_data.json --format json
    python ratio_calculator.py financial_data.json --category profitability
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple

# Import constants from config module
try:
    from config import BENCHMARKS
except ImportError:
    # Fallback if config not available (standalone execution)
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


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator


def validate_input(data: Dict[str, Any]) -> List[str]:
    """Validate input data and return list of warnings."""
    warnings = []
    
    income = data.get("income_statement", {})
    balance = data.get("balance_sheet", {})
    
    # Check for required fields
    if not income.get("revenue"):
        warnings.append("Revenue data missing - profitability ratios will be incomplete")
    
    if not balance.get("total_equity"):
        warnings.append("Total equity missing - ROE cannot be calculated")
    
    if not balance.get("total_assets"):
        warnings.append("Total assets missing - ROA cannot be calculated")
    
    # Check for negative values that might indicate data issues
    if income.get("revenue", 0) < 0:
        warnings.append("Negative revenue detected - check data source")
    
    if balance.get("total_equity", 0) < 0:
        warnings.append("Negative equity detected - company may be insolvent")
    
    return warnings


class FinancialRatioCalculator:

    def __init__(self, data: Dict[str, Any]) -> None:
        self.income = data.get("income_statement", {})
        self.balance = data.get("balance_sheet", {})
        self.cash_flow = data.get("cash_flow", {})
        self.market = data.get("market_data", {})
        self.results: Dict[str, Dict[str, Any]] = {}

    def calculate_profitability(self) -> Dict[str, Any]:
        revenue = self.income.get("revenue", 0)
        cogs = self.income.get("cost_of_goods_sold", 0)
        operating_income = self.income.get("operating_income", 0)
        net_income = self.income.get("net_income", 0)
        total_equity = self.balance.get("total_equity", 0)
        total_assets = self.balance.get("total_assets", 0)

        gross_profit = revenue - cogs

        ratios = {
            "roe": {
                "value": safe_divide(net_income, total_equity),
                "formula": "Net Income / Total Equity",
                "name": "Return on Equity",
            },
            "roa": {
                "value": safe_divide(net_income, total_assets),
                "formula": "Net Income / Total Assets",
                "name": "Return on Assets",
            },
            "gross_margin": {
                "value": safe_divide(gross_profit, revenue),
                "formula": "(Revenue - COGS) / Revenue",
                "name": "Gross Margin",
            },
            "operating_margin": {
                "value": safe_divide(operating_income, revenue),
                "formula": "Operating Income / Revenue",
                "name": "Operating Margin",
            },
            "net_margin": {
                "value": safe_divide(net_income, revenue),
                "formula": "Net Income / Revenue",
                "name": "Net Margin",
            },
        }

        for key, ratio in ratios.items():
            ratio["interpretation"] = self.interpret_ratio(key, ratio["value"])

        self.results["profitability"] = ratios
        return ratios

    def calculate_liquidity(self) -> Dict[str, Any]:
        current_assets = self.balance.get("current_assets", 0)
        current_liabilities = self.balance.get("current_liabilities", 0)
        inventory = self.balance.get("inventory", 0)
        cash = self.balance.get("cash_and_equivalents", 0)

        ratios = {
            "current_ratio": {
                "value": safe_divide(current_assets, current_liabilities),
                "formula": "Current Assets / Current Liabilities",
                "name": "Current Ratio",
            },
            "quick_ratio": {
                "value": safe_divide(
                    current_assets - inventory, current_liabilities
                ),
                "formula": "(Current Assets - Inventory) / Current Liabilities",
                "name": "Quick Ratio",
            },
            "cash_ratio": {
                "value": safe_divide(cash, current_liabilities),
                "formula": "Cash & Equivalents / Current Liabilities",
                "name": "Cash Ratio",
            },
        }

        for key, ratio in ratios.items():
            ratio["interpretation"] = self.interpret_ratio(key, ratio["value"])

        self.results["liquidity"] = ratios
        return ratios

    def calculate_leverage(self) -> Dict[str, Any]:
        total_debt = self.balance.get("total_debt", 0)
        total_equity = self.balance.get("total_equity", 0)
        operating_income = self.income.get("operating_income", 0)
        interest_expense = self.income.get("interest_expense", 0)
        operating_cash_flow = self.cash_flow.get("operating_cash_flow", 0)
        total_debt_service = self.cash_flow.get(
            "total_debt_service", interest_expense
        )

        ratios = {
            "debt_to_equity": {
                "value": safe_divide(total_debt, total_equity),
                "formula": "Total Debt / Total Equity",
                "name": "Debt-to-Equity Ratio",
            },
            "interest_coverage": {
                "value": safe_divide(operating_income, interest_expense),
                "formula": "Operating Income / Interest Expense",
                "name": "Interest Coverage Ratio",
            },
            "dscr": {
                "value": safe_divide(operating_cash_flow, total_debt_service),
                "formula": "Operating Cash Flow / Total Debt Service",
                "name": "Debt Service Coverage Ratio",
            },
        }

        for key, ratio in ratios.items():
            ratio["interpretation"] = self.interpret_ratio(key, ratio["value"])

        self.results["leverage"] = ratios
        return ratios

    def calculate_efficiency(self) -> Dict[str, Any]:
        revenue = self.income.get("revenue", 0)
        cogs = self.income.get("cost_of_goods_sold", 0)
        total_assets = self.balance.get("total_assets", 0)
        inventory = self.balance.get("inventory", 0)
        accounts_receivable = self.balance.get("accounts_receivable", 0)

        receivables_turnover_val = safe_divide(revenue, accounts_receivable)

        ratios = {
            "asset_turnover": {
                "value": safe_divide(revenue, total_assets),
                "formula": "Revenue / Total Assets",
                "name": "Asset Turnover",
            },
            "inventory_turnover": {
                "value": safe_divide(cogs, inventory),
                "formula": "COGS / Inventory",
                "name": "Inventory Turnover",
            },
            "receivables_turnover": {
                "value": receivables_turnover_val,
                "formula": "Revenue / Accounts Receivable",
                "name": "Receivables Turnover",
            },
            "dso": {
                "value": safe_divide(365, receivables_turnover_val)
                if receivables_turnover_val > 0
                else 0.0,
                "formula": "365 / Receivables Turnover",
                "name": "Days Sales Outstanding",
            },
        }

        for key, ratio in ratios.items():
            ratio["interpretation"] = self.interpret_ratio(key, ratio["value"])

        self.results["efficiency"] = ratios
        return ratios

    def calculate_valuation(self) -> Dict[str, Any]:
        market_cap = self.market.get("market_cap", 0)
        share_price = self.market.get("share_price", 0)
        shares_outstanding = self.market.get("shares_outstanding", 0)
        earnings_growth_rate = self.market.get("earnings_growth_rate", 0)

        net_income = self.income.get("net_income", 0)
        revenue = self.income.get("revenue", 0)
        total_equity = self.balance.get("total_equity", 0)
        total_debt = self.balance.get("total_debt", 0)
        cash = self.balance.get("cash_and_equivalents", 0)
        ebitda = self.income.get("ebitda", 0)

        if market_cap == 0 and share_price > 0 and shares_outstanding > 0:
            market_cap = share_price * shares_outstanding

        eps = safe_divide(net_income, shares_outstanding)
        book_value_per_share = safe_divide(total_equity, shares_outstanding)
        enterprise_value = market_cap + total_debt - cash
        pe = safe_divide(share_price, eps)

        ratios = {
            "pe_ratio": {
                "value": pe,
                "formula": "Share Price / Earnings Per Share",
                "name": "Price-to-Earnings Ratio",
            },
            "pb_ratio": {
                "value": safe_divide(share_price, book_value_per_share),
                "formula": "Share Price / Book Value Per Share",
                "name": "Price-to-Book Ratio",
            },
            "ps_ratio": {
                "value": safe_divide(
                    market_cap, revenue
                ),
                "formula": "Market Cap / Revenue",
                "name": "Price-to-Sales Ratio",
            },
            "ev_ebitda": {
                "value": safe_divide(enterprise_value, ebitda),
                "formula": "Enterprise Value / EBITDA",
                "name": "EV/EBITDA",
            },
            "peg_ratio": {
                "value": safe_divide(pe, earnings_growth_rate * 100)
                if earnings_growth_rate > 0
                else 0.0,
                "formula": "P/E Ratio / Earnings Growth Rate (%)",
                "name": "PEG Ratio",
            },
        }

        for key, ratio in ratios.items():
            ratio["interpretation"] = self.interpret_ratio(key, ratio["value"])

        self.results["valuation"] = ratios
        return ratios

    def calculate_all(self) -> Dict[str, Dict[str, Any]]:
        self.calculate_profitability()
        self.calculate_liquidity()
        self.calculate_leverage()
        self.calculate_efficiency()
        self.calculate_valuation()
        return self.results

    def interpret_ratio(self, ratio_key: str, value: float) -> str:
        if value == 0.0:
            return "Insufficient data to calculate"

        benchmarks = BENCHMARKS.get(ratio_key)
        if not benchmarks:
            return "No benchmark available"

        low, typical, high = benchmarks

        # Valuation ratios: lower is better
        valuation_ratios = {"pe_ratio", "pb_ratio", "ps_ratio", "ev_ebitda", "peg_ratio"}
        if ratio_key in valuation_ratios:
            if value <= low:
                return "Excellent - undervalued or attractive"
            elif value <= typical:
                return "Good - reasonable valuation"
            elif value <= high:
                return "Acceptable - fairly valued"
            else:
                return "Concern - potentially overvalued"

        # DSO (Days Sales Outstanding): lower is better
        if ratio_key == "dso":
            if value <= low:
                return "Excellent - collections well above average"
            elif value <= typical:
                return "Good - collections within normal range"
            elif value <= high:
                return "Acceptable - monitor collection trends"
            else:
                return "Concern - collections significantly slower than peers"

        # Debt-to-Equity: lower is better (conservative leverage)
        if ratio_key == "debt_to_equity":
            if value <= low:
                return "Conservative leverage - strong equity position"
            elif value <= typical:
                return "Moderate leverage - well balanced"
            elif value <= high:
                return "Elevated leverage - monitor debt levels"
            else:
                return "High leverage - potential financial risk"

        # Default: higher is better (profitability, liquidity, efficiency ratios)
        if value < low:
            return "Below average - needs improvement"
        elif value <= typical:
            return "Acceptable - within normal range"
        elif value <= high:
            return "Good - above average performance"
        else:
            return "Excellent - significantly above peers"

    @staticmethod
    def format_ratio(value: float, is_percentage: bool = False) -> str:
        if is_percentage:
            return f"{value * 100:.1f}%"
        return f"{value:.2f}"

    def format_text(self, category: Optional[str] = None) -> str:
        lines: List[str] = []
        lines.append("=" * 70)
        lines.append("FINANCIAL RATIO ANALYSIS")
        lines.append("=" * 70)

        categories = (
            {category: self.results[category]}
            if category and category in self.results
            else self.results
        )

        percentage_ratios = {
            "roe", "roa", "gross_margin", "operating_margin", "net_margin"
        }

        for cat_name, ratios in categories.items():
            lines.append(f"\n--- {cat_name.upper()} ---")
            for key, ratio in ratios.items():
                is_pct = key in percentage_ratios
                formatted = self.format_ratio(ratio["value"], is_pct)
                lines.append(f"  {ratio['name']}: {formatted}")
                lines.append(f"    Formula: {ratio['formula']}")
                lines.append(f"    Assessment: {ratio['interpretation']}")

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)

    def to_json(self, category: Optional[str] = None) -> Dict[str, Any]:
        if category and category in self.results:
            return {"category": category, "ratios": self.results[category]}
        return {"categories": self.results}


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate and interpret financial ratios")
    parser.add_argument("input_file", nargs="?", help="Path to JSON file")
    parser.add_argument("--stdin", action="store_true", help="Read JSON from stdin")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--category", choices=["profitability", "liquidity", "leverage", "efficiency", "valuation"], default=None)

    args = parser.parse_args()

    try:
        if args.stdin:
            data = json.load(sys.stdin)
        else:
            with open(args.input_file, "r") as f:
                data = json.load(f)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate input and show warnings
    warnings = validate_input(data)
    if warnings and args.format == "text":
        print("\n--- WARNINGS ---", file=sys.stderr)
        for warning in warnings:
            print(f"  ! {warning}", file=sys.stderr)
        print("", file=sys.stderr)

    calculator = FinancialRatioCalculator(data)

    if args.category:
        method_map = {
            "profitability": calculator.calculate_profitability,
            "liquidity": calculator.calculate_liquidity,
            "leverage": calculator.calculate_leverage,
            "efficiency": calculator.calculate_efficiency,
            "valuation": calculator.calculate_valuation,
        }
        method_map[args.category]()
    else:
        calculator.calculate_all()

    if args.format == "json":
        output = calculator.to_json(args.category)
        if warnings:
            output["warnings"] = warnings
        print(json.dumps(output, indent=2))
    else:
        print(calculator.format_text(args.category))


if __name__ == "__main__":
    main()