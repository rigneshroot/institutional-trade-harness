"""
Unit tests for Audit Logging Engine
Author: Rignesh P
"""

import json
from audit_engine import AuditLoggingEngine

def test_audit_genesis_creation():
    audit = AuditLoggingEngine()
    assert len(audit.chain) == 1
    assert audit.chain[0].event_type == "GENESIS"
    assert audit.chain[0].prev_hash == "0"
    assert audit.verify_chain_integrity()

def test_audit_hash_chain_linkage():
    audit = AuditLoggingEngine()
    audit.log_event("STRATEGY_RUN", {"status": "SUCCESS"})
    audit.log_event("RISK_CHECK", {"leverage": 1.5})
    
    assert len(audit.chain) == 3
    assert audit.chain[1].prev_hash == audit.chain[0].hash
    assert audit.chain[2].prev_hash == audit.chain[1].hash
    assert audit.verify_chain_integrity()

def test_audit_tampering_detection():
    audit = AuditLoggingEngine()
    audit.log_event("COMPLIANCE_RUN", {"approved": True})
    
    # Attempt to tamper with the first log block after generation
    audit.chain[0].payload["description"] = "TAMPERED DATA"
    
    # Integrity check must fail
    assert not audit.verify_chain_integrity()
