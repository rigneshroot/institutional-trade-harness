"""
Institutional Trade Harness - Validation Harness Engine
Author: Rignesh P

Disclaimer: Deterministic simulation demo, not live trading performance.
"""

import ast
from typing import Dict, Any, List

class StrategyValidationResult:
    """Stores the outcomes of validation checks."""
    def __init__(self, passed: bool, logs: List[str], score: float):
        self.passed = passed
        self.logs = logs
        self.score = score  # Validation Score between 0 and 100

class AdvancedASTStrategyVisitor(ast.NodeVisitor):
    """
    Advanced AST Visitor to traverse code structure and identify:
    1. Lookahead Bias: Calling shift with negative period e.g. shift(-1)
    2. Subscript offsets containing additions e.g. close[i + 1]
    3. Simultaneous buy and sell flag assignments set to True inside the same scope.
    4. Usage of banned restricted tickers in string literals.
    """
    def __init__(self, restricted_list: List[str] = None):
        self.violations = []
        self.restricted_list = restricted_list if restricted_list is not None else ["RESTRICTED_CO"]
        self.has_buy_assignment = False
        self.has_sell_assignment = False

    def visit_Call(self, node: ast.Call):
        # 1. Detect negative shift lookahead calls
        if isinstance(node.func, ast.Attribute) and node.func.attr == "shift":
            if node.args:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.UnaryOp) and isinstance(first_arg.op, ast.USub):
                    if isinstance(first_arg.operand, ast.Constant) and isinstance(first_arg.operand.value, int):
                        val = first_arg.operand.value
                        if val > 0:
                            self.violations.append(f"Lookahead Bias AST check: Calling shift with negative period -{val}")
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
        # 2. Detect forward index addition offsets close[i + 2]
        if isinstance(node.slice, ast.BinOp):
            if isinstance(node.slice.op, ast.Add):
                if isinstance(node.slice.right, ast.Constant) and isinstance(node.slice.right.value, int):
                    if node.slice.right.value > 0:
                        self.violations.append(f"Lookahead Bias AST check: Subscription index contains positive addition offset +{node.slice.right.value}")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        # 3. Detect simultaneous buy/sell flag assignment
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id.lower()
                if name == "buy" and isinstance(node.value, ast.Constant) and node.value.value is True:
                    self.has_buy_assignment = True
                if name == "sell" and isinstance(node.value, ast.Constant) and node.value.value is True:
                    self.has_sell_assignment = True
                    
        if self.has_buy_assignment and self.has_sell_assignment:
            self.violations.append("Logic Contradiction AST check: Strategy sets both 'buy' and 'sell' flags to True inside the same scope.")
            
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        # 4. Detect restricted symbols inside string literals
        if isinstance(node.value, str):
            val_str = node.value
            for banned in self.restricted_list:
                if banned in val_str:
                    self.violations.append(f"Compliance AST check: Banned restricted security literal '{banned}' detected inside code block.")
        self.generic_visit(node)

class StrategyValidator:
    """
    Validates trading strategies using advanced Abstract Syntax Tree (AST) scanning.
    Identifies lookahead bias, logical contradictions, and restricted assets inside code.
    
    Disclaimer: Deterministic simulation demo, not live trading performance.
    """
    
    LEAKAGE_KEYWORDS = {"lookahead", "future_price", "tomorrow"}
    OVERFITTING_KEYWORDS = {"perfect_params", "overfit"}

    @staticmethod
    def validate_code(code_str: str, restricted_list: List[str] = None) -> StrategyValidationResult:
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

        # 2. Advanced AST scanning
        visitor = AdvancedASTStrategyVisitor(restricted_list=restricted_list)
        visitor.visit(tree)
        
        if visitor.violations:
            for violation in visitor.violations:
                logs.append(f"AST Validator: FAILED - {violation}")
                score -= 30.0
            passed = False
        else:
            logs.append("AST Validator: Lookahead and compliance checks PASSED")

        # 3. Keyword heuristic backup
        keyword_issues = []
        for word in StrategyValidator.LEAKAGE_KEYWORDS:
            if word in code_str:
                keyword_issues.append(f"Detected leakage indicator '{word}'")
                score -= 10.0
                
        for word in StrategyValidator.OVERFITTING_KEYWORDS:
            if word in code_str:
                keyword_issues.append(f"Detected suspicious overfitting tag '{word}'")
                score -= 10.0

        if keyword_issues:
            logs.append(f"Keyword Heuristic Scanner: WARNING - {keyword_issues}")
        else:
            logs.append("Keyword Heuristic Scanner: PASSED")

        score = max(0.0, score)
        if score < 50.0:
            passed = False
            logs.append(f"Harness validation threshold not met. Score: {score}/100")
        else:
            logs.append(f"Harness validation score: {score}/100")

        return StrategyValidationResult(passed=passed, logs=logs, score=score)
