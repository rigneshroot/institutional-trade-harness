"""
Institutional Trade Harness - Backtesting Engine
Author: Rignesh P
"""

import math
from typing import List, Dict, Any, Tuple

class BacktestResult:
    """
    Carries execution summary of a historical backtest run,
    including Buy & Hold benchmark performance comparisons.
    """
    def __init__(self, 
                 portfolio_values: List[float], 
                 daily_returns: List[float], 
                 sharpe_ratio: float, 
                 sortino_ratio: float, 
                 max_drawdown: float,
                 total_return: float,
                 benchmark_total_return: float,
                 benchmark_sharpe: float,
                 benchmark_max_drawdown: float):
        self.portfolio_values = portfolio_values
        self.daily_returns = daily_returns
        self.sharpe_ratio = sharpe_ratio
        self.sortino_ratio = sortino_ratio
        self.max_drawdown = max_drawdown
        self.total_return = total_return
        
        # Benchmark indicators
        self.benchmark_total_return = benchmark_total_return
        self.benchmark_sharpe = benchmark_sharpe
        self.benchmark_max_drawdown = benchmark_max_drawdown
        self.disclaimer = "Deterministic simulation demo, not live trading performance."

class BacktestingEngine:
    """
    Evaluates strategy performance metrics across historical market datasets.
    Controls transaction costs and slippage as system Control Variables (CV).
    """
    
    def __init__(self, initial_capital: float = 1_000_000.0, transaction_cost: float = 0.001, slippage: float = 0.0005):
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.slippage = slippage

    def run(self, prices: List[float], signals: List[int]) -> BacktestResult:
        """
        Simulates a backtest over a pricing sequence.
        signals: 1 = BUY/LONG, -1 = SELL/SHORT, 0 = CASH/NEUTRAL
        """
        if len(prices) != len(signals):
            raise ValueError("Prices and signals must have identical dimensions.")
            
        capital = self.initial_capital
        position = 0.0
        portfolio_values = [capital]
        daily_returns = []
        
        last_signal = 0
        
        for i in range(1, len(prices)):
            current_price = prices[i]
            signal = signals[i-1]
            
            if signal != last_signal:
                if position != 0.0:
                    execution_price = current_price * (1.0 - self.slippage if position > 0 else 1.0 + self.slippage)
                    liquidation_cash = position * execution_price
                    capital = liquidation_cash - (abs(position * execution_price) * self.transaction_cost)
                    position = 0.0
                
                if signal == 1:  # Long
                    execution_price = current_price * (1.0 + self.slippage)
                    position = capital / execution_price
                    capital = 0.0
                elif signal == -1:  # Short
                    execution_price = current_price * (1.0 - self.slippage)
                    position = -capital / execution_price
                    capital = 2.0 * capital
                
                last_signal = signal
            
            current_val = capital
            if position != 0.0:
                if position > 0:
                    current_val = position * current_price
                else:  # Short
                    current_val = capital + (position * current_price)
            
            portfolio_values.append(current_val)
            
            ret = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
            daily_returns.append(ret)

        # Total Return
        total_return = (portfolio_values[-1] - self.initial_capital) / self.initial_capital

        # Sharpe Ratio
        avg_ret = sum(daily_returns) / len(daily_returns) if daily_returns else 0.0
        var_ret = sum((r - avg_ret) ** 2 for r in daily_returns) / (len(daily_returns) - 1) if len(daily_returns) > 1 else 0.0
        std_ret = math.sqrt(var_ret) if var_ret > 0 else 0.0
        sharpe = (avg_ret / std_ret) * math.sqrt(252) if std_ret > 0 else 0.0

        # Sortino Ratio
        downside_returns = [r for r in daily_returns if r < 0.0]
        var_downside = sum(r ** 2 for r in downside_returns) / len(daily_returns) if daily_returns else 0.0
        std_downside = math.sqrt(var_downside) if var_downside > 0 else 0.0
        sortino = (avg_ret / std_downside) * math.sqrt(252) if std_downside > 0 else 0.0

        # Max Drawdown
        peak = portfolio_values[0]
        max_dd = 0.0
        for val in portfolio_values:
            if val > peak:
                peak = val
            dd = (peak - val) / peak if peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd

        # --- Benchmark Calculations (Buy & Hold Strategy) ---
        benchmark_portfolio = []
        initial_price = prices[0]
        for p in prices:
            # Fraction of price change applied to initial capital
            benchmark_portfolio.append(self.initial_capital * (p / initial_price))
            
        benchmark_returns = []
        for i in range(1, len(benchmark_portfolio)):
            ret = (benchmark_portfolio[i] - benchmark_portfolio[i-1]) / benchmark_portfolio[i-1]
            benchmark_returns.append(ret)
            
        benchmark_total_return = (prices[-1] - initial_price) / initial_price
        
        bench_avg_ret = sum(benchmark_returns) / len(benchmark_returns) if benchmark_returns else 0.0
        bench_var_ret = sum((r - bench_avg_ret) ** 2 for r in benchmark_returns) / (len(benchmark_returns) - 1) if len(benchmark_returns) > 1 else 0.0
        bench_std_ret = math.sqrt(bench_var_ret) if bench_var_ret > 0 else 0.0
        benchmark_sharpe = (bench_avg_ret / bench_std_ret) * math.sqrt(252) if bench_std_ret > 0 else 0.0
        
        bench_peak = benchmark_portfolio[0]
        benchmark_max_drawdown = 0.0
        for val in benchmark_portfolio:
            if val > bench_peak:
                bench_peak = val
            dd = (bench_peak - val) / bench_peak if bench_peak > 0 else 0.0
            if dd > benchmark_max_drawdown:
                benchmark_max_drawdown = dd

        return BacktestResult(
            portfolio_values=portfolio_values,
            daily_returns=daily_returns,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_dd,
            total_return=total_return,
            benchmark_total_return=benchmark_total_return,
            benchmark_sharpe=benchmark_sharpe,
            benchmark_max_drawdown=benchmark_max_drawdown
        )
