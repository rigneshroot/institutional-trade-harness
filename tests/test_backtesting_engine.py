"""
Unit tests for Backtesting Engine
Author: Rignesh P
"""

from backtesting_engine import BacktestingEngine

def test_backtest_return_metrics():
    engine = BacktestingEngine(initial_capital=100000.0, transaction_cost=0.0, slippage=0.0)
    prices = [100.0, 105.0, 110.0, 104.5, 109.7]
    # Simple signals: buy day 1 and hold
    signals = [1, 1, 1, 1, 1]
    
    res = engine.run(prices, signals)
    
    assert isinstance(res.total_return, float)
    # Entry at 105.0, final price 109.7 -> return is (109.7 - 105.0) / 105.0 = 4.476%
    assert abs(res.total_return - 0.04476) < 1e-4
    assert res.sharpe_ratio >= -100.0
    # Benchmark buys at day 0 close (100.0) and holds to 109.7 -> return is 9.7%
    assert abs(res.benchmark_total_return - 0.097) < 1e-4

def test_slippage_and_cost_deduction():
    engine = BacktestingEngine(initial_capital=100000.0, transaction_cost=0.01, slippage=0.01)
    prices = [100.0, 110.0, 120.0]
    signals = [1, 0, 0]
    
    res = engine.run(prices, signals)
    assert res.total_return < 0.20
    assert res.total_return > 0.0
