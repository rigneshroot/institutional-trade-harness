"""
Unit tests for Risk Governance Engine
Author: Rignesh P
"""

from risk_engine import RiskGovernanceEngine

def test_var_cvar_calculation():
    risk_engine = RiskGovernanceEngine()
    returns = [-0.05, -0.02, 0.01, 0.03, -0.01, 0.02, -0.04, 0.01]
    var, cvar = risk_engine.calculate_var_cvar(returns, confidence=0.90)
    
    assert isinstance(var, float)
    assert isinstance(cvar, float)
    assert var >= 0.0
    assert cvar >= 0.0

def test_kill_switch_leverage():
    risk_engine = RiskGovernanceEngine(max_leverage_limit=2.0)
    positions = {"SPY": 3000.0}
    prices = {"SPY": 1000.0}
    
    report = risk_engine.evaluate_risk(
        current_portfolio_value=1_000_000.0,
        peak_value=1_000_000.0,
        positions=positions,
        prices=prices,
        historical_returns=[0.01, -0.01]
    )
    
    assert report.kill_switch_active
    assert any("Leverage limit exceeded" in log for log in report.logs)

def test_kill_switch_drawdown():
    risk_engine = RiskGovernanceEngine(max_drawdown_limit=0.10)
    report = risk_engine.evaluate_risk(
        current_portfolio_value=850_000.0,
        peak_value=1_000_000.0,
        positions={},
        prices={},
        historical_returns=[0.01, -0.01]
    )
    assert report.kill_switch_active
    assert any("Max drawdown exceeded" in log for log in report.logs)
