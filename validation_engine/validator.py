"""
Institutional Trade Harness - Validation Harness Engine
Author: Rignesh P
"""

import ast
from typing import Dict, Any, List

class StrategyValidationResult:
    """Stores the outcomes of validation checks."""
    def __init__(self, passed: bool, logs: List[str], score: float):
        self.passed = passed
        self.logs = logs
        self.score = score  # Validation Score between 0 and 100

class LookaheadVisitor(ast.NodeVisitor):
    """
    AST Visitor to traverse code structure and identify:
    1. Future shifts like shift(-1) or shift(periods=-2)
    2. Subscript offsets containing additions or forward steps e.g. df.iloc[i + 1]
    """
    def __init__(self):
        self.violations = []

    def visit_Call(self, node: ast.Call):
        # Detect shift(-1) or similar lookahead calls
        if isinstance(node.func, ast.Attribute) and node.func.attr == "shift":
            # Check positional arguments
            if node.args:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.UnaryOp) and isinstance(first_arg.op, ast.USub):
                    if isinstance(first_arg.operand, ast.Constant) and isinstance(first_arg.operand.value, int):
                        val = first_arg.operand.value
                        if val > 0:
                            self.violations.append(f"Lookahead Bias AST check: Calling shift with negative period -{val}")
            # Check keyword arguments (periods=-1)
            for keyword in node.keywords:
                if keyword.arg == "periods":
                    val_node = keyword.value
                    if isinstance(val_node, ast.UnaryOp) and isinstance(val_node.op, ast.USub):
                        if isinstance(val_node.operand, ast.Constant) and isinstance(val_node.operand.value, int):
                            val = val_node.operand.value
                            if val > 0:
                                self.violations.append(f"Lookahead Bias AST check: Calling shift with negative keyword periods -{val}")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        # Detect forward subscripting offsets e.g. close[i + 1]
        if isinstance(node.slice, ast.BinOp):
            if isinstance(node.slice.op, ast.Add):
                # Check if right operand is a constant positive integer
                if isinstance(node.slice.right, ast.Constant) and isinstance(node.slice.right.value, int):
                    if node.slice.right.value > 0:
                        self.violations.append(f"Lookahead Bias AST check: Subscription index contains positive addition offset +{node.slice.right.value}")
        self.generic_visit(node)

class StrategyValidator:
    """
    Validates trading strategies using Abstract Syntax Tree (AST) scanning.
    Identifies logical bias, syntax issues, and hyper-parameter leakage.
    
    Disclaimer: Deterministic simulation demo, not live trading performance.
    """
    
    LEAKAGE_KEYWORDS = {"lookahead", "future_price", "tomorrow"}
    OVERFITTING_KEYWORDS = {"perfect_params", "overfit"}

    @staticmethod
    def validate_code(code_str: str) -> StrategyValidationResult:
        logs = []
        passed = True
        score = 100.0

        # 1. Syntax Validation
        try:
            tree = ast.parse(code_str)
            logs.append("Syntax Validation: PASSED")
        except SyntaxError as e:
            logs.append(f"Syntax Validation: FAILED - {str(e)}")
            return StrategyValidationResult(passed=False, logs=logs, score=0.0)

        # 2. AST-Based Lookahead Bias Scanning
        visitor = LookaheadVisitor()
        visitor.visit(tree)
        
        if visitor.violations:
            for violation in visitor.violations:
                logs.append(f"AST Validator: FAILED - {violation}")
                score -= 35.0
            passed = False
        else:
            logs.append("AST Validator: Lookahead checks PASSED")

        # 3. Simple Keyword Checks (Backup heuristics)
        keyword_issues = []
        for word in StrategyValidator.LEAKAGE_KEYWORDS:
            if word in code_str:
                keyword_issues.append(f"Detected leakage indicator '{word}'")
                score -= 15.0
                
        for word in StrategyValidator.OVERFITTING_KEYWORDS:
            if word in code_str:
                keyword_issues.append(f"Detected suspicious overfitting tag '{word}'")
                score -= 10.0

        if keyword_issues:
            logs.append(f"Keyword Scanner: WARNING - {keyword_issues}")
        else:
            logs.append("Keyword Scanner: PASSED")

        # Final score calculation
        score = max(0.0, score)
        if score < 50.0:
            passed = False
            logs.append(f"Harness validation threshold not met. Score: {score}/100")
        else:
            logs.append(f"Harness validation score: {score}/100")

        return StrategyValidationResult(passed=passed, logs=logs, score=score)
