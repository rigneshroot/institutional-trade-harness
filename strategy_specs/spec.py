"""
Institutional Trade Harness - Strategy Specification Engine
Author: Rignesh P
"""

import re
from typing import Dict, Any, List

class InvalidSpecError(Exception):
    """Raised when a strategy specification is invalid."""
    pass

class StrategySpec:
    """
    Defines, parses, and validates the standardized Strategy Specification Schema.
    """
    
    ALLOWED_ASSET_CLASSES = {"Equities", "FX", "Commodities", "Crypto", "FixedIncome"}
    ALLOWED_TIMEFRAMES = {"1M", "5M", "15M", "30M", "1H", "4H", "1D", "1W"}
    
    def __init__(self, spec_data: Dict[str, Any]):
        self.raw_spec = spec_data
        self.strategy_name = ""
        self.asset_class = ""
        self.timeframe = ""
        self.max_leverage = 1.0
        self.risk_limit = 0.01
        self.benchmark = ""
        
        self.validate()

    def validate(self) -> None:
        """
        Validates all fields in the strategy specification schema.
        Raises InvalidSpecError if any validation fails.
        """
        # Validate existence of required keys
        required_keys = {"strategy_name", "asset_class", "timeframe", "max_leverage", "risk_limit", "benchmark"}
        missing_keys = required_keys - self.raw_spec.keys()
        if missing_keys:
            raise InvalidSpecError(f"Missing required strategy spec keys: {missing_keys}")
            
        self.strategy_name = str(self.raw_spec["strategy_name"]).strip()
        if not self.strategy_name:
            raise InvalidSpecError("strategy_name cannot be empty")
            
        # Validate Asset Class
        self.asset_class = str(self.raw_spec["asset_class"]).strip()
        if self.asset_class not in self.ALLOWED_ASSET_CLASSES:
            raise InvalidSpecError(
                f"Invalid asset_class '{self.asset_class}'. Allowed: {self.ALLOWED_ASSET_CLASSES}"
            )
            
        # Validate Timeframe
        self.timeframe = str(self.raw_spec["timeframe"]).strip().upper()
        if self.timeframe not in self.ALLOWED_TIMEFRAMES:
            raise InvalidSpecError(
                f"Invalid timeframe '{self.timeframe}'. Allowed: {self.ALLOWED_TIMEFRAMES}"
            )
            
        # Validate and Parse Leverage (e.g. "2x" or "1.5x" or a number)
        lev_str = str(self.raw_spec["max_leverage"]).strip().lower()
        try:
            if lev_str.endswith('x'):
                self.max_leverage = float(lev_str[:-1])
            else:
                self.max_leverage = float(lev_str)
        except ValueError:
            raise InvalidSpecError(f"Invalid max_leverage format '{self.raw_spec['max_leverage']}'. Expected e.g. '2x' or 2.0")
            
        if self.max_leverage <= 0:
            raise InvalidSpecError("max_leverage must be greater than 0")
            
        # Validate and Parse Risk Limit (e.g. "3%" or 0.03)
        risk_str = str(self.raw_spec["risk_limit"]).strip()
        try:
            if risk_str.endswith('%'):
                self.risk_limit = float(risk_str[:-1]) / 100.0
            else:
                self.risk_limit = float(risk_str)
        except ValueError:
            raise InvalidSpecError(f"Invalid risk_limit format '{self.raw_spec['risk_limit']}'. Expected e.g. '3%' or 0.03")
            
        if not (0 < self.risk_limit <= 1.0):
            raise InvalidSpecError("risk_limit must be a fraction or percentage between 0 and 100% (non-inclusive of 0)")
            
        self.benchmark = str(self.raw_spec["benchmark"]).strip()
        if not self.benchmark:
            raise InvalidSpecError("benchmark cannot be empty")
            
    def to_dict(self) -> Dict[str, Any]:
        """Returns validated specification fields as a dictionary."""
        return {
            "strategy_name": self.strategy_name,
            "asset_class": self.asset_class,
            "timeframe": self.timeframe,
            "max_leverage": self.max_leverage,
            "risk_limit": self.risk_limit,
            "benchmark": self.benchmark
        }
