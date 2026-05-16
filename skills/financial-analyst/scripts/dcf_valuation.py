#!/usr/bin/env python3
"""
DCF Valuation Model

Discounted Cash Flow enterprise and equity valuation with WACC calculation,
terminal value estimation, and two-way sensitivity analysis.

Uses standard library only (math, statistics) - NO numpy/pandas/scipy.

Usage:
    python dcf_valuation.py valuation_data.json
    python dcf_valuation.py valuation_data.json --format json
    python dcf_valuation.py valuation_data.json --projection-years 7
"""

import argparse
import json
import math
import sys
from typing import Any, Dict, List, Optional, Tuple

# Import constants from config module
try:
    from config import (
        DEFAULT_WACC,
        DEFAULT_TERMINAL_GROWTH_RATE,
        DEFAULT_PROJECTION_YEARS,
        DEFAULT_EXIT_EV_EBITDA_MULTIPLE,
        DEFAULT_EBITDA_MARGIN,
    )
except ImportError:
    # Fallback if config not available (standalone execution)
    DEFAULT_WACC = 0.10
    DEFAULT_TERMINAL_GROWTH_RATE = 0.025
    DEFAULT_PROJECTION_YEARS = 5
    DEFAULT_EXIT_EV_EBITDA_MULTIPLE = 12.0
    DEFAULT_EBITDA_MARGIN = 0.20


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator


def _fmt_money(val: Optional[float]) -> str:
    if val is None:
        return "N/A (WACC <= growth)"
    if math.isnan(val) or math.isinf(val):
        return "N/A (Invalid calculation)"
    if abs(val) >= 1e9:
        return f"${val / 1e9:,.2f}B"
    if abs(val) >= 1e6:
        return f"${val / 1e6:,.2f}M"
    if abs(val) >= 1e3:
        return f"${val / 1e3:,.1f}K"
    return f"${val:,.2f}"


def _sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
    return obj


