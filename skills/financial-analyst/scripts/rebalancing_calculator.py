#!/usr/bin/env python3
"""
Portfolio Rebalancing Calculator

Calculate optimal rebalancing trades to bring portfolio to target allocations.
Modern Portfolio Theory (Markowitz) and Risk Parity approaches.

Usage:
    python rebalancing_calculator.py portfolio_data.json
    python rebalancing_calculator.py portfolio_data.json --method risk_parity
    python rebalancing_calculator.py portfolio_data.json --transaction-cost 0.001
"""

import json
import argparse
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class PortfolioAsset:
    """Individual asset in portfolio"""
    symbol: str
    asset_class: str
    current_value: float
    current_price: float
    quantity: float
    purchase_price: Optional[float] = None

@dataclass
class RebalancingResult:
    """Rebalancing calculation results"""
    assets: List[str]
    current_values: Dict[str, float]
    target_values: Dict[str, float]
    trades: Dict[str, float]
    current_allocation: Dict[str, float]
    target_allocation: Dict[str, float]
    allocation_change: Dict[str, float]
    total_value: float
    transaction_costs: float
    trade_volume: float
    turnover_rate: float
    method_used: str

class PortfolioRebalancer:
    """Portfolio rebalancing engine"""
    
    def __init__(self, transaction_cost: float = 0.001):
        self.transaction_cost = transaction_cost
    
    def calculate_current_allocation(self, portfolio_data: Dict) -> Tuple[Dict[str, float], float]:
        """
        Calculate current portfolio allocation
        
        Args:
            portfolio_data: Dict with asset data
            
        Returns:
            (allocation_dict, total_value)
        """
        allocations = {}
        total_value = 0
        
        for asset in portfolio_data['assets']:
            value = asset.get('current_value', 
                            asset.get('current_price', 0) * asset.get('quantity', 0))
            allocations[asset['symbol']] = value
            total_value += value
        
        # Convert to percentages
        if total_value > 0:
            allocations = {k: v / total_value for k, v in allocations.items()}
        
        return allocations, total_value
    
    def rebalance_to_target(self, 
                          current_values: Dict[str, float], 
                          target_weights: Dict[str, float],
                          method: str = "simple") -> RebalancingResult:
        """
        Rebalance portfolio to target weights
        
        Args:
            current_values: Current values by asset {symbol: value}
            target_weights: Target weights (0-1) by asset {symbol: weight}
            method: Rebalancing method ("simple", "mpt", "risk_parity")
            
        Returns:
            RebalancingResult object
        """
        # Validate inputs
        if not current_values:
            raise ValueError("Current values cannot be empty")
        
        if abs(sum(target_weights.values()) - 1.0) > 0.01:
            raise ValueError(f"Target weights must sum to 1.0 (got {sum(target_weights.values()):.3f})")
        
        assets = list(current_values.keys())
        current_array = np.array([current_values[a] for a in assets])
        total_value = current_array.sum()
        
        # Get target weights for all assets (default 0 for unspecified)
        target_array = np.array([target_weights.get(a, 0) for a in assets])
        
        # Apply method-specific adjustments
        if method == "mpt":
            target_array = self._apply_mpt_adjustment(current_array, target_array)
        elif method == "risk_parity":
            target_array = self._apply_risk_parity_adjustment(current_array, target_array)
        
        # Normalize target weights
        if target_array.sum() > 0:
            target_array = target_array / target_array.sum()
        
        # Calculate target values
        target_values_array = target_array * total_value
        
        # Calculate trades
        trades_array = target_values_array - current_array
        
        # Calculate allocations
        current_alloc = current_array / total_value if total_value > 0 else np.zeros_like(current_array)
        target_alloc = target_values_array / total_value if total_value > 0 else np.zeros_like(target_values_array)
        alloc_change = target_alloc - current_alloc
        
        # Calculate transaction costs
        trade_volume = np.abs(trades_array).sum()
        transaction_costs = trade_volume * self.transaction_cost
        
        # Create result object
        result = RebalancingResult(
            assets=assets,
            current_values=dict(zip(assets, current_array)),
            target_values=dict(zip(assets, target_values_array)),
            trades=dict(zip(assets, trades_array)),
            current_allocation=dict(zip(assets, current_alloc)),
            target_allocation=dict(zip(assets, target_alloc)),
            allocation_change=dict(zip(assets, alloc_change)),
            total_value=total_value,
            transaction_costs=transaction_costs,
            trade_volume=trade_volume,
            turnover_rate=trade_volume / total_value if total_value > 0 else 0,
            method_used=method
        )
        
        return result
    
    def _apply_mpt_adjustment(self, 
                            current_values: np.ndarray,
                            target_weights: np.ndarray) -> np.ndarray:
        """
        Apply Modern Portfolio Theory adjustments
        
        For simplicity, this is a placeholder. Full MPT would require:
        - Expected returns
        - Covariance matrix
        - Risk-free rate
        """
        # Simple momentum adjustment: reduce weight on recent losers
        # In practice, this would be based on Sharpe ratios, etc.
        return target_weights
    
    def _apply_risk_parity_adjustment(self,
                                    current_values: np.ndarray,
                                    target_weights: np.ndarray) -> np.ndarray:
        """
        Apply Risk Parity adjustments
        
        Weight inversely proportional to volatility.
        Placeholder - would need historical volatility data.
        """
        # Equal risk contribution (simplified)
        n_assets = len(target_weights)
        if n_assets > 0:
            return np.ones(n_assets) / n_assets
        return target_weights
    
    def calculate_tax_loss_harvesting(self,
                                    portfolio: List[PortfolioAsset],
                                    threshold_pct: float = -0.05) -> List[Dict]:
        """
        Identify tax-loss harvesting opportunities
        
        Args:
            portfolio: List of PortfolioAsset objects
            threshold_pct: Minimum loss percentage to consider
            
        Returns:
            List of harvesting opportunities
        """
        opportunities = []
        
        for asset in portfolio:
            if asset.purchase_price and asset.current_price:
                pnl_pct = (asset.current_price - asset.purchase_price) / asset.purchase_price
                
                if pnl_pct < threshold_pct:
                    # Potential tax loss
                    loss_amount = (asset.purchase_price - asset.current_price) * asset.quantity
                    
                    opportunities.append({
                        'symbol': asset.symbol,
                        'current_price': asset.current_price,
                        'purchase_price': asset.purchase_price,
                        'quantity': asset.quantity,
                        'pnl_pct': pnl_pct,
                        'loss_amount': loss_amount,
                        'current_value': asset.current_value,
                        'action': f"Sell {asset.quantity} shares for ${loss_amount:.2f} loss"
                    })
        
        return opportunities

