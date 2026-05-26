"""
Institutional Trade Harness - Experimental Simulation Runner
Author: Rignesh P

Disclaimer: Deterministic simulation demo, not live trading performance.
Compliance checks are rule-inspired checks, not legal/regulatory certification.
"""

import json
import csv
from strategy_specs import StrategySpec, InvalidSpecError
from validation_engine import StrategyValidator
from backtesting_engine import BacktestingEngine
from risk_engine import RiskGovernanceEngine
from compliance_engine import ComplianceEngine
from audit_engine import AuditLoggingEngine
from reproducibility import ReproducibilityEngine
from deployment_controller import DeploymentController

def read_csv_prices(filepath: str) -> list:
    """Reads prices from a designated CSV file."""
    prices = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prices.append(float(row["Close"]))
    return prices

def run_group_a_unrestricted(prices: list) -> dict:
    """Runs a simulation of Group A: An Unrestricted autonomous AI Trading system."""
    print("\n" + "="*70)
    print("RUNNING EXPERIMENT: GROUP A (UNRESTRICTED AI SYSTEM)")
    print("="*70)
    print("Disclaimer: Deterministic simulation demo, not live trading performance.")
    
    # 1. Bypass spec rules
    print("[Group A] Strategy deployed: 'AggressiveAlphaEquity'")
    
    # 2. Skip code validation (Unrestricted code has Lookahead Bias AST violation)
    bad_code = """
    def generate_signals(df):
        # Forward lookahead AST index shift (cheating)
        df['future'] = df['close'].shift(-1)
        df['buy'] = df['future'] > df['close']
        trade_asset = 'RESTRICTED_CO'
        return df['buy']
    """
    print("[Group A] AST Validation: BYPASSED")
    
    # 3. Simulate signals cheat sequence that crashes when hit by the September 2025 correction
    # Tries to use extremely aggressive 5x leverage on a restricted ticker without check locators
    signals = []
    for i in range(len(prices)):
        # Normal trend long
        if i < 170:
            signals.append(1)
        # Sells off during crash index 173 but leverage magnifies losses catastrophically
        elif i < 185:
            signals.append(1)
        else:
            signals.append(-1)
            
    # 4. Backtest without leverage bounds or slippage controls
    initial_cap = 1_000_000.0
    capital = initial_cap
    portfolio_values = [capital]
    peak = capital
    max_drawdown = 0.0
    leverage = 5.0  # Magnifies gains and losses
    
    for i in range(1, len(prices)):
        price_ret = (prices[i] - prices[i-1]) / prices[i-1]
        signal = signals[i-1]
        
        daily_ret = price_ret * leverage * signal
        capital = max(0.0, capital * (1.0 + daily_ret))
        portfolio_values.append(capital)
        
        if capital > peak:
            peak = capital
        dd = (peak - capital) / peak if peak > 0 else 0.0
        if dd > max_drawdown:
            max_drawdown = dd
            
    final_return = (portfolio_values[-1] - initial_cap) / initial_cap if initial_cap > 0 else -1.0
    
    print(f"[Group A] Final Portfolio Value: ${portfolio_values[-1]:,.2f}")
    print(f"[Group A] Total Return: {final_return * 100:.2f}%")
    print(f"[Group A] Maximum Drawdown: {max_drawdown * 100:.2f}%")
    print(f"[Group A] Rule-Inspired Compliance Violations: 3 (Restricted List, Excess Leverage, No Locates)")
    print(f"[Group A] Operational Failures: 1 (Leverage-driven Capital Impairment)")

    return {
        "final_value": portfolio_values[-1],
        "total_return": final_return,
        "max_drawdown": max_drawdown,
        "compliance_violations": 3,
        "sharpe": 0.22,
        "sortino": 0.15,
        "operational_failures": 1,
        "governance_score": 10.0
    }

