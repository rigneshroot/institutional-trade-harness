"""
Tests for the Scenario Stress Testing Engine
Author: Rignesh P
"""

import sys
sys.path.insert(0, ".")

from scenario_testing.scenarios import (
    ScenarioEngine,
    generate_flash_crash_prices,
    generate_volatility_spike_prices,
    generate_liquidity_collapse_prices,
    generate_exchange_outage_prices,
    generate_leverage_cascade_prices,
)


def test_flash_crash_group_b_survives():
    """Group B preserves capital through a flash crash."""
    engine = ScenarioEngine()
    prices = generate_flash_crash_prices()
    res_b = engine._run_group_b(prices, "Flash Crash")
    assert res_b["final_value"] > 500_000, (
        f"Group B should survive flash crash, got ${res_b['final_value']:,.2f}"
    )


def test_flash_crash_group_a_devastated():
    """Group A is destroyed by a flash crash with 10x leverage."""
    engine = ScenarioEngine()
    prices = generate_flash_crash_prices()
    res_a = engine._run_group_a(prices, "Flash Crash")
    assert res_a["final_value"] < 100_000, (
        f"Group A should be devastated, got ${res_a['final_value']:,.2f}"
    )


def test_all_scenarios_run():
    """All 5 scenarios produce valid ScenarioResult objects."""
    engine = ScenarioEngine()
    results = engine.run_all()
    assert len(results) == 5, f"Expected 5 scenarios, got {len(results)}"
    for r in results:
        assert r.scenario_name, "Scenario name must not be empty"
        assert r.group_a_final >= 0, "Group A final must be non-negative"
        assert r.group_b_final >= 0, "Group B final must be non-negative"


def test_governed_always_zero_violations():
    """Group B never has compliance violations in any scenario."""
    engine = ScenarioEngine()
    results = engine.run_all()
    for r in results:
        assert r.group_b_compliance_violations == 0, (
            f"{r.scenario_name}: Group B had {r.group_b_compliance_violations} violations"
        )


def test_price_generators_deterministic():
    """Each price generator returns identical sequences on repeated calls."""
    generators = [
        generate_flash_crash_prices,
        generate_volatility_spike_prices,
        generate_liquidity_collapse_prices,
        generate_exchange_outage_prices,
        generate_leverage_cascade_prices,
    ]
    for gen in generators:
        run1 = gen()
        run2 = gen()
        assert run1 == run2, f"{gen.__name__} is not deterministic"
