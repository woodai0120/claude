"""
Data loading and preprocessing module
"""
import pandas as pd
import numpy as np
import yfinance as yf
from pandas_datareader import data as pdr
from typing import List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.append('/home/user/claude')
from config.config import (
    FACTOR_ETFS, BENCH, CASH_ETF, START_DATE, END_DATE, FRED_INDICATORS
)


class DataLoader:
    """Handles data loading from Yahoo Finance and FRED"""

    def __init__(self, start_date: str = START_DATE, end_date: Optional[str] = END_DATE):
        self.start_date = start_date
        self.end_date = end_date or pd.Timestamp.today().strftime('%Y-%m-%d')

    def load_price_data(self, tickers: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load price data for specified tickers

        Args:
            tickers: List of ticker symbols. If None, uses FACTOR_ETFS + BENCH + CASH_ETF

        Returns:
            DataFrame with adjusted close prices
        """
        if tickers is None:
            tickers = FACTOR_ETFS + [BENCH, CASH_ETF]

        print(f"Loading price data for {len(tickers)} tickers from {self.start_date} to {self.end_date}")

        # Download data
        data = yf.download(tickers, start=self.start_date, end=self.end_date,
                          auto_adjust=True, progress=False)

        # Extract Close prices
        if len(tickers) == 1:
            prices = data[['Close']].copy()
            prices.columns = tickers
        else:
            prices = data['Close'].copy()

        # Forward fill missing values
        prices = prices.ffill()

        print(f"Loaded price data: {len(prices)} rows, {len(prices.columns)} tickers")
        print(f"Date range: {prices.index[0]} to {prices.index[-1]}")

        return prices

    def load_fred_data(self) -> pd.DataFrame:
        """
        Load economic indicators from FRED

        Returns:
            DataFrame with economic indicators
        """
        print("Loading FRED economic indicators...")

        fred_data = pd.DataFrame()

        for name, series_id in FRED_INDICATORS.items():
            try:
                data = pdr.DataReader(series_id, 'fred', self.start_date, self.end_date)
                fred_data[name] = data[series_id]
                print(f"  Loaded {name} ({series_id})")
            except Exception as e:
                print(f"  Warning: Could not load {name} ({series_id}): {e}")

        return fred_data

    def resample_to_monthly(self, prices: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Convert daily prices to monthly

        Args:
            prices: DataFrame with daily prices

        Returns:
            Tuple of (monthly prices, monthly returns)
        """
        # Resample to month-end
        prices_m = prices.resample('M').last()

        # Calculate returns
        rets_m = prices_m.pct_change()

        return prices_m, rets_m

    def load_all_data(self) -> dict:
        """
        Load all required data for backtesting

        Returns:
            Dictionary containing:
                - prices_d: daily prices
                - prices_m: monthly prices
                - rets_m: monthly returns
                - fred: FRED economic indicators
        """
        # Load price data
        prices_d = self.load_price_data()

        # Convert to monthly
        prices_m, rets_m = self.resample_to_monthly(prices_d)

        # Load FRED data
        fred = self.load_fred_data()

        # Resample FRED to monthly
        fred_m = fred.resample('M').last()

        return {
            'prices_d': prices_d,
            'prices_m': prices_m,
            'rets_m': rets_m,
            'fred_m': fred_m,
        }


def calculate_rolling_stats(data: pd.Series, window: int) -> pd.DataFrame:
    """
    Calculate rolling mean and std for a series

    Args:
        data: Input series
        window: Rolling window size

    Returns:
        DataFrame with mean and std columns
    """
    stats = pd.DataFrame(index=data.index)
    stats['mean'] = data.rolling(window=window).mean()
    stats['std'] = data.rolling(window=window).std()

    return stats


def z_score(data: pd.Series, window: int) -> pd.Series:
    """
    Calculate rolling z-score

    Args:
        data: Input series
        window: Rolling window size

    Returns:
        Series of z-scores
    """
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()

    z = (data - rolling_mean) / rolling_std

    return z


if __name__ == "__main__":
    # Test data loading
    loader = DataLoader()
    data = loader.load_all_data()

    print("\n=== Data Summary ===")
    print(f"Prices shape: {data['prices_m'].shape}")
    print(f"Returns shape: {data['rets_m'].shape}")
    print(f"FRED data shape: {data['fred_m'].shape}")
    print(f"\nAvailable tickers: {list(data['prices_m'].columns)}")
    print(f"Available indicators: {list(data['fred_m'].columns)}")
