"""
Institutional Trade Harness - Validation Harness Engine
Author: Rignesh P
"""

import ast
import re
from typing import Dict, Any, Tuple, List

class StrategyValidationResult:
    """Stores the outcomes of validation checks."""
    def __init__(self, passed: bool, logs: List[str], score: float):
        self.passed = passed
        self.logs = logs
        self.score = score  # Validation Score between 0 and 100

class StrategyValidator:
    """
    Validates AI-generated python strategies for:
    1. Syntax errors
    2. Logical contradictions
    3. Lookahead bias (accessing future periods)
    4. Overfitting & Data Leakage (suspicious keywords, hardcoded parameters)
    """
    
    LEAKAGE_KEYWORDS = {
        "future", "lookahead", "cheat", "shift(-1)", "shift(-2)", "lead", "tomorrow"
    }
    
    OVERFITTING_KEYWORDS = {
        "hardcode", "overfit", "optimize_parameters_brute", "grid_search", "perfect_params"
    }

    @staticmethod
    def validate_code(code_str: str) -> StrategyValidationResult:
        logs = []
        passed = True
        score = 100.0

        # 1. Syntax Validation
        try:
            ast.parse(code_str)
            logs.append("Syntax Validation: PASSED")
        except SyntaxError as e:
            logs.append(f"Syntax Validation: FAILED - {str(e)}")
            return StrategyValidationResult(passed=False, logs=logs, score=0.0)

        # 2. Logic Contradictions Check
        # Example contradiction: setting target leverage that exceeds limits, or buy and sell flags simultaneously true
        contradiction_patterns = [
            (r"leverage\s*=\s*(\d+(\.\d+)?)\s*.*\s*leverage\s*>\s*(\d+(\.\d+)?)", "Possible leverage rule contradiction"),
            (r"buy\s*=\s*True\s*.*\s*sell\s*=\s*True", "Strategy triggers buy and sell flags concurrently under identical conditions")
        ]
        
        logic_issues = []
        for pattern, msg in contradiction_patterns:
            if re.search(pattern, code_str, re.IGNORECASE | re.DOTALL):
                logic_issues.append(msg)
                score -= 15.0
                
        if logic_issues:
            logs.append(f"Logic Verification: WARNING - Contradictions found: {logic_issues}")
        else:
            logs.append("Logic Verification: PASSED")

        # 3. Lookahead Bias Detection
        lookahead_issues = []
        for word in StrategyValidator.LEAKAGE_KEYWORDS:
            # Match word with boundary check or df['column'].shift(-val)
            pattern = rf"\b{word}\b|shift\(\s*-\d+\s*\)"
            matches = re.findall(pattern, code_str, re.IGNORECASE)
            if matches:
                lookahead_issues.append(f"Detected potential future leakage or lookahead keyword: {matches[0]}")
                score -= 30.0

        if lookahead_issues:
            logs.append(f"Lookahead Bias Detector: FAILED - Issues: {lookahead_issues}")
            passed = False
        else:
            logs.append("Lookahead Bias Detector: PASSED")

        # 4. Overfitting & Data Leakage Check
        overfitting_issues = []
        for word in StrategyValidator.OVERFITTING_KEYWORDS:
            pattern = rf"\b{word}\b"
            matches = re.findall(pattern, code_str, re.IGNORECASE)
            if matches:
                overfitting_issues.append(f"Detected suspicious overfitting keyword: '{matches[0]}'")
                score -= 15.0
                
        # Count hardcoded decimal parameters as a proxy for hyper-parameter tuning/overfitting
        decimals = re.findall(r"\b\d+\.\d{4,}\b", code_str)
        if len(decimals) > 5:
            overfitting_issues.append(f"Excessive high-precision floating numbers ({len(decimals)} detected) indicating highly overfitted constants")
            score -= 10.0

        if overfitting_issues:
            logs.append(f"Overfitting & Leakage Detector: WARNING - {overfitting_issues}")
        else:
            logs.append("Overfitting & Leakage Detector: PASSED")

        # Final pass constraint
        if score < 50.0:
            passed = False
            logs.append(f"Harness validation threshold not met. Score: {score}/100")
        else:
            logs.append(f"Harness validation score: {score}/100")

        return StrategyValidationResult(passed=passed, logs=logs, score=max(0.0, score))
