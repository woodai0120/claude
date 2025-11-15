"""
Economic regime detection module
Identifies market regimes: Expansion, Peak, Contraction, Recovery
"""
import pandas as pd
import numpy as np
from typing import Optional

import sys
sys.path.append('/home/user/claude')
from config.config import REGIME_PARAMS


class RegimeDetector:
    """Detect economic regimes based on macro indicators"""

    def __init__(self, fred_data: pd.DataFrame):
        """
        Initialize with FRED economic data

        Args:
            fred_data: DataFrame with economic indicators (CFNAI, UNRATE, T10Y2Y)
        """
        self.fred_data = fred_data

    def detect_regime_rule_based(self) -> pd.Series:
        """
        Detect regime using rule-based approach

        Rules:
        - Expansion: CFNAI > 0, unemployment falling, yield curve normal
        - Peak: CFNAI high but slowing, unemployment low, yield curve flattening
        - Contraction: CFNAI < -0.3, unemployment rising, yield curve inverted
        - Recovery: CFNAI improving from low, unemployment stabilizing

        Returns:
            Series with regime labels
        """
        regimes = pd.Series('Unknown', index=self.fred_data.index)

        # Calculate derived indicators
        cfnai = self.fred_data.get('CFNAI', pd.Series(index=self.fred_data.index))
        unrate = self.fred_data.get('UNRATE', pd.Series(index=self.fred_data.index))
        yield_curve = self.fred_data.get('T10Y2Y', pd.Series(index=self.fred_data.index))

        # CFNAI change
        cfnai_change = cfnai.diff(3)  # 3-month change

        # Unemployment change
        unrate_change = unrate.diff(3)  # 3-month change

        for date in self.fred_data.index:
            c = cfnai.get(date, np.nan) if date in cfnai.index else np.nan
            c_chg = cfnai_change.get(date, np.nan) if date in cfnai_change.index else np.nan
            u_chg = unrate_change.get(date, np.nan) if date in unrate_change.index else np.nan
            yc = yield_curve.get(date, np.nan) if date in yield_curve.index else np.nan

            # Skip if too much missing data
            if pd.isna([c, c_chg, u_chg]).sum() >= 2:
                continue

            # Contraction: negative CFNAI and rising unemployment
            if (not pd.isna(c) and c < REGIME_PARAMS['cfnai_contraction']) and \
               (pd.isna(u_chg) or u_chg > 0):
                regimes[date] = 'Contraction'

            # Recovery: improving from low CFNAI
            elif (not pd.isna(c) and c < 0) and \
                 (not pd.isna(c_chg) and c_chg > 0):
                regimes[date] = 'Recovery'

            # Expansion: positive CFNAI and stable/falling unemployment
            elif (not pd.isna(c) and c > REGIME_PARAMS['cfnai_expansion']) and \
                 (pd.isna(u_chg) or u_chg <= 0):
                regimes[date] = 'Expansion'

            # Peak: positive but slowing, or yield curve issues
            elif (not pd.isna(c) and c > 0) and \
                 (not pd.isna(c_chg) and c_chg < 0):
                regimes[date] = 'Peak'

            # Default to Unknown
            else:
                regimes[date] = 'Unknown'

        # Forward fill regimes
        regimes = regimes.replace('Unknown', np.nan).ffill().fillna('Unknown')

        return regimes

    def detect_regime_hmm(self) -> pd.Series:
        """
        Detect regime using Hidden Markov Model (HMM)

        Note: This is a placeholder for more sophisticated HMM-based regime detection
        Requires additional dependencies (hmmlearn)

        Returns:
            Series with regime labels
        """
        # TODO: Implement HMM-based regime detection
        # For now, fall back to rule-based
        return self.detect_regime_rule_based()

    def get_regime_probabilities(self) -> pd.DataFrame:
        """
        Get probability distribution over regimes

        Note: Placeholder for probabilistic regime detection

        Returns:
            DataFrame with regime probabilities
        """
        regimes = self.detect_regime_rule_based()

        # Convert to one-hot encoding as simple probability
        regime_types = ['Expansion', 'Peak', 'Contraction', 'Recovery']
        probs = pd.DataFrame(0.0, index=regimes.index, columns=regime_types)

        for regime_type in regime_types:
            probs.loc[regimes == regime_type, regime_type] = 1.0

        return probs


def smooth_regimes(regimes: pd.Series, min_duration: int = 3) -> pd.Series:
    """
    Smooth regime transitions to avoid rapid switching

    Args:
        regimes: Series with regime labels
        min_duration: Minimum duration (in periods) for a regime

    Returns:
        Smoothed regime series
    """
    smoothed = regimes.copy()

    current_regime = smoothed.iloc[0]
    regime_start = 0

    for i in range(1, len(smoothed)):
        if smoothed.iloc[i] != current_regime:
            # Check if previous regime was too short
            if i - regime_start < min_duration:
                # Revert to previous regime
                smoothed.iloc[regime_start:i] = smoothed.iloc[regime_start-1] if regime_start > 0 else current_regime
            else:
                current_regime = smoothed.iloc[i]
                regime_start = i

    return smoothed


if __name__ == "__main__":
    # Test regime detection
    from src.data.data_loader import DataLoader

    loader = DataLoader()
    data = loader.load_all_data()

    detector = RegimeDetector(data['fred_m'])
    regimes = detector.detect_regime_rule_based()

    print("\n=== Regime Detection Summary ===")
    print(f"Regimes shape: {regimes.shape}")
    print(f"\nRegime distribution:")
    print(regimes.value_counts())

    print(f"\nLatest regimes:")
    print(regimes.tail(12))

    # Smooth regimes
    regimes_smooth = smooth_regimes(regimes, min_duration=3)
    print(f"\nSmoothed regime distribution:")
    print(regimes_smooth.value_counts())
