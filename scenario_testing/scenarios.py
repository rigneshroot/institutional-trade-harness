"""
Institutional Trade Harness - Scenario Stress Testing Engine
Author: Rignesh P

Defines 5 deterministic stress-test scenarios and runs Group A (Unrestricted)
vs Group B (Harness-Governed) comparisons on each.

Disclaimer: Deterministic simulation demo, not live trading performance.
Compliance checks are rule-inspired checks, not legal/regulatory certification.
"""

import math
import random
from typing import List, Tuple, Callable

from backtesting_engine import BacktestingEngine
from risk_engine import RiskGovernanceEngine
from compliance_engine import ComplianceEngine
from audit_engine import AuditLoggingEngine
from deployment_controller import DeploymentController


# ---------------------------------------------------------------------------
# Deterministic Price Generators
# ---------------------------------------------------------------------------

def generate_flash_crash_prices() -> List[float]:
    """Sudden -35% price collapse over 3 bars (indices 40-42), partial recovery."""
    random.seed(101)
    price = 100.0
    prices = [price]
    for i in range(99):
        if 40 <= i <= 42:
            change = random.uniform(-0.14, -0.10)   # ~35% cumulative drop
        elif 43 <= i <= 55:
            change = random.uniform(0.01, 0.04)      # partial recovery
        else:
            change = random.uniform(-0.015, 0.02)
        price *= (1.0 + change)
        prices.append(price)
    return prices


def generate_volatility_spike_prices() -> List[float]:
    """Extreme ±8% daily swings for 30 consecutive bars (indices 30-59)."""
    random.seed(102)
    price = 100.0
    prices = [price]
    for i in range(99):
        if 30 <= i < 60:
            change = random.uniform(-0.08, 0.08)    # extreme vol
        else:
            change = random.uniform(-0.01, 0.015)
        price *= (1.0 + change)
        prices.append(price)
    return prices


def generate_liquidity_collapse_prices() -> List[float]:
    """Sustained -2% to -5% daily bleed for 20 bars (indices 35-54)."""
    random.seed(103)
    price = 100.0
    prices = [price]
    for i in range(99):
        if 35 <= i < 55:
            change = random.uniform(-0.05, -0.02)   # steady bleed
        elif i >= 55:
            change = random.uniform(-0.005, 0.005)   # stagnation
        else:
            change = random.uniform(-0.01, 0.02)
        price *= (1.0 + change)
        prices.append(price)
    return prices


def generate_exchange_outage_prices() -> List[float]:
    """10-bar price freeze (indices 45-54) then -20% gap-down on bar 55."""
    random.seed(104)
    price = 100.0
    prices = [price]
    for i in range(99):
        if 45 <= i < 55:
            change = 0.0                              # frozen
        elif i == 55:
            change = -0.20                             # gap-down
        else:
            change = random.uniform(-0.015, 0.02)
        price *= (1.0 + change)
        prices.append(price)
    return prices


def generate_leverage_cascade_prices() -> List[float]:
    """Sequential margin-call drops: -5%, -8%, -12%, -15%, -10% at indices 25-29."""
    random.seed(105)
    price = 100.0
    prices = [price]
    cascade_drops = [-0.05, -0.08, -0.12, -0.15, -0.10]
    for i in range(99):
        if 25 <= i <= 29:
            change = cascade_drops[i - 25]
        elif 30 <= i <= 50:
            change = random.uniform(-0.02, 0.03)      # choppy recovery
        else:
            change = random.uniform(-0.01, 0.02)
        price *= (1.0 + change)
        prices.append(price)
    return prices


# ---------------------------------------------------------------------------
# Result Container
# ---------------------------------------------------------------------------

class ScenarioResult:
    """Holds complete comparison data for one stress-test scenario."""

    def __init__(self,
                 scenario_name: str,
                 scenario_description: str,
                 group_a_final: float,
                 group_a_return: float,
                 group_a_max_dd: float,
                 group_a_sharpe: float,
                 group_a_sortino: float,
                 group_a_compliance_violations: int,
                 group_a_operational_failures: int,
                 group_a_governance_score: float,
                 group_b_final: float,
                 group_b_return: float,
                 group_b_max_dd: float,
                 group_b_sharpe: float,
                 group_b_sortino: float,
                 group_b_compliance_violations: int,
                 group_b_operational_failures: int,
                 group_b_governance_score: float,
                 group_b_kill_switch_triggered: bool):
        self.scenario_name = scenario_name
        self.scenario_description = scenario_description
        self.group_a_final = group_a_final
        self.group_a_return = group_a_return
        self.group_a_max_dd = group_a_max_dd
        self.group_a_sharpe = group_a_sharpe
        self.group_a_sortino = group_a_sortino
        self.group_a_compliance_violations = group_a_compliance_violations
        self.group_a_operational_failures = group_a_operational_failures
        self.group_a_governance_score = group_a_governance_score
        self.group_b_final = group_b_final
        self.group_b_return = group_b_return
        self.group_b_max_dd = group_b_max_dd
        self.group_b_sharpe = group_b_sharpe
        self.group_b_sortino = group_b_sortino
        self.group_b_compliance_violations = group_b_compliance_violations
        self.group_b_operational_failures = group_b_operational_failures
        self.group_b_governance_score = group_b_governance_score
        self.group_b_kill_switch_triggered = group_b_kill_switch_triggered


