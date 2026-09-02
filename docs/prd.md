# Product Requirements Document (PRD): CrediSync Underwriting & Risk Platform

## 1. Executive Summary & Background
Financial service providers often struggle with manual document processing, fragmented credit evaluations, and disconnected regulatory compliance checks. These bottlenecks lead to extended processing timelines, limited visibility for applicants and loan officers, and increased operational risk. 

**CrediSync** is an enterprise multi-agent platform designed to automate loan applications, document ingestion, solvency valuation, institutional risk scoring, and regulatory compliance screening via a secure, scalable microservices architecture built on Google Cloud.

## 2. Product Objectives & Scope
* **End-to-End Digitization:** Automate loan package progression from initial application submission to final regulatory and risk-based approval.
* **Specialized Microservice Collaboration:** Decouple monolithic operations into independent, containerized agents communicating securely via the Agent-to-Agent (A2A) protocol.
* **Enterprise Security & Governance:** Enforce Zero-Trust service-to-service communication, Google Cloud Model Armor input sanitization, and immutable audit trails.

## 3. System Architecture & Component Breakdown

```text

                    Underwriting Request
                            │
                            ▼
                       Dispatcher
                            │
                            ▼
                    Ingestion Agent
                   (Document Parsing)
                            │
                            ▼
                    Valuation Agent
                  (Solvency & Ratios)
                            │
                            ▼
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
       ┌──────────┐   ┌───────────┐   ┌──────────┐
       │   Loop   │   │   Loop    │   │   Loop   │
       │  Under-  │   │   Risk    │   │ Compli-  │
       │ writing  │   │  Critic   │   │   ance   │
       └────┬─────┘   └─────┬─────┘   └────┬─────┘
            │               │              │
            └───────────────┼──────────────┘
                            ▼
              Decision + Evidence (Cloud Spanner)
```

- **Dispatcher Service (`dispatcher_agent`)**: Manages asynchronous workflow orchestration using `LoopAgent`, `SequentialAgent`, and `RemoteA2aAgent` compiling final approval packages.
- **Ingestion Service (`ingestion_agent`)**: Accepts and parses unstructured financial documents uploaded by loan applicants, such as tax returns and bank statements with Model Armor input sanitization.
- **Valuation Service (`valuation_agent`)**: Reaches out to external APIs such as credit bureaus and property appraisers to evaluate borrower risk. 
- **Underwriting Service (`underwriting_agent`)**: Evaluates policy rules and credit metrics, committing intermediate state directly to **Cloud Spanner** for durable transaction tracking.
- **Risk Critic (`risk_critic_agent`)**: Operates as a deterministic control layer verifying model outputs against hard risk thresholds, separating AI reasoning from final authority.
- **Compliance Service (`compliance_agent`)**: Acts as the final regulatory and policy gatekeeper, validating underwriting packages against statutory lending limits, checking AML/sanctions criteria, and generating immutable audit traces.
- **Agent App (`app`)**: A web application that queries the dispatcher agent, displays progress, and renders performance waterfall analytics via Cloud Shell Web Preview.

## 4. Key Features & Advanced Capabilities

| Feature / Capability | Description & Technical Implementation | Acceptance Criteria |
| :--- | :--- | :--- |
| **High Performance Parallel Concurrency** | Dispatcher Agent launches Ingestion and Valuation agents concurrently using `asyncio.gather()`. | Execution SLAs must decrease by $\ge 50\%$ compared to sequential processing. |
| **Agent Egress Gateway Proxy** | Outbound tool calls pass through an egress proxy enforcing domain whitelisting and PII redaction. | Unauthorized external domain requests are intercepted and blocked with a `403 Forbidden` log. |
| **Google Cloud Model Armor Integration** | Input document sanitization against prompt injection, jailbreaking, and toxic content. | Malicious text payloads are flagged and stripped prior to agent token consumption. |
| **ADK Lifecycle Context Hooks** | Utilization of `ToolContext` and `CallbackContext` for session state stores and hooks. | Context state variables persist securely across microservice hand-offs. |
| **Workflow State Machine Agent** | Manages state transitions (`RECEIVED` $\rightarrow$ `VALIDATED` $\rightarrow$ `SOLVENT` $\rightarrow$ `UNDERWRITTEN` $\rightarrow$ `APPROVED`). | System supports Human-in-the-Loop (HITL) pause/resume override decision checkpoints. |
| **ADK Web Studio & Performance Dashboard** | Live browser dashboard (`python agents_cli.py web`) for visual topology inspection and performance waterfall analysis. | Renders live latency waterfall metrics and step-by-step tracing for active sessions. |

## 5. Functional Requirements (FR)

| ID | Feature / Module | Description | Acceptance Criteria |
| --- | --- | --- | --- |
| **FR-01** | **Parallel Ingestion & Valuation** | The Dispatcher must invoke Ingestion and Valuation concurrently using asynchronous patterns. | Combined response latency must decrease significantly compared to sequential processing. |
| **FR-02** | **Model Armor Sanitization** | Scans incoming documents for prompt injection, jailbreaking, and toxic payloads before agent consumption. | Malicious payloads are intercepted, flagged, and logged with status `BLOCKED`. |
| **FR-03** | **Institutional Risk Scoring** | Underwriting agent queries BigQuery transaction records to produce a quantitative risk score. | Scores map accurately to defined internal risk grading thresholds (`Tier 1` to `Tier 4`). |
| **FR-04** | **Regulatory Compliance Check** | Compliance agent evaluates the package against lending limits and AML/sanctions criteria. | Flagged packages are diverted to manual review with generated adverse-action reason codes. |
| **FR-05** | **Cloud Run Portability** | Each agent must be containerized independently and communicate via authenticated A2A protocols. | Services authenticate seamlessly using IAM OIDC ID tokens (`authenticated_httpx.py`). |

## 6. Non-Functional Requirements (NFR)
* **Security:** Zero-Trust networking with encrypted payloads and service-to-service authentication.
* **Scalability:** Serverless auto-scaling on Google Cloud Run allowing independent scaling of high-load microservices (e.g., Ingestion).
* **Reliability & State Persistence**: Guaranteed transaction persistence via **Cloud Spanner** to ensure state survives ephemeral container restarts.
* **Observability:** Centralized execution tracing via ADK lifecycle hooks (`ToolContext` and `CallbackContext`) and strcutured log collection.
