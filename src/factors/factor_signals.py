"""
Factor signal calculation module
Implements momentum and valuation signals
"""
import pandas as pd
import numpy as np
from typing import Tuple

import sys
sys.path.append('/home/user/claude')
from config.config import FACTOR_ETFS, MOM_LOOKBACK_M, VAL_LOOKBACK_M


class FactorSignals:
    """Calculate factor signals for portfolio construction"""

    def __init__(self, prices_m: pd.DataFrame, rets_m: pd.DataFrame):
        """
        Initialize with monthly price and return data

        Args:
            prices_m: Monthly prices DataFrame
            rets_m: Monthly returns DataFrame
        """
        self.prices_m = prices_m
        self.rets_m = rets_m

    def calculate_momentum(self, lookback: int = MOM_LOOKBACK_M) -> pd.DataFrame:
        """
        Calculate momentum signal (total return over lookback period)

        Args:
            lookback: Lookback period in months

        Returns:
            DataFrame with momentum values for each factor ETF
        """
        # Calculate total return over lookback period
        momentum = self.prices_m[FACTOR_ETFS].pct_change(lookback)

        return momentum

    def calculate_valuation(self, lookback: int = VAL_LOOKBACK_M) -> pd.DataFrame:
        """
        Calculate valuation signal (inverse of recent performance)
        Lower recent returns = cheaper = better value

        Args:
            lookback: Lookback period in months

        Returns:
            DataFrame with valuation values (lower is better)
        """
        # Use rolling return as proxy for valuation
        # Higher recent returns = more expensive = higher valuation
        valuation = self.prices_m[FACTOR_ETFS].pct_change(lookback)

        return valuation

    def calculate_z_scores(self, signal: pd.DataFrame, window: int = 36) -> pd.DataFrame:
        """
        Calculate rolling z-scores for signals

        Args:
            signal: Input signal DataFrame
            window: Rolling window for z-score calculation

        Returns:
            DataFrame with z-scored signals
        """
        z_scores = pd.DataFrame(index=signal.index, columns=signal.columns)

        for col in signal.columns:
            rolling_mean = signal[col].rolling(window=window).mean()
            rolling_std = signal[col].rolling(window=window).std()
            z_scores[col] = (signal[col] - rolling_mean) / rolling_std

        return z_scores

    def calculate_all_signals(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Calculate all factor signals

        Returns:
            Tuple of (momentum, z_momentum, valuation, z_valuation)
        """
        # Calculate raw signals
        momentum = self.calculate_momentum()
        valuation = self.calculate_valuation()

        # Calculate z-scores
        z_momentum = self.calculate_z_scores(momentum)
        z_valuation = self.calculate_z_scores(valuation)

        return momentum, z_momentum, valuation, z_valuation


def rank_factors(signals: pd.DataFrame, top_n: int = 2) -> pd.DataFrame:
    """
    Rank factors by signal strength

    Args:
        signals: DataFrame with factor signals
        top_n: Number of top factors to select

    Returns:
        DataFrame with 1/0 weights for top factors
    """
    weights = pd.DataFrame(0, index=signals.index, columns=signals.columns)

    for date in signals.index:
        row = signals.loc[date]
        if row.isna().all():
            continue

        # Rank and select top N
        ranked = row.rank(ascending=False, na_option='bottom')
        weights.loc[date, ranked <= top_n] = 1.0 / top_n

    return weights


def cross_sectional_zscore(signals: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate cross-sectional z-scores (across factors at each time point)

    Args:
        signals: DataFrame with factor signals

    Returns:
        DataFrame with cross-sectional z-scores
    """
    z_scores = signals.copy()

    for date in signals.index:
        row = signals.loc[date]
        if row.isna().all():
            continue

        mean = row.mean()
        std = row.std()

        if std > 0:
            z_scores.loc[date] = (row - mean) / std
        else:
            z_scores.loc[date] = 0.0

    return z_scores


if __name__ == "__main__":
    # Test factor signal calculation
    from src.data.data_loader import DataLoader

    loader = DataLoader()
    data = loader.load_all_data()

    factor_calc = FactorSignals(data['prices_m'], data['rets_m'])
    momentum, z_mom, valuation, z_val = factor_calc.calculate_all_signals()

    print("\n=== Factor Signals Summary ===")
    print(f"Momentum shape: {momentum.shape}")
    print(f"Z-Momentum shape: {z_mom.shape}")
    print(f"Valuation shape: {valuation.shape}")
    print(f"Z-Valuation shape: {z_val.shape}")

    print("\nLatest Momentum:")
    print(momentum.tail())

    print("\nLatest Z-Momentum:")
    print(z_mom.tail())
