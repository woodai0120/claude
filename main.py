"""
Main script to run regime-based factor allocation strategy
Compares v3 (baseline) with v4A (Recovery softened)
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.append('/home/user/claude')

from src.data.data_loader import DataLoader
from src.factors.factor_signals import FactorSignals
from src.regime.regime_detector import RegimeDetector, smooth_regimes
from src.backtest.strategy import RegimeStrategy, BaselineStrategies
from src.utils.performance import annual_returns

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


def main():
    """Main execution function"""

    print("=" * 80)
    print("REGIME-BASED FACTOR ALLOCATION STRATEGY")
    print("v3 (Baseline) vs v4A (Recovery Risk-off Softened)")
    print("=" * 80)

    # ==================== STEP 1: Load Data ====================
    print("\n[STEP 1] Loading data...")
    loader = DataLoader()
    data = loader.load_all_data()

    prices_d = data['prices_d']
    prices_m = data['prices_m']
    rets_m = data['rets_m']
    fred_m = data['fred_m']

    print(f"  Loaded {len(prices_m)} months of data ({prices_m.index[0].date()} to {prices_m.index[-1].date()})")

    # ==================== STEP 2: Calculate Factor Signals ====================
    print("\n[STEP 2] Calculating factor signals...")
    factor_calc = FactorSignals(prices_m, rets_m)
    momentum, z_mom, valuation, z_val = factor_calc.calculate_all_signals()

    print(f"  Momentum signals: {z_mom.shape}")
    print(f"  Valuation signals: {z_val.shape}")

    # ==================== STEP 3: Detect Regimes ====================
    print("\n[STEP 3] Detecting economic regimes...")
    detector = RegimeDetector(fred_m)
    regimes_raw = detector.detect_regime_rule_based()
    regimes = smooth_regimes(regimes_raw, min_duration=3)

    print(f"  Regime distribution:")
    for regime, count in regimes.value_counts().items():
        pct = count / len(regimes) * 100
        print(f"    {regime}: {count} months ({pct:.1f}%)")

    # ==================== STEP 4: Run Baseline Strategies ====================
    print("\n[STEP 4] Running baseline strategies...")

    baselines = BaselineStrategies(rets_m, prices_m)

    rets_eq, cum_eq, stats_eq = baselines.equal_weight()
    print(f"  ✓ Equal-Weight")

    rets_mom, cum_mom, stats_mom = baselines.momentum_top2()
    print(f"  ✓ Momentum Top-2")

    rets_spy, cum_spy, stats_spy = baselines.buy_and_hold_spy()
    print(f"  ✓ SPY Buy & Hold")

    # ==================== STEP 5: Run Regime Strategies ====================
    print("\n[STEP 5] Running regime-based strategies...")

    strategy = RegimeStrategy(rets_m, prices_m, z_mom, z_val, regimes, fred_m)

    rets_v3, cum_v3, stats_v3, w_v3 = strategy.backtest_v3()
    print(f"  ✓ v3 (Baseline)")

    rets_v4A, cum_v4A, stats_v4A, w_v4A = strategy.backtest_v4A()
    print(f"  ✓ v4A (Recovery Softened)")

    # ==================== STEP 6: Compare Results ====================
    print("\n[STEP 6] Performance comparison:")
    print("=" * 80)

    stats_df = pd.DataFrame([
        stats_eq,
        stats_mom,
        stats_v3,
        stats_v4A,
        stats_spy,
    ])

    # Format and display
    print(stats_df.to_string(index=False, float_format=lambda x: f'{x:.4f}'))

    # ==================== STEP 7: Visualizations ====================
    print("\n[STEP 7] Generating visualizations...")

    # Plot 1: Cumulative returns
    fig, ax = plt.subplots(figsize=(14, 7))
    cum_eq.plot(ax=ax, label="Equal-Weight Factors", linewidth=2)
    cum_mom.plot(ax=ax, label="Factor Momentum (Top2)", linewidth=2)
    cum_v3.plot(ax=ax, label="Regime+Val+Mom (v3)", linewidth=2.5)
    cum_v4A.plot(ax=ax, label="Regime+Val+Mom (v4A)", linewidth=2.5, linestyle='--')
    cum_spy.plot(ax=ax, label="SPY", linewidth=2, linestyle=':', alpha=0.7)

    ax.set_title("Cumulative Returns Comparison (v3 vs v4A)", fontsize=16, fontweight='bold')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Cumulative Return", fontsize=12)
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/home/user/claude/cumulative_returns.png', dpi=150)
    print("  ✓ Saved: cumulative_returns.png")

    # Plot 2: Annual returns comparison
    ann_eq = annual_returns(rets_eq).rename("Equal-Weight")
    ann_mom = annual_returns(rets_mom).rename("Momentum Top2")
    ann_v3 = annual_returns(rets_v3).rename("v3")
    ann_v4A = annual_returns(rets_v4A).rename("v4A")
    ann_spy = annual_returns(rets_spy).rename("SPY")

    ann_compare = pd.concat([ann_eq, ann_mom, ann_v3, ann_v4A, ann_spy], axis=1).fillna(0.0)

    fig, ax = plt.subplots(figsize=(14, 7))
    ann_compare.plot(kind='bar', ax=ax, width=0.8)
    ax.set_title("Annual Returns by Year (including v4A)", fontsize=16, fontweight='bold')
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Return", fontsize=12)
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linewidth=0.8)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/home/user/claude/annual_returns.png', dpi=150)
    print("  ✓ Saved: annual_returns.png")

    # Plot 3: Regime timeline
    fig, ax = plt.subplots(figsize=(14, 4))
    regime_colors = {
        'Expansion': 'green',
        'Peak': 'orange',
        'Contraction': 'red',
        'Recovery': 'blue',
        'Unknown': 'gray'
    }

    for i, (date, regime) in enumerate(regimes.items()):
        ax.axvspan(date, regimes.index[i+1] if i < len(regimes)-1 else date,
                  color=regime_colors.get(regime, 'gray'), alpha=0.3)

    ax.set_title("Economic Regime Timeline", fontsize=16, fontweight='bold')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_yticks([])

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color, alpha=0.3, label=regime)
                      for regime, color in regime_colors.items() if regime != 'Unknown']
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    plt.tight_layout()
    plt.savefig('/home/user/claude/regime_timeline.png', dpi=150)
    print("  ✓ Saved: regime_timeline.png")

    # ==================== STEP 8: Save Results ====================
    print("\n[STEP 8] Saving results...")

    # Save statistics
    stats_df.to_csv('/home/user/claude/performance_stats.csv', index=False)
    print("  ✓ Saved: performance_stats.csv")

    # Save annual returns
    ann_compare.to_csv('/home/user/claude/annual_returns.csv')
    print("  ✓ Saved: annual_returns.csv")

    # Save weights
    w_v4A.to_csv('/home/user/claude/portfolio_weights_v4A.csv')
    print("  ✓ Saved: portfolio_weights_v4A.csv")

    print("\n" + "=" * 80)
    print("EXECUTION COMPLETE")
    print("=" * 80)
    print(f"\nKey Findings:")
    print(f"  v3 CAGR:  {stats_v3['CAGR']:.2%}  |  Sharpe: {stats_v3['Sharpe']:.2f}  |  MDD: {stats_v3['MDD']:.2%}")
    print(f"  v4A CAGR: {stats_v4A['CAGR']:.2%}  |  Sharpe: {stats_v4A['Sharpe']:.2f}  |  MDD: {stats_v4A['MDD']:.2%}")
    print(f"  SPY CAGR: {stats_spy['CAGR']:.2%}  |  Sharpe: {stats_spy['Sharpe']:.2f}  |  MDD: {stats_spy['MDD']:.2%}")

    diff_cagr = stats_v4A['CAGR'] - stats_v3['CAGR']
    diff_sharpe = stats_v4A['Sharpe'] - stats_v3['Sharpe']
    print(f"\nv4A vs v3 Improvement:")
    print(f"  CAGR:   {diff_cagr:+.2%}")
    print(f"  Sharpe: {diff_sharpe:+.2f}")

    return {
        'stats_df': stats_df,
        'ann_compare': ann_compare,
        'w_v4A': w_v4A,
        'regimes': regimes,
    }


if __name__ == "__main__":
    results = main()
