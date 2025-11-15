"""
Main strategy implementation
Includes v3 (baseline) and v4A (Recovery regime softened) versions
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict

import sys
sys.path.append('/home/user/claude')
from config.config import (
    FACTOR_ETFS, CASH_ETF, BENCH, W_MOM, W_VAL,
    RISK_OFF_FRACTION, CFNAI_RISK_OFF, TC_BPS, REGIME_PREFS
)
from src.utils.performance import ann_stats, annual_returns


class RegimeStrategy:
    """
    Regime-based factor allocation strategy
    """

    def __init__(self, rets_m: pd.DataFrame, prices_m: pd.DataFrame,
                 z_mom: pd.DataFrame, z_val: pd.DataFrame,
                 regimes: pd.Series, cfnai_m: pd.DataFrame):
        """
        Initialize strategy with required data

        Args:
            rets_m: Monthly returns
            prices_m: Monthly prices
            z_mom: Z-scored momentum signals
            z_val: Z-scored valuation signals
            regimes: Regime classifications
            cfnai_m: CFNAI economic indicator
        """
        self.rets_m = rets_m
        self.prices_m = prices_m
        self.z_mom = z_mom
        self.z_val = z_val
        self.regimes = regimes
        self.cfnai_m = cfnai_m

    def calculate_factor_scores(self, dt: pd.Timestamp) -> pd.Series:
        """
        Calculate combined factor scores

        Args:
            dt: Date for score calculation

        Returns:
            Series of factor scores
        """
        # Get signals
        zm = self.z_mom.loc[dt] if dt in self.z_mom.index else pd.Series(index=FACTOR_ETFS, dtype=float)
        zv = self.z_val.loc[dt] if dt in self.z_val.index else pd.Series(index=FACTOR_ETFS, dtype=float)

        # Check if all NaN
        if (zm.isna().all() if len(zm) > 0 else True) and (zv.isna().all() if len(zv) > 0 else True):
            return pd.Series(0.0, index=FACTOR_ETFS)

        # Combine signals
        if zv.isna().all():
            score_raw = zm
        elif zm.isna().all():
            score_raw = -zv
        else:
            score_raw = W_MOM * zm + W_VAL * (-zv)

        return score_raw

    def apply_regime_tilt(self, scores: pd.Series, regime: str) -> pd.Series:
        """
        Apply regime-based tilts to factor scores

        Args:
            scores: Raw factor scores
            regime: Current regime

        Returns:
            Tilted factor scores
        """
        prefs = REGIME_PREFS.get(regime, REGIME_PREFS["Unknown"])
        reg_w = pd.Series([prefs[f] for f in FACTOR_ETFS], index=FACTOR_ETFS)

        return scores * reg_w

    def calculate_risk_off(self, dt: pd.Timestamp, regime: str, version: str = 'v3') -> float:
        """
        Calculate risk-off allocation (cash weight)

        Args:
            dt: Current date
            regime: Current regime
            version: 'v3' for baseline, 'v4A' for Recovery softened

        Returns:
            Cash allocation fraction
        """
        risk_off_base = 0.0

        # SPY 12-month momentum check
        spy_mom = self.prices_m[BENCH].pct_change(12)
        if dt in spy_mom.index and not pd.isna(spy_mom.loc[dt]):
            if spy_mom.loc[dt] < 0:
                risk_off_base = RISK_OFF_FRACTION  # 0.5

        # CFNAI check
        c_val = self.cfnai_m.loc[dt, "CFNAI"] if dt in self.cfnai_m.index and "CFNAI" in self.cfnai_m.columns else np.nan
        if not pd.isna(c_val) and c_val < -0.5:
            risk_off_base = max(risk_off_base, CFNAI_RISK_OFF)  # 0.7

        # v4A modification: cap risk-off in Recovery regime
        if version == 'v4A' and regime == 'Recovery':
            risk_off = min(risk_off_base, 0.3)  # Max 30% cash in Recovery
        else:
            risk_off = risk_off_base

        return risk_off

    def backtest_v3(self) -> Tuple[pd.Series, pd.Series, Dict, pd.DataFrame]:
        """
        Backtest v3 strategy (baseline with full risk-off)

        Returns:
            Tuple of (net_returns, cumulative, stats, weights)
        """
        return self._backtest_core(version='v3', name='Regime+Val+Mom (v3)')

    def backtest_v4A(self) -> Tuple[pd.Series, pd.Series, Dict, pd.DataFrame]:
        """
        Backtest v4A strategy (Recovery regime risk-off softened)

        Returns:
            Tuple of (net_returns, cumulative, stats, weights)
        """
        return self._backtest_core(version='v4A', name='Regime+Val+Mom (v4A: Recovery softened)')

    def _backtest_core(self, version: str, name: str) -> Tuple[pd.Series, pd.Series, Dict, pd.DataFrame]:
        """
        Core backtesting logic

        Args:
            version: 'v3' or 'v4A'
            name: Strategy name for reporting

        Returns:
            Tuple of (net_returns, cumulative, stats, weights)
        """
        # Initialize weights DataFrame
        all_columns = FACTOR_ETFS + [CASH_ETF]
        w = pd.DataFrame(index=self.rets_m.index, columns=all_columns, data=0.0)

        prev_w = None
        turnovers = []
        first = True

        # Loop through all dates
        for dt in self.rets_m.index:
            # Get current regime
            regime = self.regimes.loc[dt] if dt in self.regimes.index else "Unknown"

            # Calculate factor scores
            score_raw = self.calculate_factor_scores(dt)

            # Apply regime tilt
            score = self.apply_regime_tilt(score_raw, regime)

            # Normalize to weights
            score = score.clip(lower=0.0)
            if score.sum() == 0 or score.isna().all():
                factor_weights = pd.Series(1.0 / len(FACTOR_ETFS), index=FACTOR_ETFS)
            else:
                factor_weights = score / score.sum()

            # Calculate risk-off
            risk_off = self.calculate_risk_off(dt, regime, version)

            # Construct portfolio weights
            w_row = pd.Series(0.0, index=all_columns)
            w_row[FACTOR_ETFS] = factor_weights * (1 - risk_off)
            w_row[CASH_ETF] = risk_off

            # Calculate turnover
            if first:
                to = w_row.abs().sum()
                first = False
            else:
                to = (w_row - prev_w).abs().sum()

            turnovers.append(to)
            prev_w = w_row
            w.loc[dt] = w_row

        # Forward fill and fill NaN
        w = w.ffill().fillna(0.0)

        # Calculate returns
        gross = (w[FACTOR_ETFS] * self.rets_m[FACTOR_ETFS]).sum(axis=1) + \
                w[CASH_ETF] * self.rets_m[CASH_ETF]

        # Transaction costs
        tc = pd.Series(turnovers, index=w.index[:len(turnovers)]) * (TC_BPS / 10000.0)
        tc = tc.reindex(gross.index).fillna(0.0)

        # Net returns
        net = gross - tc

        # Cumulative returns
        cum = (1 + net).cumprod()

        # Statistics
        stats = ann_stats(cum, net, name)

        return net, cum, stats, w


class BaselineStrategies:
    """Baseline strategies for comparison"""

    def __init__(self, rets_m: pd.DataFrame, prices_m: pd.DataFrame):
        """
        Initialize with return and price data

        Args:
            rets_m: Monthly returns
            prices_m: Monthly prices
        """
        self.rets_m = rets_m
        self.prices_m = prices_m

    def equal_weight(self) -> Tuple[pd.Series, pd.Series, Dict]:
        """
        Equal-weight factor allocation

        Returns:
            Tuple of (returns, cumulative, stats)
        """
        # Equal weights across factors
        w = 1.0 / len(FACTOR_ETFS)
        rets = (self.rets_m[FACTOR_ETFS] * w).sum(axis=1)
        cum = (1 + rets).cumprod()
        stats = ann_stats(cum, rets, "Equal-Weight Factors")

        return rets, cum, stats

    def momentum_top2(self, lookback: int = 12) -> Tuple[pd.Series, pd.Series, Dict]:
        """
        Select top 2 factors by momentum

        Args:
            lookback: Momentum lookback period in months

        Returns:
            Tuple of (returns, cumulative, stats)
        """
        # Calculate momentum
        mom = self.prices_m[FACTOR_ETFS].pct_change(lookback)

        # Allocate to top 2
        w = pd.DataFrame(0.0, index=self.rets_m.index, columns=FACTOR_ETFS)

        for dt in mom.index:
            if dt not in w.index:
                continue

            row = mom.loc[dt]
            if row.isna().all():
                w.loc[dt] = 1.0 / len(FACTOR_ETFS)
            else:
                top2 = row.nlargest(2).index
                w.loc[dt, top2] = 0.5

        # Calculate returns
        rets = (w * self.rets_m[FACTOR_ETFS]).sum(axis=1)
        cum = (1 + rets).cumprod()
        stats = ann_stats(cum, rets, "Factor Momentum (Top2)")

        return rets, cum, stats

    def buy_and_hold_spy(self) -> Tuple[pd.Series, pd.Series, Dict]:
        """
        Buy and hold SPY

        Returns:
            Tuple of (returns, cumulative, stats)
        """
        rets = self.rets_m[BENCH]
        cum = (1 + rets).cumprod()
        stats = ann_stats(cum, rets, "SPY")

        return rets, cum, stats


if __name__ == "__main__":
    # This will be tested in the main script
    print("Strategy module loaded successfully")
