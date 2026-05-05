#!/usr/bin/env python3
import json, argparse, sys
from typing import Dict, List, Optional

class PortfolioRebalancer:
    def __init__(self, transaction_cost: float = 0.001):
        self.transaction_cost = transaction_cost

    def calculate_current_allocation(self, portfolio_data: Dict):
        allocations = {}
        total_value = 0
        for asset in portfolio_data['assets']:
            value = asset.get('current_value', asset.get('current_price', 0) * asset.get('quantity', 0))
            allocations[asset['symbol']] = value
            total_value += value
        if total_value > 0:
            allocations = {k: v / total_value for k, v in allocations.items()}
        return allocations, total_value

    def rebalance_to_target(self, current_values: Dict[str, float], target_weights: Dict[str, float]):
        if not current_values:
            raise ValueError("Current values cannot be empty")
        if abs(sum(target_weights.values()) - 1.0) > 0.01:
            raise ValueError(f"Target weights must sum to 1.0 (got {sum(target_weights.values()):.3f})")

        # Combine assets from both current and target (in case target includes new assets)
        all_assets = set(current_values.keys()) | set(target_weights.keys())
        assets = list(all_assets)
        
        total_value = sum(current_values.values())

        target_values = {a: target_weights.get(a, 0) * total_value for a in assets}
        trades = {a: target_values[a] - current_values.get(a, 0) for a in assets}
        current_alloc = {a: current_values.get(a, 0) / total_value for a in assets}
        target_alloc = {a: target_values[a] / total_value for a in assets}
        alloc_change = {a: target_alloc[a] - current_alloc[a] for a in assets}

        trade_volume = sum(abs(trades[a]) for a in assets)
        transaction_costs = trade_volume * self.transaction_cost

        return {
            "assets": assets,
            "current_values": current_values,
            "target_values": target_values,
            "trades": trades,
            "current_allocation": current_alloc,
            "target_allocation": target_alloc,
            "allocation_change": alloc_change,
            "total_value": total_value,
            "transaction_costs": transaction_costs,
            "trade_volume": trade_volume,
            "turnover_rate": trade_volume / total_value if total_value > 0 else 0,
        }

def main():
    parser = argparse.ArgumentParser(description='Portfolio Rebalancing Calculator')
    parser.add_argument('portfolio_file', nargs='?', help='JSON file')
    parser.add_argument('--stdin', action='store_true', help='Read from stdin')
    parser.add_argument('--transaction-cost', type=float, default=0.001)
    parser.add_argument('--format', choices=['json', 'text'], default='text')

    args = parser.parse_args()

    try:
        if args.stdin:
            portfolio_data = json.loads(sys.stdin.read())
        elif args.portfolio_file:
            with open(args.portfolio_file) as f:
                portfolio_data = json.load(f)
        else:
            parser.print_help()
            return 1
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    rebalancer = PortfolioRebalancer(transaction_cost=args.transaction_cost)
    current_alloc, total_value = rebalancer.calculate_current_allocation(portfolio_data)
    target_weights = portfolio_data.get('target_weights', {})

    if not target_weights:
        n = len(portfolio_data['assets'])
        target_weights = {a['symbol']: 1.0/n for a in portfolio_data['assets']}

    current_values = {}
    for asset in portfolio_data['assets']:
        value = asset.get('current_value', asset.get('current_price', 0) * asset.get('quantity', 0))
        current_values[asset['symbol']] = value

    try:
        result = rebalancer.rebalance_to_target(current_values, target_weights)
        if args.format == 'json':
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"\nPortfolio Value: ${result['total_value']:,.2f}")
            print(f"Transaction Costs: ${result['transaction_costs']:,.2f}")
            print(f"Turnover Rate: {result['turnover_rate']:.1%}")
            print(f"\n{'Asset':<15} {'Current %':>10} {'Target %':>10} {'Change':>10} {'Trade':>12}")
            print("-" * 60)
            for a in result['assets']:
                print(f"{a:<15} {result['current_allocation'][a]*100:>9.1f}% {result['target_allocation'][a]*100:>9.1f}% {result['allocation_change'][a]*100:>9.1f}% ${result['trades'][a]:>11,.2f}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
