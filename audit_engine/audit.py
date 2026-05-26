"""
Institutional Trade Harness - Audit Logging Engine
Author: Rignesh P
"""

import json
import hashlib
import time
from typing import Dict, Any, List

class AuditLogEntry:
    """Represents a single immutable cryptographically chained audit event."""
    def __init__(self, 
                 index: int, 
                 event_type: str, 
                 payload: Dict[str, Any], 
                 prev_hash: str):
        self.index = index
        self.timestamp = time.time()
        self.event_type = event_type
        self.payload = payload
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculates SHA-256 hash of the entry content."""
        data_str = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload,
            "prev_hash": self.prev_hash
        }, sort_keys=True)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Converts entry to dictionary structure."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "hash": self.hash
        }

class AuditLoggingEngine:
    """
    Maintains an immutable chain of audit records to verify compliance history,
    trading activities, and risk actions without risk of tampering.
    """
    
    def __init__(self):
        self.chain: List[AuditLogEntry] = []
        # Create genesis block
        self.log_event("GENESIS", {"description": "Institutional Trade Harness Audit Chain Initialized."})

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> AuditLogEntry:
        """Appends a new event entry to the audit log chain."""
        index = len(self.chain)
        prev_hash = "0" if index == 0 else self.chain[-1].hash
        
        entry = AuditLogEntry(
            index=index,
            event_type=event_type,
            payload=payload,
            prev_hash=prev_hash
        )
        self.chain.append(entry)
        return entry

    def verify_chain_integrity(self) -> bool:
        """
        Validates the entire audit chain cryptographic linkages.
        Returns True if integral, False if tampering occurred.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # Recalculate hash of current block
            if current.hash != current.calculate_hash():
                return False
                
            # Verify chain linkage
            if current.prev_hash != previous.hash:
                return False
                
        return True

    def export_chain_json(self) -> str:
        """Exports the entire audit trail as a formatted JSON array."""
        return json.dumps([entry.to_dict() for entry in self.chain], indent=2)
