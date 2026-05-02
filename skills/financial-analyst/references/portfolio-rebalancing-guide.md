# Portfolio Rebalancing Guide

## Overview

Portfolio rebalancing is the process of realigning the weightings of assets in a portfolio to maintain a desired level of asset allocation and risk. This guide covers methodologies, best practices, and implementation strategies.

## Why Rebalance?

### Key Benefits
1. **Risk Management**: Maintains target risk level
2. **Discipline**: Forces "sell high, buy low" behavior
3. **Diversification**: Prevents concentration in winning assets
4. **Goal Alignment**: Keeps portfolio aligned with investment objectives

### When to Rebalance?
- **Time-based**: Quarterly, semi-annually, annually
- **Threshold-based**: When allocations drift ±5-10%
- **Event-based**: Major life changes, market events
- **Opportunity-based**: Tax-loss harvesting opportunities

## Rebalancing Methodologies

### 1. Simple Rebalancing
Bring portfolio back to target asset allocation percentages.

**Formula:**
```
Trade Amount = (Target % - Current %) × Total Portfolio Value
```

**Example:**
- Target: 60% Stocks, 40% Bonds
- Current: 70% Stocks, 30% Bonds
- Portfolio: $100,000
- Action: Sell $10,000 Stocks, Buy $10,000 Bonds

### 2. Modern Portfolio Theory (Markowitz)
Optimize portfolio on the efficient frontier.

**Key Components:**
- Expected returns for each asset
- Covariance matrix (risk relationships)
- Risk-free rate
- Investor's risk tolerance

**Mathematical Formulation:**
```
Maximize: μ'w - (λ/2) × w'Σw
Subject to: Σw = 1, w ≥ 0 (long-only)
Where:
  μ = expected returns vector
  w = portfolio weights
  Σ = covariance matrix
  λ = risk aversion parameter
```

### 3. Risk Parity
Allocate so each asset contributes equally to portfolio risk.

**Calculation:**
1. Estimate volatility (σ) for each asset
2. Calculate risk contribution: wᵢ × σᵢ
3. Adjust weights until all risk contributions equal

**Weight Formula:**
```
wᵢ = (1/σᵢ) / Σ(1/σⱼ)
```

### 4. Black-Litterman Model
Combine market equilibrium with investor views.

**Steps:**
1. Start with market equilibrium weights (CAPM)
2. Express investor views as expected returns
3. Use Bayesian updating to combine
4. Optimize with new expected returns

## Tax Considerations

### Tax-Loss Harvesting
Selling securities at a loss to offset capital gains.

**Rules:**
- **Wash Sale Rule**: Cannot repurchase "substantially identical" security within 30 days
- **Short-term vs Long-term**: Different tax rates
- **Carryforward**: Losses can offset future gains

**Implementation Strategy:**
1. Identify losing positions (>5-10% loss)
2. Sell to realize loss
3. Buy similar but not identical security
4. Maintain market exposure

### Tax-Efficient Rebalancing
1. **Use tax-advantaged accounts first** (IRA, 401k)
2. **Harvest losses in taxable accounts**
3. **Consider turnover and transaction costs**
4. **Match gains with losses**

## Implementation Strategies

### 1. Full Rebalancing
Sell overallocated assets and buy underallocated assets to return exactly to target.

**Pros**: Precise, maintains exact target
**Cons**: Higher transaction costs, potential tax impact

### 2. Partial Rebalancing
Only rebalance assets beyond a threshold (e.g., ±5%).

**Pros**: Lower costs, less turnover
**Cons**: May not return to exact target

### 3. Cash Flow Rebalancing
Use new contributions or withdrawals to adjust allocations.

**Pros**: No selling needed, tax-efficient
**Cons**: Requires ongoing cash flows

### 4. Band-Based Rebalancing
Trigger rebalancing when allocations move outside predetermined bands.

**Common Bands:**
- Conservative: ±5%
- Moderate: ±10%
- Aggressive: ±15%

## Risk Management in Rebalancing

### Volatility Considerations
- **High Volatility Assets**: Require more frequent rebalancing
- **Low Volatility Assets**: Can tolerate wider bands
- **Correlation Changes**: Monitor asset relationships

### Transaction Costs
Include in optimization:
- Brokerage commissions
- Bid-ask spreads
- Market impact
- Tax implications

### Liquidity Constraints
- **Large Positions**: May need gradual rebalancing
- **Illiquid Assets**: Wider bands, less frequent
- **Market Conditions**: Avoid rebalancing during crises

## Performance Measurement

### Before/After Metrics
1. **Portfolio Volatility**: Should decrease after rebalancing
2. **Sharpe Ratio**: Risk-adjusted return should improve
3. **Maximum Drawdown**: Potential reduction in worst loss
4. **Tracking Error**: Vs. target allocation

### Cost-Benefit Analysis
```
Net Benefit = Expected Risk Reduction - Transaction Costs - Tax Impact
```

## Common Pitfalls

### 1. Over-Rebalancing
- Excessive transaction costs
- Unnecessary tax events
- Chasing performance

### 2. Under-Rebalancing
- Risk drift from target
- Concentration in winners
- Missed diversification benefits

### 3. Market Timing
Trying to time rebalancing based on market predictions.

**Better Approach**: Stick to systematic, rules-based rebalancing.

### 4. Ignoring Taxes
Failing to consider tax implications of selling.

## Best Practices

### 1. Document Your Policy
- Rebalancing method
- Frequency or thresholds
- Tax considerations
- Implementation rules

### 2. Automate When Possible
- Use portfolio management software
- Set up alerts for threshold breaches
- Schedule regular reviews

### 3. Monitor and Adjust
- Review policy annually
- Adjust for life changes
- Update for tax law changes

### 4. Consider Behavioral Biases
- Dislike of realizing losses
- Attachment to winning positions
- Procrastination

## Tools and Resources

### Python Libraries
- **NumPy/SciPy**: Optimization algorithms
- **pandas**: Data manipulation
- **PyPortfolioOpt**: Portfolio optimization library
- **QuantLib**: Advanced financial calculations

### Financial APIs
- **Alpha Vantage**: Market data and technical indicators
- **Yahoo Finance**: Historical prices
- **IEX Cloud**: Real-time and historical data
- **FRED**: Economic data

## Case Studies

### Case 1: Retiree Portfolio
- **Profile**: Conservative, income-focused
- **Strategy**: Band-based with tax efficiency
- **Frequency**: Semi-annual, using cash flows when possible
- **Tax**: Focus on tax-loss harvesting in down markets

### Case 2: Young Accumulator
- **Profile**: Aggressive, growth-focused
- **Strategy**: Full rebalancing to maintain risk exposure
- **Frequency**: Annual, using new contributions
- **Tax**: Maximize tax-advantaged accounts

### Case 3: Institutional Portfolio
- **Profile**: Large, tax-sensitive
- **Strategy**: Optimization with transaction cost modeling
- **Frequency**: Quarterly with careful tax planning
- **Tax**: Sophisticated tax-loss harvesting

## References

1. Markowitz, H. (1952). "Portfolio Selection"
2. Black, F., & Litterman, R. (1992). "Global Portfolio Optimization"
3. Qian, E. (2005). "Risk Parity Fundamentals"
4. Israelsen, C. (2005). "A Refinement to the Sharpe Ratio"

---

**Remember**: The best rebalancing strategy is one you can stick with consistently over the long term.