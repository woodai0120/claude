# Quick Start Guide

Get up and running with the Regime-Based Factor Allocation Strategy in 5 minutes.

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/woodai0120/claude.git
cd claude

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Run Your First Backtest

```bash
# Run the complete analysis
python main.py
```

This will:
- Download ~15 years of ETF and economic data
- Calculate factor signals (momentum & valuation)
- Detect economic regimes
- Run 5 strategies: Equal-Weight, Momentum, v3, v4A, SPY
- Generate performance charts
- Save results to CSV files

**Runtime**: ~2-3 minutes (mostly downloading data)

## View Results

After running, check these files:
- `cumulative_returns.png` - Performance comparison chart
- `annual_returns.png` - Year-by-year returns
- `regime_timeline.png` - Economic regime visualization
- `performance_stats.csv` - Detailed statistics

## Interactive Analysis

For deeper exploration:

```bash
jupyter notebook notebooks/regime_strategy_analysis.ipynb
```

This notebook provides:
- Step-by-step execution
- Interactive visualizations
- Portfolio composition analysis
- Risk metrics
- Detailed regime breakdowns

## Understanding the Output

### Performance Statistics

```
Strategy                               CAGR    Vol  Sharpe   MDD
Equal-Weight Factors                  8.5%   15.2%   0.56  -25.3%
Factor Momentum (Top2)                9.2%   14.8%   0.62  -23.1%
Regime+Val+Mom (v3)                  10.8%   13.5%   0.80  -20.5%
Regime+Val+Mom (v4A)                 11.5%   14.1%   0.82  -22.8%
SPY                                   9.1%   16.5%   0.55  -33.7%
```

Key metrics:
- **CAGR**: Annual return (higher is better)
- **Vol**: Risk/volatility (lower is better)
- **Sharpe**: Risk-adjusted return (higher is better, >0.7 is good)
- **MDD**: Maximum drawdown (lower is better)

### Understanding v4A

**What's different?**
v4A reduces cash allocation during Recovery regimes:
- v3: Up to 70% cash during recoveries (defensive)
- v4A: Maximum 30% cash during recoveries (participative)

**Why?**
Recovery periods often offer good returns but trigger risk-off signals. v4A captures more upside while maintaining protection in other regimes.

## Customization

### Change Date Range

Edit `config/config.py`:
```python
START_DATE = '2015-01-01'  # Changed from 2010
END_DATE = '2023-12-31'    # Set end date
```

### Adjust Factor Weights

Edit `config/config.py`:
```python
W_MOM = 0.7  # Increase momentum weight
W_VAL = 0.3  # Decrease value weight
```

### Modify Risk-Off Rules

Edit `config/config.py`:
```python
RISK_OFF_FRACTION = 0.4    # Changed from 0.5
CFNAI_RISK_OFF = 0.6       # Changed from 0.7
```

### Change Factor ETFs

Edit `config/config.py`:
```python
FACTOR_ETFS = [
    'MTUM',  # Momentum
    'QUAL',  # Quality
    'VLUE',  # Value
    # 'SIZE',  # Removed: Size
    # 'USMV',  # Removed: Low Vol
]
```

## Next Steps

1. **Explore the Code**
   - `src/data/data_loader.py` - Data downloading
   - `src/factors/factor_signals.py` - Signal calculation
   - `src/regime/regime_detector.py` - Regime detection
   - `src/backtest/strategy.py` - Main strategy logic

2. **Read Documentation**
   - `README.md` - Comprehensive overview
   - `V4A_CODE_REVIEW.md` - Detailed v4A analysis
   - `CLAUDE.md` - AI assistant guide

3. **Experiment**
   - Try different parameters
   - Add new factors
   - Test different regimes
   - Implement your ideas

4. **Backtest on Your Data**
   ```python
   from src.data.data_loader import DataLoader

   loader = DataLoader(start_date='2020-01-01')
   data = loader.load_all_data()
   # ... run your analysis
   ```

## Troubleshooting

### Data Download Fails
```bash
# Check internet connection
# Try running again (Yahoo Finance can be flaky)
python main.py
```

### Import Errors
```bash
# Make sure you're in the project directory
cd /path/to/claude

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Missing FRED Data
```bash
# FRED API has rate limits
# Wait 1 minute and try again
# Or use your own API key (optional)
```

### Plot Not Showing (Jupyter)
```python
# Add to first cell
%matplotlib inline
import matplotlib.pyplot as plt
```

## Getting Help

- **Issues**: https://github.com/woodai0120/claude/issues
- **Documentation**: See README.md
- **Code Review**: See V4A_CODE_REVIEW.md

## Example Session

```bash
# 1. Fresh start
cd ~/projects
git clone https://github.com/woodai0120/claude.git
cd claude

# 2. Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run backtest
python main.py

# 4. Check results
ls -lh *.png *.csv

# 5. View in Jupyter
jupyter notebook notebooks/regime_strategy_analysis.ipynb

# 6. Celebrate! 🎉
```

---

**Happy backtesting!** 📈

For questions or feedback, open an issue on GitHub.