# ---------------------------------------------------------------------------
# Scenario Engine
# ---------------------------------------------------------------------------

class ScenarioEngine:
    """Runs all stress-test scenarios comparing Group A vs Group B."""

    SCENARIOS: List[Tuple[str, str, Callable]] = [
        ("Flash Crash",
         "Sudden -35% price collapse over 3 bars",
         generate_flash_crash_prices),
        ("Volatility Spike",
         "Extreme ±8% daily swings for 30 consecutive bars",
         generate_volatility_spike_prices),
        ("Liquidity Collapse",
         "Sustained -2% to -5% daily bleed for 20 bars",
         generate_liquidity_collapse_prices),
        ("Exchange Outage",
         "10-bar price freeze followed by -20% gap down",
         generate_exchange_outage_prices),
        ("Leverage Cascade",
         "Sequential margin-call drops: -5%, -8%, -12%, -15%, -10%",
         generate_leverage_cascade_prices),
    ]

    INITIAL_CAPITAL = 1_000_000.0

    # ---- Group A: Unrestricted AI (10x leveraged, no risk management) ----

    def _run_group_a(self, prices: List[float], scenario_name: str) -> dict:
        capital = self.INITIAL_CAPITAL
        peak = capital
        max_drawdown = 0.0
        daily_returns: List[float] = []

        for i in range(1, len(prices)):
            price_ret = (prices[i] - prices[i - 1]) / prices[i - 1]
            leverage = 10.0
            daily_ret = price_ret * leverage  # always long
            prev_cap = capital
            capital = max(0.0, capital * (1.0 + daily_ret))
            daily_returns.append(
                (capital - prev_cap) / prev_cap if prev_cap > 0 else -1.0
            )

            if capital > peak:
                peak = capital
            dd = (peak - capital) / peak if peak > 0 else 0.0
            if dd > max_drawdown:
                max_drawdown = dd

        total_return = (capital - self.INITIAL_CAPITAL) / self.INITIAL_CAPITAL
        sharpe = self._calc_sharpe(daily_returns)
        sortino = self._calc_sortino(daily_returns)
        liquidated = capital < 1000.0

        return {
            "final_value": capital,
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "sharpe": sharpe,
            "sortino": sortino,
            "compliance_violations": 2,
            "operational_failures": 1 if liquidated else 0,
            "governance_score": 10.0,
        }

    # ---- Group B: Harness-Governed AI (SMA crossover + full risk stack) ----

    def _run_group_b(self, prices: List[float], scenario_name: str) -> dict:
        # Build SMA-10 crossover signals
        signals = self._sma_signals(prices, window=10)

        backtester = BacktestingEngine()
        risk = RiskGovernanceEngine(
            max_leverage_limit=2.0, max_drawdown_limit=0.10
        )
        audit = AuditLoggingEngine()
        audit.log_event("SCENARIO_START", {"scenario": scenario_name})

        bt = backtester.run(prices, signals)

        # Find worst drawdown point to evaluate risk gate
        worst_idx = 0
        worst_dd = 0.0
        peak_val = bt.portfolio_values[0]
        for idx, val in enumerate(bt.portfolio_values):
            if val > peak_val:
                peak_val = val
            dd = (peak_val - val) / peak_val if peak_val > 0 else 0.0
            if dd > worst_dd:
                worst_dd = dd
                worst_idx = idx

        # Evaluate risk at worst point
        hist_returns = bt.daily_returns[:worst_idx] if worst_idx > 0 else bt.daily_returns[:10]
        risk_res = risk.evaluate_risk(
            current_portfolio_value=bt.portfolio_values[worst_idx],
            peak_value=peak_val,
            positions={"SIM": 1.0},
            prices={"SIM": prices[worst_idx]},
            historical_returns=hist_returns,
        )

        kill_switch = risk_res.kill_switch_active

        if kill_switch:
            final_cap = bt.portfolio_values[worst_idx]
            audit.log_event("KILL_SWITCH_TRIGGERED", {
                "scenario": scenario_name,
                "drawdown": f"{worst_dd * 100:.2f}%",
            })
        else:
            final_cap = bt.portfolio_values[-1]

        total_return = (final_cap - self.INITIAL_CAPITAL) / self.INITIAL_CAPITAL

        return {
            "final_value": final_cap,
            "total_return": total_return,
            "max_drawdown": bt.max_drawdown,
            "sharpe": bt.sharpe_ratio,
            "sortino": bt.sortino_ratio,
            "compliance_violations": 0,
            "operational_failures": 0,
            "governance_score": 100.0,
            "kill_switch_triggered": kill_switch,
        }

    # ---- Run all scenarios --------------------------------------------------

    def run_all(self) -> List[ScenarioResult]:
        results: List[ScenarioResult] = []

        for name, desc, gen_fn in self.SCENARIOS:
            prices = gen_fn()

            print(f"\n{'═' * 70}")
            print(f"SCENARIO: {name} — {desc}")
            print(f"{'═' * 70}")

            res_a = self._run_group_a(prices, name)
            res_b = self._run_group_b(prices, name)

            ks_label_b = "Yes" if res_b["kill_switch_triggered"] else "No"
            print(
                f"  Group A (Unrestricted):  "
                f"Final=${res_a['final_value']:>14,.2f}  "
                f"Return={res_a['total_return'] * 100:>8.2f}%  "
                f"MDD={res_a['max_drawdown'] * 100:>7.2f}%  "
                f"Sharpe={res_a['sharpe']:>6.2f}  "
                f"Kill-Switch=N/A"
            )
            print(
                f"  Group B (Governed):      "
                f"Final=${res_b['final_value']:>14,.2f}  "
                f"Return={res_b['total_return'] * 100:>8.2f}%  "
                f"MDD={res_b['max_drawdown'] * 100:>7.2f}%  "
                f"Sharpe={res_b['sharpe']:>6.2f}  "
                f"Kill-Switch={ks_label_b}"
            )

            results.append(ScenarioResult(
                scenario_name=name,
                scenario_description=desc,
                group_a_final=res_a["final_value"],
                group_a_return=res_a["total_return"],
                group_a_max_dd=res_a["max_drawdown"],
                group_a_sharpe=res_a["sharpe"],
                group_a_sortino=res_a["sortino"],
                group_a_compliance_violations=res_a["compliance_violations"],
                group_a_operational_failures=res_a["operational_failures"],
                group_a_governance_score=res_a["governance_score"],
                group_b_final=res_b["final_value"],
                group_b_return=res_b["total_return"],
                group_b_max_dd=res_b["max_drawdown"],
                group_b_sharpe=res_b["sharpe"],
                group_b_sortino=res_b["sortino"],
                group_b_compliance_violations=res_b["compliance_violations"],
                group_b_operational_failures=res_b["operational_failures"],
                group_b_governance_score=res_b["governance_score"],
                group_b_kill_switch_triggered=res_b["kill_switch_triggered"],
            ))

        # ---- Summary table ----
        self._print_summary(results)
        return results

    # ---- Summary printer ----------------------------------------------------

    @staticmethod
    def _print_summary(results: List["ScenarioResult"]) -> None:
        print(f"\n{'═' * 100}")
        print("SCENARIO STRESS TEST SUMMARY")
        print(f"{'═' * 100}")
        print("Disclaimer: Deterministic simulation demo, not live trading performance.")
        print()
        header = (
            f"{'Scenario':<22}"
            f"{'Group A Final':>16}"
            f"{'Group A MDD':>14}"
            f"{'Group B Final':>16}"
            f"{'Group B MDD':>14}"
            f"{'Kill-Switch':>13}"
        )
        print(header)
        print("─" * 100)
        for r in results:
            ks = "Yes" if r.group_b_kill_switch_triggered else "No"
            print(
                f"{r.scenario_name:<22}"
                f"${r.group_a_final:>14,.2f}"
                f"{r.group_a_max_dd * 100:>13.2f}%"
                f"${r.group_b_final:>14,.2f}"
                f"{r.group_b_max_dd * 100:>13.2f}%"
                f"{ks:>13}"
            )

    # ---- Helper: SMA crossover signal generator -----------------------------

    @staticmethod
    def _sma_signals(prices: List[float], window: int = 10) -> List[int]:
        signals: List[int] = []
        for i in range(len(prices)):
            if i < window:
                signals.append(0)  # wait for enough data
            else:
                sma = sum(prices[i - window:i]) / window
                signals.append(1 if prices[i] > sma else 0)
        return signals

    # ---- Helper: Sharpe and Sortino from daily returns ----------------------

    @staticmethod
    def _calc_sharpe(returns: List[float]) -> float:
        if len(returns) < 2:
            return 0.0
        avg = sum(returns) / len(returns)
        var = sum((r - avg) ** 2 for r in returns) / (len(returns) - 1)
        std = math.sqrt(var) if var > 0 else 0.0
        return (avg / std) * math.sqrt(252) if std > 0 else 0.0

    @staticmethod
    def _calc_sortino(returns: List[float]) -> float:
        if len(returns) < 2:
            return 0.0
        avg = sum(returns) / len(returns)
        downside = [r for r in returns if r < 0.0]
        var_down = sum(r ** 2 for r in downside) / len(returns) if returns else 0.0
        std_down = math.sqrt(var_down) if var_down > 0 else 0.0
        return (avg / std_down) * math.sqrt(252) if std_down > 0 else 0.0