def run_single(historical: Dict[str, Any], assumptions: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single DCF valuation with given historical financials and assumptions."""
    model = DCFModel()
    model.set_historical_financials(historical)
    model.set_assumptions(assumptions)
    return model.run_full_valuation()


def build_comparison(results_by_scenario: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Build a comparison table dict across scenario results (ev_exit, ev_perpetuity, share_price_exit, share_price_perpetuity per scenario)."""
    comparison = {}
    for name, r in results_by_scenario.items():
        comparison[name] = {
            "ev_exit": r["enterprise_value"]["exit_multiple"],
            "ev_perpetuity": r["enterprise_value"]["perpetuity_growth"],
            "share_price_exit": r["value_per_share"]["exit_multiple"],
            "share_price_perpetuity": r["value_per_share"]["perpetuity_growth"],
        }
    return comparison


def format_scenario_detail(
    name: str,
    results: Dict[str, Any],
    show_sensitivity: bool = False,
) -> str:
    """
    Format detailed output for one scenario.

    If name is empty (legacy single-scenario mode), prints the canonical
    "DCF VALUATION ANALYSIS" header without a scenario label.
    If name is non-empty, prints "[NAME] DETAIL" section header.
    """
    lines: List[str] = []
    if name:
        lines.append(f"\n{'=' * 70}")
        lines.append(f"[{name.upper()}] DETAIL")
        lines.append(f"{'=' * 70}")
    else:
        lines.append("=" * 70)
        lines.append("DCF VALUATION ANALYSIS")
        lines.append("=" * 70)

    lines.append(f"\n--- WACC ---")
    wacc = results["wacc"]
    if math.isnan(wacc) or math.isinf(wacc):
        lines.append(f"  Weighted Average Cost of Capital: N/A (Invalid)")
    else:
        lines.append(f"  Weighted Average Cost of Capital: {wacc * 100:.2f}%")

    lines.append(f"\n--- REVENUE PROJECTIONS ---")
    for i, rev in enumerate(results["projected_revenue"], 1):
        lines.append(f"  Year {i}: {_fmt_money(rev)}")

    lines.append(f"\n--- FREE CASH FLOW PROJECTIONS ---")
    for i, fcf in enumerate(results["projected_fcf"], 1):
        lines.append(f"  Year {i}: {_fmt_money(fcf)}")

    lines.append(f"\n--- TERMINAL VALUE ---")
    lines.append(
        f"  Perpetuity Growth Method: {_fmt_money(results['terminal_value']['perpetuity_growth'])}"
    )
    lines.append(
        f"  Exit Multiple Method:     {_fmt_money(results['terminal_value']['exit_multiple'])}"
    )

    lines.append(f"\n--- ENTERPRISE VALUE ---")
    lines.append(
        f"  Perpetuity Growth Method: {_fmt_money(results['enterprise_value']['perpetuity_growth'])}"
    )
    lines.append(
        f"  Exit Multiple Method:     {_fmt_money(results['enterprise_value']['exit_multiple'])}"
    )

    lines.append(f"\n--- EQUITY VALUE ---")
    lines.append(
        f"  Perpetuity Growth Method: {_fmt_money(results['equity_value']['perpetuity_growth'])}"
    )
    lines.append(
        f"  Exit Multiple Method:     {_fmt_money(results['equity_value']['exit_multiple'])}"
    )

    lines.append(f"\n--- VALUE PER SHARE ---")
    vps = results["value_per_share"]
    lines.append(f"  Perpetuity Growth Method: ${vps['perpetuity_growth']:,.2f}")
    lines.append(f"  Exit Multiple Method:     ${vps['exit_multiple']:,.2f}")

    if show_sensitivity:
        sens = results["sensitivity_analysis"]
        lines.append(f"\n--- SENSITIVITY ANALYSIS (Enterprise Value) ---")
        lines.append(f"  WACC vs Terminal Growth Rate")
        lines.append("")

        header = "  {:>10s}".format("WACC \\ g")
        for g in sens["growth_values"]:
            header += f"  {g * 100:>8.1f}%"
        lines.append(header)
        lines.append("  " + "-" * (10 + 10 * len(sens["growth_values"])))

        for i, w in enumerate(sens["wacc_values"]):
            row = f"  {w * 100:>9.1f}%"
            for j in range(len(sens["growth_values"])):
                val = sens["enterprise_value_table"][i][j]
                row += f"  {_fmt_money(val):>8s}"
            lines.append(row)

    return "\n".join(lines)


def format_scenarios_text(
    results_by_scenario: Dict[str, Dict[str, Any]]
) -> str:
    """
    Format multi-scenario comparison table plus per-scenario detail.

    Base scenario (case-insensitive match) gets the full sensitivity table.
    Other scenarios get abbreviated output (no sensitivity table).
    """
    comparison = build_comparison(results_by_scenario)

    lines: List[str] = []
    lines.append("=" * 70)
    lines.append("DCF VALUATION ANALYSIS — SCENARIO COMPARISON")
    lines.append("=" * 70)
    lines.append("")
    lines.append(
        f"{'Scenario':<12} | {'EV (Exit)':>12} | {'EV (Perp)':>12} | "
        f"{'$/share (Exit)':>14} | {'$/share (Perp)':>14}"
    )
    lines.append("-" * 70)

    for name in results_by_scenario:
        c = comparison[name]
        lines.append(
            f"{name:<12} | {_fmt_money(c['ev_exit']):>12} | "
            f"{_fmt_money(c['ev_perpetuity']):>12} | "
            f"${c['share_price_exit']:>12,.2f} | "
            f"${c['share_price_perpetuity']:>12,.2f}"
        )

    base_name = next(
        (n for n in results_by_scenario if n.lower() == "base"),
        next(iter(results_by_scenario), None),
    )

    for name, results in results_by_scenario.items():
        show_sensitivity = (name == base_name)
        lines.append(format_scenario_detail(name, results, show_sensitivity=show_sensitivity))

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def _format_failed_scenarios(failed: Dict[str, str]) -> str:
    """Format failed scenario list for text output."""
    lines: List[str] = []
    lines.append("\n--- SKIPPED / FAILED SCENARIOS ---")
    for name, reason in failed.items():
        lines.append(f"  [{name}] FAILED: {reason}")
    return "\n".join(lines)


class DCFModel:

    def __init__(self) -> None:
        self.historical: Dict[str, Any] = {}
        self.assumptions: Dict[str, Any] = {}
        self.wacc: float = 0.0
        self.projected_revenue: List[float] = []
        self.projected_fcf: List[float] = []
        self.projection_years: int = 5
        self.terminal_value_perpetuity: float = 0.0
        self.terminal_value_exit_multiple: float = 0.0
        self.enterprise_value_perpetuity: float = 0.0
        self.enterprise_value_exit_multiple: float = 0.0
        self.equity_value_perpetuity: float = 0.0
        self.equity_value_exit_multiple: float = 0.0
        self.value_per_share_perpetuity: float = 0.0
        self.value_per_share_exit_multiple: float = 0.0

    def set_historical_financials(self, historical: Dict[str, Any]) -> None:
        self.historical = historical

    def set_assumptions(self, assumptions: Dict[str, Any]) -> None:
        self.assumptions = assumptions
        self.projection_years = assumptions.get("projection_years", DEFAULT_PROJECTION_YEARS)

    def calculate_wacc(self) -> float:
        wacc_inputs = self.assumptions.get("wacc_inputs", {})

        risk_free_rate = wacc_inputs.get("risk_free_rate", 0.04)
        equity_risk_premium = wacc_inputs.get("equity_risk_premium", 0.06)
        beta = wacc_inputs.get("beta", 1.0)
        cost_of_debt = wacc_inputs.get("cost_of_debt", 0.05)
        tax_rate = wacc_inputs.get("tax_rate", 0.25)
        debt_weight = wacc_inputs.get("debt_weight", 0.30)
        equity_weight = wacc_inputs.get("equity_weight", 0.70)

        cost_of_equity = risk_free_rate + beta * equity_risk_premium

        after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
        self.wacc = (equity_weight * cost_of_equity) + (
            debt_weight * after_tax_cost_of_debt
        )

        # Sanity check: WACC should typically be between 2% and 30%
        if self.wacc < 0.02 or self.wacc > 0.30:
            print(f"Warning: Calculated WACC ({self.wacc:.2%}) is outside typical range (2%-30%)", file=sys.stderr)

        return self.wacc

    def project_cash_flows(self) -> Tuple[List[float], List[float]]:
        base_revenue = self.historical.get("revenue", [])
        if not base_revenue:
            raise ValueError("Historical revenue data is required")

        last_revenue = base_revenue[-1]

        revenue_growth_rates = self.assumptions.get("revenue_growth_rates", [])
        fcf_margins = self.assumptions.get("fcf_margins", [])

        default_growth = self.assumptions.get("default_revenue_growth", 0.05)
        default_fcf_margin = self.assumptions.get("default_fcf_margin", 0.10)

        self.projected_revenue = []
        self.projected_fcf = []
        current_revenue = last_revenue

        for year in range(self.projection_years):
            growth = (
                revenue_growth_rates[year]
                if year < len(revenue_growth_rates)
                else default_growth
            )
            fcf_margin = (
                fcf_margins[year]
                if year < len(fcf_margins)
                else default_fcf_margin
            )

            current_revenue = current_revenue * (1 + growth)
            fcf = current_revenue * fcf_margin

            self.projected_revenue.append(current_revenue)
            self.projected_fcf.append(fcf)

        return self.projected_revenue, self.projected_fcf

    def calculate_terminal_value(self) -> Tuple[float, float]:
        if not self.projected_fcf:
            raise ValueError("Must project cash flows before terminal value")

        terminal_fcf = self.projected_fcf[-1]
        terminal_growth = self.assumptions.get("terminal_growth_rate", DEFAULT_TERMINAL_GROWTH_RATE)
        exit_multiple = self.assumptions.get("exit_ev_ebitda_multiple", DEFAULT_EXIT_EV_EBITDA_MULTIPLE)

        # Validate terminal growth is reasonable (typically 0% to 10%)
        if terminal_growth < 0 or terminal_growth > 0.10:
            print(f"Warning: Terminal growth rate ({terminal_growth:.2%}) is outside typical range (0%-10%)", file=sys.stderr)

        if self.wacc > terminal_growth:
            self.terminal_value_perpetuity = (
                terminal_fcf * (1 + terminal_growth)
            ) / (self.wacc - terminal_growth)
        else:
            self.terminal_value_perpetuity = 0.0
            print("Warning: WACC ({:.2%}) <= terminal growth rate ({:.2%}). Perpetuity method disabled.".format(self.wacc, terminal_growth), file=sys.stderr)

        terminal_revenue = self.projected_revenue[-1]
        ebitda_margin = self.assumptions.get("terminal_ebitda_margin", DEFAULT_EBITDA_MARGIN)
        terminal_ebitda = terminal_revenue * ebitda_margin
        self.terminal_value_exit_multiple = terminal_ebitda * exit_multiple

        return self.terminal_value_perpetuity, self.terminal_value_exit_multiple

    def calculate_enterprise_value(self) -> Tuple[float, float]:
        if not self.projected_fcf:
            raise ValueError("Must project cash flows first")

        pv_fcf = 0.0
        for i, fcf in enumerate(self.projected_fcf):
            discount_factor = (1 + self.wacc) ** (i + 1)
            pv_fcf += fcf / discount_factor

        terminal_discount = (1 + self.wacc) ** self.projection_years

        pv_tv_perpetuity = self.terminal_value_perpetuity / terminal_discount
        pv_tv_exit = self.terminal_value_exit_multiple / terminal_discount

        self.enterprise_value_perpetuity = pv_fcf + pv_tv_perpetuity
        self.enterprise_value_exit_multiple = pv_fcf + pv_tv_exit

        return self.enterprise_value_perpetuity, self.enterprise_value_exit_multiple

    def calculate_equity_value(self) -> Tuple[float, float]:
        net_debt = self.historical.get("net_debt", 0)
        shares_outstanding = self.historical.get("shares_outstanding", 1)

        self.equity_value_perpetuity = (
            self.enterprise_value_perpetuity - net_debt
        )
        self.equity_value_exit_multiple = (
            self.enterprise_value_exit_multiple - net_debt
        )

        self.value_per_share_perpetuity = safe_divide(
            self.equity_value_perpetuity, shares_outstanding
        )
        self.value_per_share_exit_multiple = safe_divide(
            self.equity_value_exit_multiple, shares_outstanding
        )

        return self.equity_value_perpetuity, self.equity_value_exit_multiple

    def sensitivity_analysis(
        self,
        wacc_range: Optional[List[float]] = None,
        growth_range: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """
        Two-way sensitivity analysis: WACC vs terminal growth rate.

        Returns a table of enterprise values using nested lists (no numpy).
        """
        if wacc_range is None:
            base_wacc = self.wacc
            wacc_range = [
                round(base_wacc - 0.02, 4),
                round(base_wacc - 0.01, 4),
                round(base_wacc, 4),
                round(base_wacc + 0.01, 4),
                round(base_wacc + 0.02, 4),
            ]

        if growth_range is None:
            base_growth = self.assumptions.get("terminal_growth_rate", 0.025)
            growth_range = [
                round(base_growth - 0.01, 4),
                round(base_growth - 0.005, 4),
                round(base_growth, 4),
                round(base_growth + 0.005, 4),
                round(base_growth + 0.01, 4),
            ]

        rows = len(wacc_range)
        cols = len(growth_range)

        ev_table = [[0.0] * cols for _ in range(rows)]
        share_price_table = [[0.0] * cols for _ in range(rows)]

        terminal_fcf = self.projected_fcf[-1] if self.projected_fcf else 0

        for i, wacc_val in enumerate(wacc_range):
            for j, growth_val in enumerate(growth_range):
                if wacc_val <= growth_val:
                    ev_table[i][j] = None
                    share_price_table[i][j] = None
                    continue

                pv_fcf = 0.0
                for k, fcf in enumerate(self.projected_fcf):
                    pv_fcf += fcf / ((1 + wacc_val) ** (k + 1))

                tv = (terminal_fcf * (1 + growth_val)) / (wacc_val - growth_val)
                pv_tv = tv / ((1 + wacc_val) ** self.projection_years)

                ev = pv_fcf + pv_tv
                ev_table[i][j] = round(ev, 2)

                net_debt = self.historical.get("net_debt", 0)
                shares = self.historical.get("shares_outstanding", 1)
                equity = ev - net_debt
                share_price_table[i][j] = round(
                    safe_divide(equity, shares), 2
                )

        return {
            "wacc_values": wacc_range,
            "growth_values": growth_range,
            "enterprise_value_table": ev_table,
            "share_price_table": share_price_table,
        }

    def run_full_valuation(self) -> Dict[str, Any]:
        """Run the complete DCF valuation."""
        self.calculate_wacc()
        self.project_cash_flows()
        self.calculate_terminal_value()
        self.calculate_enterprise_value()
        self.calculate_equity_value()
        sensitivity = self.sensitivity_analysis()

        return {
            "wacc": self.wacc,
            "projected_revenue": self.projected_revenue,
            "projected_fcf": self.projected_fcf,
            "terminal_value": {
                "perpetuity_growth": self.terminal_value_perpetuity,
                "exit_multiple": self.terminal_value_exit_multiple,
            },
            "enterprise_value": {
                "perpetuity_growth": self.enterprise_value_perpetuity,
                "exit_multiple": self.enterprise_value_exit_multiple,
            },
            "equity_value": {
                "perpetuity_growth": self.equity_value_perpetuity,
                "exit_multiple": self.equity_value_exit_multiple,
            },
            "value_per_share": {
                "perpetuity_growth": self.value_per_share_perpetuity,
                "exit_multiple": self.value_per_share_exit_multiple,
            },
            "sensitivity_analysis": sensitivity,
        }

    def format_text(self, results: Dict[str, Any]) -> str:
        """Single-scenario text output (legacy wrapper for backward compat)."""
        return format_scenario_detail("", results, show_sensitivity=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="DCF Valuation Model")
    parser.add_argument("input_file", nargs="?", help="Path to JSON file")
    parser.add_argument("--stdin", action="store_true", help="Read JSON from stdin")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--projection-years", type=int, default=None)

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

    historical = data.get("historical", {})
    assumptions = data.get("assumptions", {})

    if args.projection_years is not None:
        assumptions["projection_years"] = args.projection_years

    scenarios_input = assumptions.get("scenarios")

    if scenarios_input:
        global_defaults = {k: v for k, v in assumptions.items() if k != "scenarios"}
        results_by_scenario: Dict[str, Dict[str, Any]] = {}
        failed: Dict[str, str] = {}
        for name, scenario_assumptions in scenarios_input.items():
            merged = {**global_defaults, **scenario_assumptions}
            try:
                results_by_scenario[name] = run_single(historical, merged)
            except ValueError as e:
                failed[name] = str(e)
                print(f"Warning: scenario '{name}' skipped — {e}", file=sys.stderr)

        if not results_by_scenario:
            print("Error: all scenarios failed", file=sys.stderr)
            sys.exit(1)

        if args.format == "json":
            output = {
                "scenarios": _sanitize(results_by_scenario),
                "comparison": _sanitize(build_comparison(results_by_scenario)),
            }
            if failed:
                output["failed_scenarios"] = failed
            print(json.dumps(output, indent=2))
        else:
            text = format_scenarios_text(results_by_scenario)
            if failed:
                text += _format_failed_scenarios(failed)
            print(text)
    else:
        model = DCFModel()
        model.set_historical_financials(historical)
        model.set_assumptions(assumptions)

        try:
            results = model.run_full_valuation()
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        if args.format == "json":
            print(json.dumps(_sanitize(results), indent=2))
        else:
            print(model.format_text(results))


if __name__ == "__main__":
    main()