def load_portfolio_data(filepath: str) -> Dict:
    """Load portfolio data from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_results(results: RebalancingResult, output_file: Optional[str] = None):
    """Save rebalancing results"""
    results_dict = asdict(results)
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)
    
    return results_dict

def load_portfolio_data_from_stdin() -> Dict:
    """Load portfolio data from stdin"""
    import sys
    raw = sys.stdin.read()
    return json.loads(raw)

def main():
    parser = argparse.ArgumentParser(description='Portfolio Rebalancing Calculator')
    parser.add_argument('portfolio_file', nargs='?', help='JSON file with portfolio data')
    parser.add_argument('--stdin', action='store_true', help='Read portfolio data from stdin')
    parser.add_argument('--method', choices=['simple', 'mpt', 'risk_parity'], 
                       default='simple', help='Rebalancing method')
    parser.add_argument('--transaction-cost', type=float, default=0.001,
                       help='Transaction cost per dollar traded (default: 0.001)')
    parser.add_argument('--output', '-o', help='Output file for results')
    parser.add_argument('--format', choices=['json', 'text'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    # Load portfolio data
    try:
        if args.stdin:
            portfolio_data = load_portfolio_data_from_stdin()
        elif args.portfolio_file:
            portfolio_data = load_portfolio_data(args.portfolio_file)
        else:
            parser.print_help()
            return 1
    except FileNotFoundError:
        print(f"Error: File {args.portfolio_file} not found")
        return 1
    except json.JSONDecodeError:
        print("Error: Invalid JSON in input")
        return 1
    
    # Create rebalancer
    rebalancer = PortfolioRebalancer(transaction_cost=args.transaction_cost)
    
    # Calculate current allocation
    current_alloc, total_value = rebalancer.calculate_current_allocation(portfolio_data)
    
    # Get target weights (from input or use default)
    target_weights = portfolio_data.get('target_weights', {})
    if not target_weights:
        # Default: equal weight
        n_assets = len(portfolio_data['assets'])
        target_weights = {asset['symbol']: 1.0/n_assets for asset in portfolio_data['assets']}
    
    # Convert current values to dict
    current_values = {}
    for asset in portfolio_data['assets']:
        value = asset.get('current_value', 
                         asset.get('current_price', 0) * asset.get('quantity', 0))
        current_values[asset['symbol']] = value
    
    # Perform rebalancing
    try:
        result = rebalancer.rebalance_to_target(current_values, target_weights, args.method)
        
        # Save results
        results_dict = save_results(result, args.output)
        
        # Print summary
        if args.format == 'text':
            print("\n" + "="*60)
            print("PORTFOLIO REBALANCING REPORT")
            print("="*60)
            
            print(f"\nPortfolio Value: ${result.total_value:,.2f}")
            print(f"Rebalancing Method: {result.method_used}")
            print(f"Transaction Costs: ${result.transaction_costs:,.2f}")
            print(f"Turnover Rate: {result.turnover_rate:.1%}")
            
            print("\n" + "-"*60)
            print("ASSET ALLOCATION SUMMARY")
            print("-"*60)
            print(f"{'Asset':<15} {'Current %':>10} {'Target %':>10} {'Change':>10} {'Trade':>12}")
            print("-"*60)
            
            for asset in result.assets:
                curr_pct = result.current_allocation[asset] * 100
                targ_pct = result.target_allocation[asset] * 100
                change_pct = result.allocation_change[asset] * 100
                trade = result.trades[asset]
                
                print(f"{asset:<15} {curr_pct:>9.1f}% {targ_pct:>9.1f}% {change_pct:>9.1f}% ${trade:>11,.2f}")
            
            print("\n" + "="*60)
            print("RECOMMENDED ACTIONS:")
            print("="*60)
            
            # Show buy recommendations
            print("\nBUY:")
            for asset in result.assets:
                if result.trades[asset] > 100:  # Min $100 trade
                    print(f"  {asset}: ${result.trades[asset]:,.2f}")
            
            # Show sell recommendations
            print("\nSELL:")
            for asset in result.assets:
                if result.trades[asset] < -100:  # Min $100 trade
                    print(f"  {asset}: ${-result.trades[asset]:,.2f}")
            
            print("\n" + "="*60)
        
        elif args.format == 'json':
            print(json.dumps(results_dict, indent=2, default=str))
        
        if args.output:
            print(f"\nResults saved to: {args.output}")
            
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())