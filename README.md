# Institutional Trade Harness

![Institutional Trade Harness Architecture and Workflows](docs/images/trade_harness_dashboard.png)
![Strategy Validation AST and Compliance Pipeline](docs/images/validation_pipeline.png)

An AI-governed trading infrastructure designed to constrain, validate, and supervise autonomous AI agents in regulated financial environments.

**Author:** Rignesh P  
**License:** MIT (Code), CC BY 4.0 (Visual Assets)

---

## Technical Disclaimer
* **Simulation Status:** Deterministic simulation demo, not live trading performance.
* **Compliance Checks:** Rule-inspired compliance checks, not legal/regulatory certification.

---

## Architecture Overview

The harness interposes a series of non-bypassable pre-trade validation checkpoints and active execution supervisors between the AI-generated strategies and the trading markets:

```
                      ┌─────────────────────┐
                      │   AI Trading Agent  │
                      └──────────┬──────────┘
                                 │
                                 ▼
                   ┌─────────────────────────┐
                   │ Strategy Specification  │
                   └──────────┬──────────────┘
                              ▼
                  ┌──────────────────────────┐
                  │ Validation Harness Engine│
                  └──────────┬───────────────┘
                             ▼
                  ┌──────────────────────────┐
                  │ Backtesting Engine       │
                  └──────────┬───────────────┘
                             ▼
                  ┌──────────────────────────┐
                  │ Risk Governance Engine   │
                  └──────────┬───────────────┘
                             ▼
                  ┌──────────────────────────┐
                  │ Compliance Engine        │
                  └──────────┬───────────────┘
                             ▼
                  ┌──────────────────────────┐
                  │ Audit & Logging Engine   │
                  └──────────┬───────────────┘
                             ▼
                  ┌──────────────────────────┐
                  │ Deployment Controller    │
                  └──────────────────────────┘
```

1. **Strategy Specification Engine:** Validates schema bounds (instruments, maximum leverage limits).
2. **Validation Engine:** Checks for lookahead biases using AST parsing, syntax errors, and overfitting.
3. **Backtesting Engine:** Simulates historical out-of-sample returns with transaction costs, slippage, and Buy & Hold benchmark comparisons.
4. **Risk Governance Engine:** Implements VaR / CVaR limits and active **Kill-Switch** protection.
5. **Compliance Engine:** Prevents trading of restricted assets and enforces rule-inspired baseline safety standards.
6. **Audit Logging Engine:** Chains state transitions cryptographically (SHA-256) into an immutable audit ledger.
7. **Reproducibility Engine:** Hardlocks global seeds and audits system environment configurations.
8. **Deployment Controller:** Manages Canary Rollouts (10% starting exposure) and emergency rollbacks.

---

## Getting Started

### Environment Setup

Install the package dependencies:

```bash
pip install -r requirements.txt
```

### Execution

Execute the complete empirical simulation run comparing **Group A (Unrestricted AI)** and **Group B (Harness-Governed AI)** on a synthetic deterministic SPY-like daily price sequence:

```bash
python3 run_experiments.py
```

### Unit Tests

Run the test suite using our zero-dependency test runner:

```bash
python3 run_tests.py
```

### Empirical Results

Running the simulator prints the comparative performance matrix under a historical SPY pricing sequence including a correction sell-off:

```
Metric                       Group A (Unrestricted)  Group B (Governed)    Buy & Hold (SPY)
-------------------------------------------------------------------------------------------
Sharpe Ratio                 0.22                    5.81                  3.06
Sortino Ratio                0.15                    7.12                  N/A
Max Drawdown                 76.16%                  4.94%                  15.78%
Compliance Violations        3                       0                       0
Operational Failures         1                       0                       0
Governance Score             10.0%                  100.0%                  100.0%
Final Portfolio Capital      $874,262.51          $1,290,476.10          $1,271,285.89
```

For a comprehensive analysis, review the [research.md](research.md) paper.
