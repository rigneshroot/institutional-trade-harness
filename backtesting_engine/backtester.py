"""
Institutional Trade Harness - Backtesting Engine
Author: Rignesh P
"""

import math
from typing import List, Dict, Any, Tuple

class BacktestResult:
    """Carries the execution summary of a historical backtest run."""
    def __init__(self, 
                 portfolio_values: List[float], 
                 daily_returns: List[float], 
                 sharpe_ratio: float, 
                 sortino_ratio: float, 
                 max_drawdown: float,
                 total_return: float):
        self.portfolio_values = portfolio_values
        self.daily_returns = daily_returns
        self.sharpe_ratio = sharpe_ratio
        self.sortino_ratio = sortino_ratio
        self.max_drawdown = max_drawdown
        self.total_return = total_return

class BacktestingEngine:
    """
    Evaluates strategy performance metrics across historical market datasets.
    Controls transaction costs and slippage as system Control Variables (CV).
    """
    
    def __init__(self, initial_capital: float = 1_000_000.0, transaction_cost: float = 0.001, slippage: float = 0.0005):
        self.initial_capital = initial_capital
        # Transaction costs and slippage represent our Control Variables (CV)
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
        position = 0.0  # units of the asset held
        portfolio_values = [capital]
        daily_returns = []
        
        last_signal = 0
        
        for i in range(1, len(prices)):
            current_price = prices[i]
            prev_price = prices[i-1]
            signal = signals[i-1]
            
            # Execute transactions on signal change
            if signal != last_signal:
                # Liquidate old position
                if position != 0.0:
                    trade_value = position * current_price
                    # Deduct transaction cost and slippage
                    execution_price = current_price * (1.0 - self.slippage if position > 0 else 1.0 + self.slippage)
                    liquidation_cash = position * execution_price
                    capital = liquidation_cash - (abs(position * execution_price) * self.transaction_cost)
                    position = 0.0
                
                # Establish new position
                if signal == 1:  # Long
                    execution_price = current_price * (1.0 + self.slippage)
                    position = capital / execution_price
                    capital = 0.0
                elif signal == -1:  # Short
                    # Simplified short modeling: hold negative unit exposure and cash buffer
                    execution_price = current_price * (1.0 - self.slippage)
                    position = -capital / execution_price
                    capital = 2.0 * capital  # Cash buffer holds short collateral
                
                last_signal = signal
            
            # Mark-to-market portfolio value calculation
            current_val = capital
            if position != 0.0:
                if position > 0:
                    current_val = position * current_price
                else:  # Short
                    # cash buffer plus short position gain/loss
                    current_val = capital + (position * current_price)
            
            portfolio_values.append(current_val)
            
            # Daily return
            ret = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
            daily_returns.append(ret)

        # 1. Total Return
        total_return = (portfolio_values[-1] - self.initial_capital) / self.initial_capital

        # 2. Sharpe Ratio (assuming risk-free rate = 0 for simplicity)
        avg_ret = sum(daily_returns) / len(daily_returns) if daily_returns else 0.0
        var_ret = sum((r - avg_ret) ** 2 for r in daily_returns) / (len(daily_returns) - 1) if len(daily_returns) > 1 else 0.0
        std_ret = math.sqrt(var_ret) if var_ret > 0 else 0.0
        
        # Annualized Sharpe (assuming 252 trading sessions)
        sharpe = (avg_ret / std_ret) * math.sqrt(252) if std_ret > 0 else 0.0

        # 3. Sortino Ratio (downside risk only)
        downside_returns = [r for r in daily_returns if r < 0.0]
        var_downside = sum(r ** 2 for r in downside_returns) / len(daily_returns) if daily_returns else 0.0
        std_downside = math.sqrt(var_downside) if var_downside > 0 else 0.0
        
        sortino = (avg_ret / std_downside) * math.sqrt(252) if std_downside > 0 else 0.0

        # 4. Maximum Drawdown
        peak = portfolio_values[0]
        max_dd = 0.0
        for val in portfolio_values:
            if val > peak:
                peak = val
            dd = (peak - val) / peak if peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd

        return BacktestResult(
            portfolio_values=portfolio_values,
            daily_returns=daily_returns,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_dd,
            total_return=total_return
        )
