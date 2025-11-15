"""
Configuration file for Regime-based Factor Allocation Strategy
"""

# Factor ETFs
FACTOR_ETFS = [
    'MTUM',  # Momentum
    'QUAL',  # Quality
    'SIZE',  # Size
    'VLUE',  # Value
    'USMV',  # Low Volatility
]

# Benchmark and Cash
BENCH = 'SPY'
CASH_ETF = 'BIL'  # Short-term Treasury Bills

# Lookback periods (in months)
MOM_LOOKBACK_M = 12  # Momentum lookback
VAL_LOOKBACK_M = 12  # Valuation lookback
REGIME_LOOKBACK_M = 3  # Regime detection lookback

# Signal weights
W_MOM = 0.5  # Weight for momentum signal
W_VAL = 0.5  # Weight for valuation signal

# Risk management
RISK_OFF_FRACTION = 0.5  # Base cash allocation in risk-off
CFNAI_THRESHOLD = -0.5  # CFNAI threshold for severe risk-off
CFNAI_RISK_OFF = 0.7  # Cash allocation when CFNAI < threshold

# Transaction costs
TC_BPS = 5  # Transaction cost in basis points

# Regime definitions and preferences
REGIME_PREFS = {
    'Expansion': {
        'MTUM': 1.2,  # Favor momentum
        'QUAL': 1.0,
        'SIZE': 1.1,  # Favor small caps
        'VLUE': 0.8,
        'USMV': 0.7,  # Reduce defensive
    },
    'Peak': {
        'MTUM': 1.0,
        'QUAL': 1.2,  # Favor quality
        'SIZE': 0.8,
        'VLUE': 1.0,
        'USMV': 1.1,  # Increase defensive
    },
    'Contraction': {
        'MTUM': 0.7,
        'QUAL': 1.3,  # Strong quality preference
        'SIZE': 0.6,  # Reduce small caps
        'VLUE': 0.8,
        'USMV': 1.4,  # Strong defensive preference
    },
    'Recovery': {
        'MTUM': 1.3,  # Strong momentum preference
        'QUAL': 1.0,
        'SIZE': 1.2,  # Favor small caps
        'VLUE': 1.1,  # Moderate value
        'USMV': 0.6,  # Reduce defensive
    },
    'Unknown': {
        'MTUM': 1.0,
        'QUAL': 1.0,
        'SIZE': 1.0,
        'VLUE': 1.0,
        'USMV': 1.0,
    }
}

# Data parameters
START_DATE = '2010-01-01'
END_DATE = None  # None for today

# FRED economic indicators
FRED_INDICATORS = {
    'CFNAI': 'CFNAIMA3',  # Chicago Fed National Activity Index (3-month MA)
    'UNRATE': 'UNRATE',   # Unemployment Rate
    'T10Y2Y': 'T10Y2Y',   # 10Y-2Y Treasury Spread
}

# Regime detection parameters
REGIME_PARAMS = {
    'cfnai_expansion': 0.0,
    'cfnai_contraction': -0.3,
    'unemployment_rising': 0.3,  # % point increase
    'yield_curve_inverted': 0.0,
}
