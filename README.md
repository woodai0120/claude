# Regime-Based Factor Allocation Strategy

A sophisticated quantitative investment strategy that combines macroeconomic regime detection with factor-based portfolio allocation, featuring dynamic risk management.

## Overview

This repository implements a regime-aware factor rotation strategy that:
- Detects economic regimes (Expansion, Peak, Contraction, Recovery) using macroeconomic indicators
- Allocates across factor ETFs (Momentum, Quality, Size, Value, Low Volatility) based on regime preferences
- Combines momentum and valuation signals for factor selection
- Implements dynamic risk-off mechanisms during adverse market conditions
- Compares baseline (v3) with improved (v4A) risk management approaches

## Key Features

### v3 (Baseline Strategy)
- Full regime-based factor allocation
- Risk-off: 50% cash on negative SPY momentum, 70% on CFNAI < -0.5
- Consistent across all regimes

### v4A (Recovery Softened)
**Key Innovation**: Caps risk-off at 30% during Recovery regimes
- Maintains at least 70% factor exposure during recoveries
- Captures more upside during market recovery periods
- Other regimes follow standard risk-off rules

## Project Structure

```
claude/
├── config/
│   └── config.py                 # Configuration and parameters
├── src/
│   ├── data/
│   │   └── data_loader.py        # Data loading from Yahoo Finance and FRED
│   ├── factors/
│   │   └── factor_signals.py     # Momentum and valuation signal calculation
│   ├── regime/
│   │   └── regime_detector.py    # Economic regime detection
│   ├── backtest/
│   │   └── strategy.py           # Main strategy implementation (v3 & v4A)
│   └── utils/
│       └── performance.py        # Performance metrics and analytics
├── notebooks/
│   └── regime_strategy_analysis.ipynb  # Interactive analysis notebook
├── data/
│   ├── raw/                      # Raw data files
│   └── processed/                # Processed data
├── main.py                       # Main execution script
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/woodai0120/claude.git
cd claude

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the complete analysis:

```bash
python main.py
```

This will:
1. Download price and economic data
2. Calculate factor signals
3. Detect economic regimes
4. Run all strategies (Equal-Weight, Momentum, v3, v4A, SPY)
5. Generate performance statistics and visualizations
6. Save results to CSV files

### Interactive Analysis

For detailed exploration, use the Jupyter notebook:

```bash
jupyter notebook notebooks/regime_strategy_analysis.ipynb
```

### Custom Configuration

Edit `config/config.py` to customize:
- Factor ETF selection
- Signal weights (momentum vs. valuation)
- Risk-off thresholds
- Regime preferences
- Transaction costs
- Date ranges

## Strategy Components

### 1. Data Sources

**Price Data** (Yahoo Finance):
- MTUM: iShares MSCI USA Momentum Factor ETF
- QUAL: iShares MSCI USA Quality Factor ETF
- SIZE: iShares MSCI USA Size Factor ETF
- VLUE: iShares MSCI USA Value Factor ETF
- USMV: iShares MSCI USA Min Vol Factor ETF
- SPY: S&P 500 ETF (benchmark)
- BIL: SPDR Bloomberg 1-3 Month T-Bill ETF (cash)

**Economic Data** (FRED):
- CFNAI: Chicago Fed National Activity Index
- UNRATE: Unemployment Rate
- T10Y2Y: 10-Year Treasury - 2-Year Treasury Spread

### 2. Factor Signals

**Momentum Signal**:
- 12-month total return
- Z-scored across 36-month rolling window
- Higher momentum = better expected returns

**Valuation Signal**:
- Inverse of recent performance
- Lower recent returns = cheaper = better value
- Z-scored across 36-month rolling window

**Combined Score**:
```
Score = 0.5 × Z(Momentum) + 0.5 × (-Z(Valuation))
```

### 3. Regime Detection

**Regimes**:
1. **Expansion**: CFNAI > 0, unemployment falling, positive growth
2. **Peak**: CFNAI high but slowing, unemployment low, potential overheating
3. **Contraction**: CFNAI < -0.3, unemployment rising, recession risk
4. **Recovery**: CFNAI improving from low levels, stabilization

**Regime Preferences** (factor tilts):

| Factor | Expansion | Peak | Contraction | Recovery |
|--------|-----------|------|-------------|----------|
| MTUM   | 1.2       | 1.0  | 0.7         | 1.3      |
| QUAL   | 1.0       | 1.2  | 1.3         | 1.0      |
| SIZE   | 1.1       | 0.8  | 0.6         | 1.2      |
| VLUE   | 0.8       | 1.0  | 0.8         | 1.1      |
| USMV   | 0.7       | 1.1  | 1.4         | 0.6      |

### 4. Risk Management

**Risk-Off Triggers**:
- SPY 12-month momentum < 0 → 50% cash
- CFNAI < -0.5 → 70% cash (max of above)

**v4A Modification**:
```python
if regime == "Recovery":
    risk_off = min(risk_off_base, 0.3)  # Cap at 30% cash
