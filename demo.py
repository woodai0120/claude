"""
Demo script with synthetic data to showcase the strategy
Works without external data downloads
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.append('/home/user/claude')

from config.config import FACTOR_ETFS, CASH_ETF, BENCH
from src.backtest.strategy import RegimeStrategy, BaselineStrategies
from src.utils.performance import annual_returns

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# Set random seed for reproducibility
np.random.seed(42)


def generate_synthetic_data(start_date='2010-01-01', periods=168):
    """Generate synthetic monthly data for demonstration"""

    print("Generating synthetic market data...")

    # Date range
    dates = pd.date_range(start_date, periods=periods, freq='M')

    # Generate prices with realistic characteristics
    tickers = FACTOR_ETFS + [BENCH, CASH_ETF]

    # Initial prices
    prices = pd.DataFrame(100.0, index=dates, columns=tickers)

    # Generate returns with different characteristics for each factor
    for i in range(1, len(dates)):
        # MTUM: Higher momentum, more volatile
        prices.loc[dates[i], 'MTUM'] = prices.loc[dates[i-1], 'MTUM'] * (1 + np.random.normal(0.008, 0.05))

        # QUAL: Stable, moderate returns
        prices.loc[dates[i], 'QUAL'] = prices.loc[dates[i-1], 'QUAL'] * (1 + np.random.normal(0.007, 0.03))

        # SIZE: Small cap, higher volatility
        prices.loc[dates[i], 'SIZE'] = prices.loc[dates[i-1], 'SIZE'] * (1 + np.random.normal(0.009, 0.06))

        # VLUE: Value factor, mean-reverting
        prices.loc[dates[i], 'VLUE'] = prices.loc[dates[i-1], 'VLUE'] * (1 + np.random.normal(0.006, 0.04))

        # USMV: Low volatility, defensive
        prices.loc[dates[i], 'USMV'] = prices.loc[dates[i-1], 'USMV'] * (1 + np.random.normal(0.005, 0.02))

        # SPY: Market benchmark
        prices.loc[dates[i], 'SPY'] = prices.loc[dates[i-1], 'SPY'] * (1 + np.random.normal(0.007, 0.04))

        # BIL: Cash, low return, minimal volatility
        prices.loc[dates[i], 'BIL'] = prices.loc[dates[i-1], 'BIL'] * (1 + 0.0015)  # ~1.8% annual

    # Calculate returns
    rets = prices.pct_change().fillna(0.0)

    # Generate economic indicators (CFNAI-like)
    cfnai = pd.DataFrame(index=dates)
    cfnai['CFNAI'] = np.random.normal(0.0, 0.5, len(dates))

    # Add some structure: cycles of expansion and contraction
    for i in range(len(dates)):
        month = i % 48  # 4-year cycle
        if month < 24:  # Expansion
            cfnai.loc[dates[i], 'CFNAI'] = np.random.normal(0.3, 0.3)
        else:  # Slowdown/contraction
            cfnai.loc[dates[i], 'CFNAI'] = np.random.normal(-0.2, 0.4)

    # Smooth CFNAI
    cfnai['CFNAI'] = cfnai['CFNAI'].rolling(3).mean().fillna(0.0)

    # Generate regimes based on CFNAI
    regimes = pd.Series('Unknown', index=dates)

    cfnai_change = cfnai['CFNAI'].diff(3)

    for i, date in enumerate(dates):
        c = cfnai.loc[date, 'CFNAI']
        c_chg = cfnai_change.loc[date] if date in cfnai_change.index else 0

        if c < -0.3:
            regimes[date] = 'Contraction'
        elif c < 0 and c_chg > 0:
            regimes[date] = 'Recovery'
        elif c > 0.2:
            regimes[date] = 'Expansion'
        elif c > 0:
            regimes[date] = 'Peak'
        else:
            regimes[date] = 'Unknown'

    # Forward fill
    regimes = regimes.replace('Unknown', np.nan).ffill().fillna('Expansion')

    print(f"  Generated {len(prices)} months of data")
    print(f"  Date range: {dates[0].date()} to {dates[-1].date()}")
    print(f"  Regime distribution:")
    for regime, count in regimes.value_counts().items():
        print(f"    {regime}: {count} months ({count/len(regimes)*100:.1f}%)")

    return prices, rets, cfnai, regimes


def calculate_simple_signals(prices, rets):
    """Calculate simplified momentum and valuation signals"""

    print("\nCalculating factor signals...")

    # Momentum: 12-month return
    momentum = prices[FACTOR_ETFS].pct_change(12)

    # Z-score momentum (36-month rolling)
    z_mom = pd.DataFrame(index=momentum.index, columns=FACTOR_ETFS)
    for col in FACTOR_ETFS:
        rolling_mean = momentum[col].rolling(36).mean()
        rolling_std = momentum[col].rolling(36).std()
        z_mom[col] = (momentum[col] - rolling_mean) / rolling_std

    # Valuation: inverse of recent performance
    valuation = prices[FACTOR_ETFS].pct_change(12)

    # Z-score valuation
    z_val = pd.DataFrame(index=valuation.index, columns=FACTOR_ETFS)
    for col in FACTOR_ETFS:
        rolling_mean = valuation[col].rolling(36).mean()
        rolling_std = valuation[col].rolling(36).std()
        z_val[col] = (valuation[col] - rolling_mean) / rolling_std

    z_mom = z_mom.fillna(0.0)
    z_val = z_val.fillna(0.0)

    print(f"  Calculated signals for {len(z_mom)} periods")

    return z_mom, z_val


def main():
    """Main demo execution"""

    print("=" * 80)
    print("REGIME-BASED FACTOR ALLOCATION STRATEGY - DEMO")
    print("Synthetic Data Demonstration")
    print("=" * 80)

    # Generate synthetic data
    prices, rets, cfnai, regimes = generate_synthetic_data(periods=168)  # 14 years

    # Calculate signals
    z_mom, z_val = calculate_simple_signals(prices, rets)

    # Run baseline strategies
    print("\n[STEP 1] Running baseline strategies...")

    baselines = BaselineStrategies(rets, prices)

    rets_eq, cum_eq, stats_eq = baselines.equal_weight()
    print("  ✓ Equal-Weight")

    rets_mom, cum_mom, stats_mom = baselines.momentum_top2()
    print("  ✓ Momentum Top-2")

    rets_spy, cum_spy, stats_spy = baselines.buy_and_hold_spy()
    print("  ✓ SPY Buy & Hold")

    # Run regime strategies
    print("\n[STEP 2] Running regime-based strategies...")

    strategy = RegimeStrategy(rets, prices, z_mom, z_val, regimes, cfnai)

    rets_v3, cum_v3, stats_v3, w_v3 = strategy.backtest_v3()
    print("  ✓ v3 (Baseline)")

    rets_v4A, cum_v4A, stats_v4A, w_v4A = strategy.backtest_v4A()
    print("  ✓ v4A (Recovery Softened)")

    # Performance comparison
    print("\n[STEP 3] Performance Comparison:")
    print("=" * 80)

    stats_df = pd.DataFrame([stats_eq, stats_mom, stats_v3, stats_v4A, stats_spy])

    print(stats_df.to_string(index=False))

    # Generate visualizations
    print("\n[STEP 4] Generating visualizations...")

    # Plot 1: Cumulative returns
    fig, ax = plt.subplots(figsize=(14, 7))
    cum_eq.plot(ax=ax, label="Equal-Weight Factors", linewidth=2)
    cum_mom.plot(ax=ax, label="Factor Momentum (Top2)", linewidth=2)
    cum_v3.plot(ax=ax, label="Regime+Val+Mom (v3)", linewidth=2.5)
    cum_v4A.plot(ax=ax, label="Regime+Val+Mom (v4A)", linewidth=2.5, linestyle='--')
    cum_spy.plot(ax=ax, label="SPY", linewidth=2, linestyle=':', alpha=0.7)

    ax.set_title("Cumulative Returns Comparison (Demo Data)", fontsize=16, fontweight='bold')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Cumulative Return", fontsize=12)
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/home/user/claude/demo_cumulative_returns.png', dpi=150, bbox_inches='tight')
    print("  ✓ Saved: demo_cumulative_returns.png")
    plt.close()

    # Plot 2: Cash allocation comparison
    fig, ax = plt.subplots(figsize=(14, 6))
    w_v3['BIL'].plot(ax=ax, label='v3 Cash', linewidth=2, alpha=0.7)
    w_v4A['BIL'].plot(ax=ax, label='v4A Cash', linewidth=2, linestyle='--')

    # Highlight Recovery regimes
    regime_colors = {
        'Expansion': 'green',
        'Peak': 'orange',
        'Contraction': 'red',
        'Recovery': 'blue',
    }

    for i, (date, regime) in enumerate(regimes.items()):
        if regime == 'Recovery':
            next_date = regimes.index[i+1] if i < len(regimes)-1 else date
            ax.axvspan(date, next_date, color='blue', alpha=0.1)

    ax.set_title("Cash Allocation: v3 vs v4A (Recovery periods in blue)",
                fontsize=16, fontweight='bold')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Cash Weight", fontsize=12)
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/home/user/claude/demo_cash_allocation.png', dpi=150, bbox_inches='tight')
    print("  ✓ Saved: demo_cash_allocation.png")
    plt.close()

    # Plot 3: Regime timeline
    fig, ax = plt.subplots(figsize=(14, 4))

    for i, (date, regime) in enumerate(regimes.items()):
        next_date = regimes.index[i+1] if i < len(regimes)-1 else date
        ax.axvspan(date, next_date, color=regime_colors.get(regime, 'gray'), alpha=0.3)

    ax.set_title("Economic Regime Timeline (Demo Data)", fontsize=16, fontweight='bold')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_yticks([])

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color, alpha=0.3, label=regime)
                      for regime, color in regime_colors.items()]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    plt.tight_layout()
    plt.savefig('/home/user/claude/demo_regime_timeline.png', dpi=150, bbox_inches='tight')
    print("  ✓ Saved: demo_regime_timeline.png")
    plt.close()

    # Save results
    print("\n[STEP 5] Saving results...")
    stats_df.to_csv('/home/user/claude/demo_performance_stats.csv', index=False)
    print("  ✓ Saved: demo_performance_stats.csv")

    print("\n" + "=" * 80)
    print("DEMO EXECUTION COMPLETE")
    print("=" * 80)
    print(f"\nKey Findings (Synthetic Data):")
    print(f"  v3 CAGR:  {stats_v3['CAGR']:.2%}  |  Sharpe: {stats_v3['Sharpe']:.2f}  |  MDD: {stats_v3['MDD']:.2%}")
    print(f"  v4A CAGR: {stats_v4A['CAGR']:.2%}  |  Sharpe: {stats_v4A['Sharpe']:.2f}  |  MDD: {stats_v4A['MDD']:.2%}")
    print(f"  SPY CAGR: {stats_spy['CAGR']:.2%}  |  Sharpe: {stats_spy['Sharpe']:.2f}  |  MDD: {stats_spy['MDD']:.2%}")

    diff_cagr = stats_v4A['CAGR'] - stats_v3['CAGR']
    diff_sharpe = stats_v4A['Sharpe'] - stats_v3['Sharpe']
    print(f"\nv4A vs v3 Improvement:")
    print(f"  CAGR:   {diff_cagr:+.2%}")
    print(f"  Sharpe: {diff_sharpe:+.2f}")

    print("\nNote: This demo uses synthetic data for demonstration purposes.")
    print("With real market data, results will vary based on actual market conditions.")

    return stats_df


if __name__ == "__main__":
    results = main()
