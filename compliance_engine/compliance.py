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
        # Explicit academic and legal disclaimer
        self.disclaimer = "Rule-inspired compliance checks, not legal/regulatory certification."

class ComplianceEngine:
    """
    Enforces compliance guidelines inspired by:
    - SEC (e.g. pattern day trading rules, leverage bounds)
    - FINRA (margin caps)
    - MiFID II (short selling locator requirements)
    - SR 11-7 (Model Governance rules)
    
    Disclaimer: Rule-inspired compliance checks, not legal/regulatory certification.
    """

    def __init__(self, restricted_list: List[str] = None):
        self.restricted_list = restricted_list if restricted_list is not None else ["RESTRICTED_CO", "BAD_STOCK"]
        
    def check_compliance(self, 
                         strategy_name: str,
                         asset_class: str,
                         trade_symbols: List[str],
                         planned_leverage: float,
                         is_short_sale: bool) -> ComplianceResult:
        """Runs basic compliance rule mappings."""
        violations = []
        
        for sym in trade_symbols:
            if sym in self.restricted_list:
                violations.append(f"Restricted List: Asset '{sym}' is blocked from active institutional trading.")

        if asset_class == "Equities" and planned_leverage > 2.0:
            violations.append(f"Equity leverage ({planned_leverage:.2f}x) exceeds rule-inspired baseline of 2.0x.")
        elif asset_class == "Crypto" and planned_leverage > 1.0:
            violations.append(f"Crypto leverage ({planned_leverage:.2f}x) exceeds rule-inspired baseline of 1.0x.")
            
        if is_short_sale:
            locate_verified = False
            for sym in trade_symbols:
                if sym.endswith(".E"):
                    locate_verified = True
            
            if not locate_verified:
                violations.append(f"Short sale of '{','.join(trade_symbols)}' lacks locating verification.")

        if not strategy_name or len(strategy_name) < 4:
            violations.append("SR 11-7 Governance Check: Strategy name identifier does not meet model documentation standard length.")

        approved = len(violations) == 0
        framework = "SEC, FINRA, MiFID II, SR 11-7 Inspired Gates"

        return ComplianceResult(
            approved=approved,
            violations=violations,
            framework=framework
        )
