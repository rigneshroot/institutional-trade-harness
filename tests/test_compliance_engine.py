"""
Unit tests for Compliance Validation Engine
Author: Rignesh P
"""

from compliance_engine import ComplianceEngine

def test_compliance_restricted_asset():
    comp = ComplianceEngine(restricted_list=["BANNED_TICKER"])
    res = comp.check_compliance(
        strategy_name="CompliantTrendV1",
        asset_class="Equities",
        trade_symbols=["BANNED_TICKER"],
        planned_leverage=1.0,
        is_short_sale=False
    )
    assert not res.approved
    assert any("Restricted List: Asset 'BANNED_TICKER' is blocked" in violation for violation in res.violations)

def test_compliance_excessive_leverage():
    comp = ComplianceEngine()
    res = comp.check_compliance(
        strategy_name="CompliantTrendV1",
        asset_class="Equities",
        trade_symbols=["SPY"],
        planned_leverage=2.5,
        is_short_sale=False
    )
    assert not res.approved
    assert any("exceeds rule-inspired baseline of 2.0x" in violation for violation in res.violations)

def test_compliance_short_sale_no_locates():
    comp = ComplianceEngine()
    res = comp.check_compliance(
        strategy_name="CompliantTrendV1",
        asset_class="Equities",
        trade_symbols=["AAPL"],
        planned_leverage=1.0,
        is_short_sale=True
    )
    assert not res.approved
    assert any("lacks locating verification" in violation for violation in res.violations)

def test_compliant_run():
    comp = ComplianceEngine()
    res = comp.check_compliance(
        strategy_name="CompliantTrendV1",
        asset_class="Equities",
        trade_symbols=["SPY.E"],
        planned_leverage=1.5,
        is_short_sale=True
    )
    assert res.approved
    assert not res.violations