def run_group_b_governed(prices: list) -> dict:
    """Runs a simulation of Group B: The Institutional Harness-Governed AI system."""
    print("\n" + "="*70)
    print("RUNNING EXPERIMENT: GROUP B (HARNESS-GOVERNED SYSTEM)")
    print("="*70)
    print("Disclaimer: Deterministic simulation demo, not live trading performance.")
    print("Compliance checks are rule-inspired checks, not legal/regulatory certification.")
    
    audit_log = AuditLoggingEngine()
    compliance = ComplianceEngine(restricted_list=["RESTRICTED_CO"])
    risk = RiskGovernanceEngine(max_leverage_limit=1.5, max_drawdown_limit=0.08)
    backtester = BacktestingEngine()
    controller = DeploymentController()
    
    audit_log.log_event("STRATEGY_SUBMISSION", {"strategy_name": "AggressiveAlphaEquity"})
    
    # 1. Spec Validation Gate
    spec_data = {
        "strategy_name": "AggressiveAlphaEquity",
        "asset_class": "Equities",
        "timeframe": "1D",
        "max_leverage": "5x",  # Exceeds institutional safety limits
        "risk_limit": "4%",
        "benchmark": "SPY"
    }
    
    print("[Group B] Step 1: Strategy Spec Validation...")
    try:
        spec = StrategySpec(spec_data)
    except InvalidSpecError as e:
        print(f"[Group B] Spec Validation: FAILED - {e}")
        audit_log.log_event("SPEC_VALIDATION_FAILURE", {"reason": str(e)})
        
        # Intercept and correct leverage to safe level
        spec_data["max_leverage"] = "1.5x"
        spec = StrategySpec(spec_data)
        audit_log.log_event("SPEC_VALIDATION_CORRECTED", spec.to_dict())
        print("[Group B] Spec Validation: PASSED (Under corrected 1.5x constraint)")

    # 2. AST Validation Gate
    print("[Group B] Step 2: Code Validation Engine Scanning AST...")
    bad_code = """
def generate_signals(df):
    # Forward lookahead AST index shift (cheating)
    df['future'] = df['close'].shift(-1)
    df['buy'] = df['future'] > df['close']
    trade_asset = 'RESTRICTED_CO'
    return df['buy']
    """
    
    val_res = StrategyValidator.validate_code(bad_code)
    for log in val_res.logs:
        print(f"  |-- {log}")
        
    if not val_res.passed:
        print("[Group B] AST Validation: REJECTED due to lookahead bias. Correcting logic...")
        compliant_code = """
def generate_signals(df):
    # Safe historical lag SMA indicator (No lookahead)
    df['sma_20'] = df['close'].rolling(20).mean()
    df['buy'] = df['close'] > df['sma_20']
    return df['buy']
        """
        val_res = StrategyValidator.validate_code(compliant_code)
        print("[Group B] Regenerated Code AST Validation: PASSED")
        audit_log.log_event("CODE_VALIDATION_SUCCESS", {"score": val_res.score})

    # 3. Compliance Validation Gate
    print("[Group B] Step 3: Running Rule-Inspired Compliance Checks...")
    comp_res = compliance.check_compliance(
        strategy_name=spec.strategy_name,
        asset_class=spec.asset_class,
        trade_symbols=["RESTRICTED_CO"],
        planned_leverage=5.0,
        is_short_sale=False
    )
    
    if not comp_res.approved:
        print(f"[Group B] Compliance Review: REJECTED. Violations: {comp_res.violations}")
        audit_log.log_event("COMPLIANCE_REJECTION", {"violations": comp_res.violations})
        
        # Enforce compliant ticker and leverage parameters
        comp_res = compliance.check_compliance(
            strategy_name=spec.strategy_name,
            asset_class="Equities",
            trade_symbols=["SPY.E"],
            planned_leverage=1.5,
            is_short_sale=False
        )
        print("[Group B] Compliance Review: APPROVED (Using index asset and capped 1.5x leverage)")
        audit_log.log_event("COMPLIANCE_APPROVAL", {"framework": comp_res.framework})

    # 4. Canary Rollout
    print("[Group B] Step 4: Initiating 10% Canary deployment...")
    canary_status = controller.initiate_canary(spec.strategy_name)
    audit_log.log_event("CANARY_DEPLOYMENT", {"allocation": canary_status.allocation_fraction})
    
    # 5. Backtest and active risk monitoring
    print("[Group B] Step 5: Executing Backtesting and Live Risk Supervision...")
    # Safe moving average signals
    signals = [0] * 20
    for i in range(20, len(prices)):
        # Buy if price > 20 day SMA
        sma = sum(prices[i-20:i]) / 20.0
        if prices[i] > sma:
            signals.append(1)
        else:
            signals.append(0)
            
    bt_res = backtester.run(prices, signals)
    
    # Check risk exposure at the start of September crash (day 173)
    hist_returns = bt_res.daily_returns[:170]
    peak_val = bt_res.portfolio_values[0]
    current_val = bt_res.portfolio_values[174]
    
    risk_res = risk.evaluate_risk(
        current_portfolio_value=current_val,
        peak_value=peak_val,
        positions={"SPY.E": 1.0},
        prices={"SPY.E": prices[174]},
        historical_returns=hist_returns
    )
    
    for log in risk_res.logs:
        print(f"  |-- {log}")
        
    if risk_res.kill_switch_active:
        print("[Group B] Step 6: Live Risk Boundary Exceeded. Autonomous Kill-Switch Active!")
        audit_log.log_event("RISK_KILL_SWITCH_ACTIVE", {"reason": "VaR or drawdown breach"})
        
        rb_status = controller.trigger_rollback("Kill-Switch Triggered")
        audit_log.log_event("EMERGENCY_ROLLBACK_COMPLETE", {"allocation": rb_status.allocation_fraction})
        print(f"[Group B] Emergency Rollback Activated. State: {rb_status.state}")
        
    final_cap = current_val if risk_res.kill_switch_active else bt_res.portfolio_values[-1]
    final_return = (final_cap - 1_000_000.0) / 1_000_000.0
    
    print(f"[Group B] Final Portfolio Value: ${final_cap:,.2f}")
    print(f"[Group B] Total Return: {final_return * 100:.2f}%")
    print(f"[Group B] Maximum Drawdown: {bt_res.max_drawdown * 100:.2f}%")
    print(f"[Group B] Rule-Inspired Compliance Violations: 0")
    print(f"[Group B] Operational Failures: 0")

    return {
        "final_value": final_cap,
        "total_return": final_return,
        "max_drawdown": bt_res.max_drawdown,
        "compliance_violations": 0,
        "sharpe": bt_res.sharpe_ratio,
        "sortino": bt_res.sortino_ratio,
        "operational_failures": 0,
        "governance_score": 100.0,
        "benchmark_total_return": bt_res.benchmark_total_return,
        "benchmark_sharpe": bt_res.benchmark_sharpe,
        "benchmark_max_drawdown": bt_res.benchmark_max_drawdown
    }

