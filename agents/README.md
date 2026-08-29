# CrediSync Multi-Agent Microservices Mesh

This directory houses the independent, serverless microservices that make up the **CrediSync Underwriting & Risk Platform**. Each agent is built using the Google Agent Development Kit (ADK) and deployed as an isolated service communicating via the Agent-to-Agent (A2A) protocol.

---

## 🏗️ Microservices Architecture

The following diagram illustrates the orchestration logic. The **Dispatcher** uses a **ParallelAgent** to kick off document intake and valuation concurrently, followed by a **LoopAgent** to manage the iterative underwriting and compliance review process.

![CrediSync Multi-Agent Workflow](..docs/assets/workflow-architecture.jpg)

---

## 📁 Service Breakdown

### 1. Ingestion Agent (`agents/ingestion_agent/`)
* **Role:** Parses incoming financial documentation, tax returns, and bank statements.
* **Key Features:** Integrates with Google Cloud Model Armor for document safety and automated data extraction.

### 2. Valuation Agent (`agents/valuation_agent/`)
* **Role:** Evaluates collateral, performs debt-to-income (DTI) solvency checks, and prices asset value.
* **Key Features:** Runs in parallel with the Ingestion Agent to slash end-to-end processing latency.

### 3. Underwriting Agent (`agents/underwriting_agent/`)
* **Role:** Computes institutional risk scores and evaluates creditworthiness using structured financial metrics.
* **Key Features:** Works inside an iterative review loop with the Compliance Agent.

### 4. Compliance Agent (`agents/compliance_agent/`)
* **Role:** Enforces regulatory guardrails, Anti-Money Laundering (AML) checks, and lending limits.
* **Key Features:** Flags borderline risk scores, triggering automated loopbacks for re-verification when necessary.

### 5. Dispatcher Agent (`agents/dispatcher_agent/`)
* **Role:** The core orchestrator managing state transitions, task distribution, and final report aggregation.
* **Key Features:** Leverages ADK primitives (`ParallelAgent`, `LoopAgent`, `SequentialAgent`) to coordinate downstream microservices seamlessly via A2A protocol endpoints.

---

## 🚀 Local Development

To spin up all microservices concurrently along with the frontend web UI, use the root orchestration script:

```bash
# From the project root directory
./run_local.sh
