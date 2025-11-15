"""
Performance metrics and analytics module
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional


def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate returns from prices"""
    return prices.pct_change()


def cumulative_returns(returns: pd.Series) -> pd.Series:
    """Calculate cumulative returns"""
    return (1 + returns).cumprod()


def annualized_return(returns: pd.Series, periods_per_year: int = 12) -> float:
    """
    Calculate annualized return (CAGR)

    Args:
        returns: Series of returns
        periods_per_year: Number of periods per year (12 for monthly, 252 for daily)

    Returns:
        Annualized return as decimal
    """
    cum_ret = (1 + returns).prod()
    n_periods = len(returns)
    n_years = n_periods / periods_per_year

    if n_years > 0:
        cagr = cum_ret ** (1 / n_years) - 1
    else:
        cagr = 0.0

    return cagr


def annualized_volatility(returns: pd.Series, periods_per_year: int = 12) -> float:
    """
    Calculate annualized volatility

    Args:
        returns: Series of returns
        periods_per_year: Number of periods per year (12 for monthly, 252 for daily)

    Returns:
        Annualized volatility as decimal
    """
    return returns.std() * np.sqrt(periods_per_year)


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0,
                periods_per_year: int = 12) -> float:
    """
    Calculate Sharpe ratio

    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year

    Returns:
        Sharpe ratio
    """
    excess_returns = returns - risk_free_rate / periods_per_year
    if excess_returns.std() > 0:
        return excess_returns.mean() / excess_returns.std() * np.sqrt(periods_per_year)
    else:
        return 0.0


def max_drawdown(returns: pd.Series) -> float:
    """
    Calculate maximum drawdown

    Args:
        returns: Series of returns

    Returns:
        Maximum drawdown as positive decimal (e.g., 0.20 for -20%)
    """
    cum_returns = (1 + returns).cumprod()
    running_max = cum_returns.expanding().max()
    drawdown = (cum_returns - running_max) / running_max

    return abs(drawdown.min())


def calmar_ratio(returns: pd.Series, periods_per_year: int = 12) -> float:
    """
    Calculate Calmar ratio (CAGR / Max Drawdown)

    Args:
        returns: Series of returns
        periods_per_year: Number of periods per year

    Returns:
        Calmar ratio
    """
    cagr = annualized_return(returns, periods_per_year)
    mdd = max_drawdown(returns)

    if mdd > 0:
        return cagr / mdd
    else:
        return 0.0


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0,
                 periods_per_year: int = 12) -> float:
    """
    Calculate Sortino ratio (uses downside deviation)

    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year

    Returns:
        Sortino ratio
    """
    excess_returns = returns - risk_free_rate / periods_per_year
    downside_returns = excess_returns[excess_returns < 0]

    if len(downside_returns) > 0:
        downside_std = downside_returns.std() * np.sqrt(periods_per_year)
        if downside_std > 0:
            return (excess_returns.mean() * periods_per_year) / downside_std
        else:
            return 0.0
    else:
        return 0.0


def win_rate(returns: pd.Series) -> float:
    """Calculate percentage of positive returns"""
    return (returns > 0).sum() / len(returns)


def ann_stats(cumulative: pd.Series, returns: pd.Series, name: str = "Strategy",
             periods_per_year: int = 12) -> Dict:
    """
    Calculate comprehensive annualized statistics

    Args:
        cumulative: Cumulative returns series
        returns: Returns series
        name: Strategy name
        periods_per_year: Number of periods per year

    Returns:
        Dictionary with performance statistics
    """
    stats = {
        'Strategy': name,
        'CAGR': annualized_return(returns, periods_per_year),
        'Vol': annualized_volatility(returns, periods_per_year),
        'Sharpe': sharpe_ratio(returns, periods_per_year=periods_per_year),
        'MDD': max_drawdown(returns),
        'Calmar': calmar_ratio(returns, periods_per_year),
        'Sortino': sortino_ratio(returns, periods_per_year=periods_per_year),
        'Win Rate': win_rate(returns),
    }

    return stats


def annual_returns(returns: pd.Series) -> pd.Series:
    """
    Calculate returns for each calendar year

    Args:
        returns: Series of returns

    Returns:
        Series of annual returns indexed by year
    """
    annual = (1 + returns).groupby(returns.index.year).prod() - 1
    annual.index.name = 'Year'

    return annual


def monthly_returns_table(returns: pd.Series) -> pd.DataFrame:
    """
    Create table of monthly returns by year

    Args:
        returns: Series of monthly returns

    Returns:
        DataFrame with years as rows and months as columns
    """
    monthly = returns.copy()
    monthly.index = pd.to_datetime(monthly.index)

    table = pd.DataFrame(index=monthly.index.year.unique(),
                        columns=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Year'])

    month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

    for date, ret in monthly.items():
        year = date.year
        month = month_map[date.month]
        table.loc[year, month] = ret

    # Calculate annual returns
    table['Year'] = annual_returns(returns)

    return table


def rolling_sharpe(returns: pd.Series, window: int = 12,
                  periods_per_year: int = 12) -> pd.Series:
    """
    Calculate rolling Sharpe ratio

    Args:
        returns: Series of returns
        window: Rolling window size
        periods_per_year: Number of periods per year

    Returns:
        Series of rolling Sharpe ratios
    """
    rolling_mean = returns.rolling(window=window).mean()
    rolling_std = returns.rolling(window=window).std()

    sharpe = (rolling_mean / rolling_std) * np.sqrt(periods_per_year)

    return sharpe


def rolling_drawdown(returns: pd.Series) -> pd.Series:
    """
    Calculate rolling drawdown

    Args:
        returns: Series of returns

    Returns:
        Series of drawdowns
    """
    cum_returns = (1 + returns).cumprod()
    running_max = cum_returns.expanding().max()
    drawdown = (cum_returns - running_max) / running_max

    return drawdown


if __name__ == "__main__":
    # Test performance metrics
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=36, freq='M')
    returns = pd.Series(np.random.randn(36) * 0.02 + 0.005, index=dates)

    cum = cumulative_returns(returns)
    stats = ann_stats(cum, returns, "Test Strategy")

    print("\n=== Performance Statistics ===")
    for key, value in stats.items():
        if isinstance(value, float):
            if 'Rate' in key:
                print(f"{key}: {value:.2%}")
            else:
                print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

    print("\nAnnual Returns:")
    print(annual_returns(returns))
