"""
Institutional Trade Harness - Deployment Controller
Author: Rignesh P
"""

import time
from typing import Dict, Any, List

class DeploymentStatus:
    """Tracks active deployment states."""
    def __init__(self, 
                 state: str, 
                 allocation_fraction: float, 
                 logs: List[str]):
        self.state = state  # "INACTIVE", "CANARY", "PROD", "ROLLED_BACK"
        self.allocation_fraction = allocation_fraction
        self.logs = logs
        self.last_update = time.time()

class DeploymentController:
    """
    Controls live promotion of strategy instances from sandbox to paper/live.
    Supports Canary Rollout, Live supervision, and Automated Rollbacks.
    """
    
    def __init__(self, initial_canary_allocation: float = 0.10):
        self.state = "INACTIVE"
        self.allocation_fraction = 0.0
        self.initial_canary_allocation = initial_canary_allocation
        self.logs = []

    def initiate_canary(self, strategy_name: str) -> DeploymentStatus:
        """Launches a controlled Canary rollout allocating a small capital segment."""
        self.state = "CANARY"
        self.allocation_fraction = self.initial_canary_allocation
        self.logs.append(f"Canary initiated for strategy '{strategy_name}' at {self.allocation_fraction * 100:.1f}% capital allocation.")
        return self.get_status()

    def promote_to_full(self) -> DeploymentStatus:
        """Promotes a successful canary to full production allocation."""
        if self.state != "CANARY":
            self.logs.append("Warning: Cannot promote strategy unless in CANARY phase.")
            return self.get_status()
            
        self.state = "PROD"
        self.allocation_fraction = 1.0
        self.logs.append("Strategy promoted to full PRODUCTION (100% allocation).")
        return self.get_status()

    def trigger_rollback(self, reason: str) -> DeploymentStatus:
        """Performs immediate emergency rollback to save capital."""
        self.state = "ROLLED_BACK"
        self.allocation_fraction = 0.0
        self.logs.append(f"EMERGENCY ROLLBACK TRIGGERED: {reason}. Allocation set to 0.0.")
        return self.get_status()

    def monitor_runtime_health(self, 
                               latency_ms: float, 
                               fill_rate: float, 
                               active_kill_switch: bool) -> bool:
        """
        Supervises execution telemetry metrics.
        Returns True if healthy, False if threshold violations warrant rollback.
        """
        if active_kill_switch:
            self.trigger_rollback("Active risk kill-switch detected")
            return False
            
        # Standard SLA limits
        if latency_ms > 100.0:  # > 100ms latency limit
            self.trigger_rollback(f"High network latency SLA breach: {latency_ms:.2f}ms")
            return False
            
        if fill_rate < 0.85:   # < 85% trade fill rate
            self.trigger_rollback(f"Low order execution fill rate: {fill_rate * 100:.1f}%")
            return False
            
        return True

    def get_status(self) -> DeploymentStatus:
        """Returns the current deployment status snapshot."""
        return DeploymentStatus(
            state=self.state,
            allocation_fraction=self.allocation_fraction,
            logs=list(self.logs)
        )
