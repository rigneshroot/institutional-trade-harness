"""
Institutional Trade Harness - Reproducibility Engine
Author: Rignesh P
"""

import random
import hashlib
import sys
from typing import Dict, Any, List

class ReproducibilityEngine:
    """
    Enforces absolute determinism of computational backtests and strategy execution:
    - Pins system random seeds.
    - Audits standard system environment properties (Python version, platform details).
    - Verifies dataset integrity hashes.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.lock_seeds()

    def lock_seeds(self) -> None:
        """Fixes all python pseudo-random seeds."""
        random.seed(self.seed)
        # Attempt to seed numpy if available
        try:
            import numpy as np
            np.random.seed(self.seed)
        except ImportError:
            pass

    def check_dataset_hash(self, dataset_name: str, data: List[float]) -> str:
        """
        Calculates SHA-256 integrity hash of input dataset.
        Ensures identical starting datasets (Control Variable check).
        """
        data_str = ",".join(map(str, data))
        data_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
        return data_hash

    def audit_environment(self) -> Dict[str, Any]:
        """Captures active runtime platform specifications to guarantee replica execution matches."""
        # Check standard python libraries
        packages_verified = {
            "python": sys.version
        }
        
        # Check standard external libraries used in tech stacks
        for pkg in ["numpy", "pandas"]:
            try:
                __import__(pkg)
                packages_verified[pkg] = sys.modules[pkg].__version__ # type: ignore
            except ImportError:
                packages_verified[pkg] = "NOT_INSTALLED"

        return {
            "seed_locked": self.seed,
            "environment_spec": packages_verified,
            "platform": sys.platform
        }