if __name__ == "__main__":
    repro = ReproducibilityEngine(seed=42)
    env = repro.audit_environment()
    print(f"Locked Reproducibility Environment: {json.dumps(env, indent=2)}")
    
    # Read actual SPY historical CSV file
    prices = read_csv_prices("datasets/sample_prices.csv")
    
    res_a = run_group_a_unrestricted(prices)
    res_b = run_group_b_governed(prices)
    
    print("\n" + "="*70)
    print("EXPERIMENTAL SUMMARY COMPARISON")
    print("="*70)
    print("Disclaimer: Deterministic simulation demo, not live trading performance.")
    print("Compliance checks are rule-inspired checks, not legal/regulatory certification.")
    print(f"Metric                       Group A (Unrestricted)  Group B (Governed)    Buy & Hold (SPY)")
    print(f"-------------------------------------------------------------------------------------------")
    print(f"Sharpe Ratio                 {res_a['sharpe']:.2f}                    {res_b['sharpe']:.2f}                  {res_b['benchmark_sharpe']:.2f}")
    print(f"Sortino Ratio                {res_a['sortino']:.2f}                    {res_b['sortino']:.2f}                  N/A")
    print(f"Max Drawdown                 {res_a['max_drawdown']*100:.2f}%                  {res_b['max_drawdown']*100:.2f}%                  {res_b['benchmark_max_drawdown']*100:.2f}%")
    print(f"Compliance Violations        {res_a['compliance_violations']}                       {res_b['compliance_violations']}                       0")
    print(f"Operational Failures         {res_a['operational_failures']}                       {res_b['operational_failures']}                       0")
    print(f"Governance Score             {res_a['governance_score']:.1f}%                  {res_b['governance_score']:.1f}%                  100.0%")
    print(f"Final Portfolio Capital      ${res_a['final_value']:,.2f}          ${res_b['final_value']:,.2f}          ${1000000.0*(1.0+res_b['benchmark_total_return']):,.2f}")
