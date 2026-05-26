"""
Institutional Trade Harness - Compliance Engine
Author: Rignesh P
"""

import time
from typing import List, Dict, Any

class ComplianceResult:
    """Carries compliance status and reasoning log."""
    def __init__(self, approved: bool, violations: List[str], framework: str):
        self.approved = approved
        self.violations = violations
        self.framework = framework
        self.timestamp = time.time()

class ComplianceEngine:
    """
    Enforces compliance guidelines mapped to:
    - SEC (e.g. strict pattern day trading rules, asset constraints)
    - FINRA (e.g. leverage thresholds)
    - MiFID II (e.g. algorithm identifier tags and short selling checks)
    - SR 11-7 (Model Governance rules)
    """

    def __init__(self, restricted_list: List[str] = None):
        # List of banned tickers / assets
        self.restricted_list = restricted_list if restricted_list is not None else ["RESTRICTED_CO", "BAD_STOCK"]
        
    def check_compliance(self, 
                         strategy_name: str,
                         asset_class: str,
                         trade_symbols: List[str],
                         planned_leverage: float,
                         is_short_sale: bool) -> ComplianceResult:
        """
        Runs comprehensive regulatory checks.
        """
        violations = []
        
        # 1. Restricted Assets Check (SEC/FINRA/Insider trading controls)
        for sym in trade_symbols:
            if sym in self.restricted_list:
                violations.append(f"Restricted List Violation: Asset '{sym}' is banned from active trading.")

        # 2. Leverage Rules (SEC Rule 15c3-1 / FINRA Margin Rules)
        # Institutional leverage is capped at standard conservative levels under baseline rules
        if asset_class == "Equities" and planned_leverage > 2.0:
            violations.append(f"SEC/FINRA Violation: Equity leverage ({planned_leverage:.2f}x) exceeds standard regulatory limit of 2.0x.")
        elif asset_class == "Crypto" and planned_leverage > 1.0:
            violations.append(f"Institutional Risk Violation: Crypto leverage ({planned_leverage:.2f}x) exceeds safe margin cap of 1.0x.")
            
        # 3. Short Selling Compliance (MiFID II Short-Selling Regulations / SEC Regulation SHO)
        # Requires verified locates for short positions
        if is_short_sale:
            # Simulated locate check
            locate_verified = False
            for sym in trade_symbols:
                # Mock compliance locate check
                if sym.endswith(".E"):  # Mock easy-to-borrow assets
                    locate_verified = True
            
            if not locate_verified:
                violations.append(f"Regulation SHO / MiFID II Violation: Short sale of '{','.join(trade_symbols)}' lacks a verified locate or pre-borrow allocation.")

        # 4. SR 11-7 Model Governance
        # Must have an approved strategy structure
        if not strategy_name or len(strategy_name) < 4:
            violations.append("SR 11-7 Model Governance Violation: Strategy identifier is unapproved or lacks documentation lineage.")

        approved = len(violations) == 0
        framework = "SEC, FINRA, MiFID II, SR 11-7"

        return ComplianceResult(
            approved=approved,
            violations=violations,
            framework=framework
        )
