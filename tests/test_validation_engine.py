"""
Unit tests for Strategy Validation Engine
Author: Rignesh P
"""

from validation_engine import StrategyValidator

def test_syntax_error():
    bad_code = "def generate_signals(df):\n    return df["  # Invalid Syntax
    res = StrategyValidator.validate_code(bad_code)
    assert not res.passed
    assert "Syntax Validation: FAILED" in res.logs[0]

def test_ast_lookahead_shift():
    lookahead_code = """
def generate_signals(df):
    df['future'] = df['close'].shift(-1)
    return df['future']
    """
    res = StrategyValidator.validate_code(lookahead_code)
    assert not res.passed
    assert any("Calling shift with negative period" in log for log in res.logs)

def test_ast_lookahead_subscript():
    subscript_code = """
def generate_signals(df):
    for i in range(len(df)):
        x = df['close'][i + 2]
    return df
    """
    res = StrategyValidator.validate_code(subscript_code)
    assert not res.passed
    assert any("Subscription index contains positive addition offset" in log for log in res.logs)

def test_compliant_strategy():
    good_code = """
def generate_signals(df):
    df['sma_10'] = df['close'].rolling(10).mean()
    df['buy'] = df['close'] > df['sma_10']
    return df['buy']
    """
    res = StrategyValidator.validate_code(good_code)
    assert res.passed
    assert res.score == 100.0