else:
    risk_off = risk_off_base
```

### 5. Portfolio Construction

Monthly rebalancing:
1. Calculate factor scores (momentum + valuation)
2. Apply regime tilts
3. Normalize to weights
4. Apply risk-off adjustment
5. Allocate: (1 - risk_off) × factor_weights + risk_off × cash

## Performance Metrics

The system calculates comprehensive performance statistics:
- **CAGR**: Compound Annual Growth Rate
- **Volatility**: Annualized standard deviation
- **Sharpe Ratio**: Risk-adjusted return
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Calmar Ratio**: CAGR / Max Drawdown
- **Sortino Ratio**: Risk-adjusted return using downside deviation
- **Win Rate**: Percentage of positive return periods

## Output Files

After running `main.py`, the following files are generated:
- `performance_stats.csv`: Summary statistics for all strategies
- `annual_returns.csv`: Year-by-year returns comparison
- `portfolio_weights_v4A.csv`: Historical portfolio weights for v4A
- `cumulative_returns.png`: Cumulative performance chart
- `annual_returns.png`: Annual returns bar chart
- `regime_timeline.png`: Economic regime visualization

## Code Examples

### Loading Data

```python
from src.data.data_loader import DataLoader

loader = DataLoader(start_date='2010-01-01')
data = loader.load_all_data()
```

### Calculating Factor Signals

```python
from src.factors.factor_signals import FactorSignals

factor_calc = FactorSignals(data['prices_m'], data['rets_m'])
momentum, z_mom, valuation, z_val = factor_calc.calculate_all_signals()
```

### Detecting Regimes

```python
from src.regime.regime_detector import RegimeDetector

detector = RegimeDetector(data['fred_m'])
regimes = detector.detect_regime_rule_based()
```

### Running Strategy

```python
from src.backtest.strategy import RegimeStrategy

strategy = RegimeStrategy(rets_m, prices_m, z_mom, z_val, regimes, fred_m)
rets_v4A, cum_v4A, stats_v4A, w_v4A = strategy.backtest_v4A()
```

## Research Notes

### v4A Rationale

During recovery periods:
- Economic indicators are improving but still negative
- Markets often anticipate recovery before economic data confirms
- Traditional risk-off rules may be overly conservative
- Opportunity cost of holding 50-70% cash during recoveries is high

**Hypothesis**: Softening risk-off during Recovery regimes should:
1. Capture more upside during early recovery phases
2. Improve CAGR without proportional increase in risk
3. Enhance Sharpe ratio through better factor exposure timing

### Potential Improvements

1. **Dynamic Regime Detection**: Use Hidden Markov Models instead of rules
2. **Adaptive Risk-Off**: Make thresholds regime-dependent
3. **Factor Timing**: Optimize momentum/valuation lookback windows
4. **Transaction Costs**: Consider more sophisticated execution models
5. **Multi-Asset**: Extend to international factors and alternative assets

## Testing

Run tests (when implemented):
```bash
pytest tests/
```

## Performance Disclaimer

This strategy is for educational and research purposes only. Past performance does not guarantee future results. Always conduct thorough testing and due diligence before deploying any investment strategy.

## Contributing

Contributions are welcome! Areas for improvement:
- Enhanced regime detection methods
- Additional factor signals
- Alternative risk management approaches
- Optimization algorithms
- Better documentation and examples

## License

MIT License - see LICENSE file for details

## Contact

For questions or feedback:
- Repository: https://github.com/woodai0120/claude
- Issues: https://github.com/woodai0120/claude/issues

## References

1. Ilmanen, A. (2011). Expected Returns: An Investor's Guide to Harvesting Market Rewards
2. Asness, C., Moskowitz, T., & Pedersen, L. (2013). Value and Momentum Everywhere
3. Faber, M. (2007). A Quantitative Approach to Tactical Asset Allocation
4. Chicago Fed National Activity Index methodology
5. Factor ETF documentation from iShares

---

**Last Updated**: 2025-11-15
**Version**: 1.0.0
