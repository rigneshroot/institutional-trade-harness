"""
Institutional Trade Harness - Risk Governance Engine
Author: Rignesh P
"""

import math
from typing import List, Dict, Any, Tuple

class RiskReport:
    """Contains risk exposure metrics and gate statuses."""
    def __init__(self, 
                 gross_exposure: float,
                 net_exposure: float,
                 leverage: float,
                 var_99: float,
                 cvar_99: float,
                 current_drawdown: float,
                 kill_switch_active: bool,
                 logs: List[str]):
        self.gross_exposure = gross_exposure
        self.net_exposure = net_exposure
        self.leverage = leverage
        self.var_99 = var_99
        self.cvar_99 = cvar_99
        self.current_drawdown = current_drawdown
        self.kill_switch_active = kill_switch_active
        self.logs = logs

class RiskGovernanceEngine:
    """
    Implements institutional risk limits, pre-trade exposure gates, 
    statistical VaR/CVaR, and an autonomous Kill-Switch.
    """
    
    def __init__(self, 
                 max_leverage_limit: float = 3.0, 
                 max_drawdown_limit: float = 0.15,
                 var_limit: float = 0.05):
        self.max_leverage_limit = max_leverage_limit
        self.max_drawdown_limit = max_drawdown_limit
        self.var_limit = var_limit
        self.kill_switch_active = False

    def calculate_var_cvar(self, returns: List[float], confidence: float = 0.99) -> Tuple[float, float]:
        """
        Calculates historical Value-at-Risk (VaR) and Conditional Value-at-Risk (CVaR).
        """
        if not returns:
            return 0.0, 0.0
            
        sorted_rets = sorted(returns)
        n = len(sorted_rets)
        
        # Index corresponding to confidence level
        idx = int(math.floor((1.0 - confidence) * n))
        idx = max(0, min(idx, n - 1))
        
        # VaR is the negative value of return at confidence boundary
        var = -sorted_rets[idx]
        
        # CVaR is the average of returns worse than VaR
        tail_returns = sorted_rets[:idx + 1]
        cvar = -sum(tail_returns) / len(tail_returns) if tail_returns else var
        
        return max(0.0, var), max(0.0, cvar)

    def evaluate_risk(self, 
                      current_portfolio_value: float,
                      peak_value: float,
                      positions: Dict[str, float],
                      prices: Dict[str, float],
                      historical_returns: List[float]) -> RiskReport:
        """
        Evaluates pre-trade and post-trade risk gates.
        positions: dict of asset symbol -> position size (positive for long, negative for short)
        prices: dict of asset symbol -> current price
        """
        logs = []
        
        # 1. Exposure & Leverage Calculation
        long_value = 0.0
        short_value = 0.0
        
        for symbol, size in positions.items():
            price = prices.get(symbol, 0.0)
            val = size * price
            if val > 0:
                long_value += val
            else:
                short_value += abs(val)
                
        gross_exposure = long_value + short_value
        net_exposure = long_value - short_value
        
        leverage = gross_exposure / current_portfolio_value if current_portfolio_value > 0 else 0.0
        
        # 2. Drawdown Calculation
        current_drawdown = (peak_value - current_portfolio_value) / peak_value if peak_value > 0 else 0.0
        
        # 3. VaR & CVaR Calculation
        var_99, cvar_99 = self.calculate_var_cvar(historical_returns, confidence=0.99)
        
        # 4. Check Risk Limits (Pre-trade & Live monitoring)
        if leverage > self.max_leverage_limit:
            self.kill_switch_active = True
            logs.append(f"KILL-SWITCH TRIGGERED: Leverage limit exceeded! {leverage:.2f}x > {self.max_leverage_limit:.2f}x")
            
        if current_drawdown > self.max_drawdown_limit:
            self.kill_switch_active = True
            logs.append(f"KILL-SWITCH TRIGGERED: Max drawdown exceeded! {current_drawdown*100:.2f}% > {self.max_drawdown_limit*100:.2f}%")
            
        if var_99 > self.var_limit:
            self.kill_switch_active = True
            logs.append(f"KILL-SWITCH TRIGGERED: 99% VaR limit breached! {var_99*100:.2f}% > {self.var_limit*100:.2f}%")

        if not self.kill_switch_active:
            logs.append("All risk gates PASSED.")
        else:
            logs.append("Risk status: DANGER (Kill-Switch Active). Execution halted.")

        return RiskReport(
            gross_exposure=gross_exposure,
            net_exposure=net_exposure,
            leverage=leverage,
            var_99=var_99,
            cvar_99=cvar_99,
            current_drawdown=current_drawdown,
            kill_switch_active=self.kill_switch_active,
            logs=logs
        )
