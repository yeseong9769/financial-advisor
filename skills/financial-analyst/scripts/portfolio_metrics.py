#!/usr/bin/env python3
"""
Portfolio Metrics Calculator

Calculates portfolio-level metrics: allocation, returns, concentration,
and performance ranking. Pure Python (no numpy/pandas).

Usage:
    python portfolio_metrics.py portfolio.json
    python portfolio_metrics.py --stdin
    python portfolio_metrics.py --stdin --format json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator


class PortfolioMetrics:

    def __init__(self, data: Dict[str, Any]) -> None:
        self.assets: List[Dict[str, Any]] = data.get("assets", [])
        self.total_value: float = 0.0
        self.metrics: Dict[str, Any] = {}

    def validate(self) -> None:
        if not self.assets:
            raise ValueError("Portfolio must have at least one asset")
        for i, a in enumerate(self.assets):
            if "symbol" not in a:
                raise ValueError(f"Asset at index {i} missing 'symbol'")

    def calculate_total_value(self) -> float:
        self.total_value = 0.0
        for a in self.assets:
            value = a.get("current_value", 0)
            if value == 0:
                value = a.get("current_price", 0) * a.get("quantity", 0)
            a["_value"] = value
            self.total_value += value
        return self.total_value

    def calculate_allocation_by_asset(self) -> List[Dict[str, Any]]:
        result = []
        for a in self.assets:
            weight = safe_divide(a["_value"], self.total_value) * 100
            result.append({
                "symbol": a["symbol"],
                "value": round(a["_value"], 2),
                "weight_pct": round(weight, 2),
            })
        result.sort(key=lambda x: x["weight_pct"], reverse=True)
        return result

    def calculate_allocation_by_group(self, key: str) -> List[Dict[str, Any]]:
        groups: Dict[str, float] = {}
        for a in self.assets:
            group = a.get(key, "unknown")
            groups[group] = groups.get(group, 0) + a["_value"]
        result = []
        for group, value in sorted(groups.items(), key=lambda x: x[1], reverse=True):
            weight = safe_divide(value, self.total_value) * 100
            result.append({
                "group": group,
                "value": round(value, 2),
                "weight_pct": round(weight, 2),
            })
        return result

    def calculate_returns(self) -> Tuple[List[Dict[str, Any]], float, float]:
        returns = []
        total_pnl = 0.0
        total_cost = 0.0
        for a in self.assets:
            cost = a.get("cost_basis", 0)
            if cost == 0:
                purchase_price = a.get("purchase_price", 0)
                quantity = a.get("quantity", 0)
                cost = purchase_price * quantity
            current = a["_value"]
            pnl = current - cost
            total_pnl += pnl
            total_cost += cost
            ret_pct = safe_divide(pnl, cost) * 100
            returns.append({
                "symbol": a["symbol"],
                "cost_basis": round(cost, 2),
                "current_value": round(current, 2),
                "pnl": round(pnl, 2),
                "return_pct": round(ret_pct, 2),
            })
        returns.sort(key=lambda x: x["return_pct"], reverse=True)
        weighted_avg_return = safe_divide(total_pnl, total_cost) * 100 if total_cost > 0 else 0.0
        return returns, round(total_pnl, 2), round(weighted_avg_return, 2)

    def calculate_concentration(self) -> Dict[str, Any]:
        weights = [safe_divide(a["_value"], self.total_value) for a in self.assets]
        hhi = sum(w * w * 10000 for w in weights)
        by_value = sorted(self.assets, key=lambda a: a["_value"], reverse=True)
        top3_weight = sum(safe_divide(a["_value"], self.total_value) for a in by_value[:3]) * 100
        return {
            "hhi": round(hhi, 2),
            "hhi_label": "highly concentrated" if hhi > 2500 else "moderately concentrated" if hhi > 1500 else "well diversified",
            "top_3_weight_pct": round(top3_weight, 2),
            "num_assets": len(self.assets),
        }

    def run_all(self) -> Dict[str, Any]:
        self.validate()
        self.calculate_total_value()

        allocation = self.calculate_allocation_by_asset()
        by_class = self.calculate_allocation_by_group("asset_class")
        by_sector = self.calculate_allocation_by_group("sector")
        returns, total_pnl, weighted_return = self.calculate_returns()
        concentration = self.calculate_concentration()

        return {
            "total_value": round(self.total_value, 2),
            "allocation": allocation,
            "allocation_by_class": by_class,
            "allocation_by_sector": by_sector,
            "returns": {
                "per_asset": returns,
                "total_unrealized_pnl": total_pnl,
                "weighted_avg_return_pct": weighted_return,
            },
            "concentration": concentration,
        }

    def format_text(self, results: Dict[str, Any]) -> str:
        lines: List[str] = []
        lines.append("=" * 70)
        lines.append("PORTFOLIO METRICS")
        lines.append("=" * 70)

        lines.append(f"\nTotal Portfolio Value: ${results['total_value']:,.2f}")

        lines.append(f"\n--- ALLOCATION BY ASSET ---")
        lines.append(f"  {'Symbol':<8} {'Value':>12} {'Weight':>8}")
        lines.append(f"  " + "-" * 30)
        for a in results["allocation"]:
            lines.append(f"  {a['symbol']:<8} ${a['value']:>10,.2f} {a['weight_pct']:>7.1f}%")

        if results["allocation_by_class"]:
            lines.append(f"\n--- ALLOCATION BY ASSET CLASS ---")
            for g in results["allocation_by_class"]:
                lines.append(f"  {g['group']:<15} ${g['value']:>10,.2f}  {g['weight_pct']:>5.1f}%")

        if results["allocation_by_sector"]:
            lines.append(f"\n--- ALLOCATION BY SECTOR ---")
            for g in results["allocation_by_sector"]:
                lines.append(f"  {g['group']:<20} ${g['value']:>10,.2f}  {g['weight_pct']:>5.1f}%")

        ret = results["returns"]
        lines.append(f"\n--- RETURNS ---")
        lines.append(f"  Weighted Avg Return: {ret['weighted_avg_return_pct']:.2f}%")
        lines.append(f"  Total Unrealized P&L: ${ret['total_unrealized_pnl']:,.2f}")

        lines.append(f"\n  {'Symbol':<8} {'Return':>8} {'P&L':>12}")
        lines.append(f"  " + "-" * 30)
        for a in ret["per_asset"]:
            sign = "+" if a["return_pct"] >= 0 else ""
            lines.append(f"  {a['symbol']:<8} {sign}{a['return_pct']:>7.2f}% ${a['pnl']:>10,.2f}")

        conc = results["concentration"]
        lines.append(f"\n--- CONCENTRATION ---")
        lines.append(f"  HHI: {conc['hhi']:.0f} ({conc['hhi_label']})")
        lines.append(f"  Top 3 Weight: {conc['top_3_weight_pct']:.1f}%")
        lines.append(f"  Total Assets: {conc['num_assets']}")

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Portfolio Metrics Calculator")
    parser.add_argument("input_file", nargs="?", help="Path to JSON file")
    parser.add_argument("--stdin", action="store_true", help="Read JSON from stdin")
    parser.add_argument("--format", choices=["text", "json"], default="text")

    args = parser.parse_args()

    try:
        if args.stdin:
            data = json.load(sys.stdin)
        elif args.input_file:
            with open(args.input_file, "r") as f:
                data = json.load(f)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    calculator = PortfolioMetrics(data)
    try:
        results = calculator.run_all()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(calculator.format_text(results))


if __name__ == "__main__":
    main()
