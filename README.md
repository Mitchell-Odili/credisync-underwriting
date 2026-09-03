# Credisync-underwriting 
### Agentic AI for Credit Underwriting

CrediSync is a multi-agent AI underwriting platform exploring how complex credit decisions can be decomposed into specialized AI services while maintaining security, durable state, governance, and deterministic controls.

Instead of asking a single LLM to decide whether a borrower should be approved, CrediSync orchestrates specialized agents for data ingestion, valuation, underwriting, compliance, and risk critique.

---
## 🏗️ High Level Pipeline Architecture

This diagram illustrates the sequential workflow execution, the nested loop review block, and state persistence touchpoints across the agent pipeline:

![CrediSync Multi-Agent Workflow](docs/assets/workflow-architecture.jpg)

---

## 🏛️ Micro Services Architecture
Credisync uses a distributed microservices architecture where each agent runs in its own container and communicates securely via the Agent-2-Agent (A2A) protocol over HTTP:

- **Dispatcher Service (`dispatcher`)**: Summarizes the lending package, manages workflow coordination using `LoopAgent`, `SequentialAgent`, and `RemoteA2aAgent` and writes the final output to a shared cloud workspace.
- **Ingestion Service (`ingestion`)**: Accepts and parses unstructured financial documents uploaded by loan applicants, such as tax returns and bank statements with Model Armor input sanitization.
- **Valuation Service (`valuation`)**: Reaches out to (mock) external APIs such as credit bureaus and property appraisers to evaluate borrower risk.
- **Underwriting Service (`underwriting`)**: Accesses private database tables in BigQuery containing client transaction records to perform institutional risk scoring.
- **Compliance Service (`compliance_agent`)**: Acts as the final regulatory and policy gatekeeper, evaluating underwriting packages against configured lending policies and compliance requirements, including AML/sanctions checks, and records audit events.
- **Risk Critic Service (`risk_critic_agent`)**: Acts as the risk governance layer, executing deterministic Python risk evaluations to enforce institutional risk appetite rules and trigger refinement loops for high-value exposures.
- **Agent App (`app`)**: A web application that queries the dispatcher agent, displays progress, and renders performance waterfall analytics (accessible via local browser or Cloud Shell Web Preview).

---

## 💡 Key Design Decisions
- **Specialized agents**: Separates ingestion, valuation, underwriting, compliance, and risk responsibilities.
- **A2A communication**: Enables independently deployable agent services.
- **Durable state**: Spanner separates business state from ephemeral Cloud Run execution.
- **Model Armor**: Screens untrusted inputs and model outputs for threats and sensitive-data leakage before information crosses the AI boundary.
- **Deterministic risk controls**: A Python-based risk critic provides a non-LLM control layer for risk-sensitive decisions.
- **OIDC authentication**: Establishes authenticated service-to-service trust boundaries.

---

## ☁️ Enterprise Cloud Infrastructure

For production deployments, CrediSync maps onto a production-oriented Google Cloud architecture utilizing **Cloud Run** for independently deployable services, **Cloud Spanner** for durable transactional state, **Model Armor** for input sanitization and output data-leak detection, **Secret Manager** for secure credential management, external APIs, and authenticated **A2A communication**.


![Enterprise Multi-Agent Architecture](docs/assets/enterprise-architecture.jpg)

---

## 🔐 Enterprise Memory & State Management
Following strict enterprise cloud security guidelines, **agent memory** is never kept solely in local container RAM to prevent broken multi-turn conversations during scaling events or container recycling. Instead, the application employs a two-tier model:

1. **Ephemeral Runtime State (`tool_context.state`)**: Provides low-latency shorthand context for active agent execution loops.
2. **Durable Enterprise Persistence (Google Cloud Spanner)**: Instantly externalizes transaction records to a managed, ACID-compliant, encrypted operational store (`OLTP`), providing durable transactional state and supporting resilience, auditability, and controlled data access.

---
## 🗂️ Project Structure
```
credisync-underwriting/
├── database/                # Spanner DDL schema definitions and database guides
│   └── schema.sql
├── agents/                  # Contains individual agent directories and SKILL.md files
│   ├── ingestion_agent/
│   ├── underwriting_agent/
│   ├── valuation_agent/
|   ├── compliance_agent/
│   ├── risk_critic_agent/
│   └── dispatcher_agent/
├── shared/                  # Common schemas, Pydantic models, configuration, database client, logging callbacks, Model Armor security, tests, and A2A protocol helpers
├── config/                  # Cloud Run deployment configs & environment variables
└── main.py                  # Orchestration entrypoint
```

### 🔗 Shared Files
The `shared/` directory contains core modules shared across all agents and the web application. To eliminate code duplication, these files can be linked into respective subdirectories as [**symlinks**](https://en.wikipedia.org/wiki/Symbolic_link):
- `config.py` – Centralized dictionary mapping microservices to specific Gemini model tiers (`gemini-3.5-flash-lite`).
- `schemas.py` – Pydantic data models for loan applications, ingestion, valuation, underwriting, compliance, and final lending packages
- `db.py` – Google Cloud Spanner transactional mutation wrapper (`SpannerClientWrapper`) for secure operational state persistence.
- `rate_limiter.py` – Robust retry decorator handling `429 ResourceExhausted` errors and automatically managing Gemini API free-tier 15 RPM rate limits.
- `logging_callback.py` – Structured JSON logging callbacks tracking agent execution phases, lifecycle events, and invocation timing.
- `model_armor_callback.py` – Security perimeter callbacks (`before_model_callback` / `after_model_callback`) for blocking prompt injections and data leaks.
- `tests/` – Unit tests (`test_logging.py`, `test_model_armor.py`) validating shared utility modules.
- `a2a_utils.py` – Contains code for rewriting agent URLs in A2A AgentCards when deployed in Google Cloud Run.
- `adk_app.py` – ADK API Service implementation with built-in A2A functionality and lifecycle hook management (`ToolContext`/ `CallbackContext`).
- `authenticated_httpx.py` – [httpx](https://www.python-httpx.org/) client extension configured for secure [service-to-service requests](https://docs.cloud.google.com/run/docs/authenticating/service-to-service) with OIDC ID tokens.

---
## 📋 Requirements

*   **uv**: Python package manager (required for local development).
*   **Google Cloud SDK**: Required for GCP service authentication, secret management, and Cloud Run deployments

## ⚡ Quick Start

1.  **Install Dependencies:**
    ```bash
    uv sync
    ```

2.  **Set up credentials:**
    Ensure you have Google Cloud credentials available. You might need to run:
    ```bash
    gcloud auth application-default login
    ```
    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export SPANNER_INSTANCE_ID="your-spanner-instance-id"
    export SPANNER_DATABASE_ID="your-database-id"
    ```
3. **Initialize Database**:
    Create your Spanner instance/database using Google Standard SQL and apply the DDL script in [database/schema.sql](database/schema.sql).

4.  **Run Locally:**
    Make the orchestration script executable and start the mesh:
    ```bash
    chmod +x run_local.sh
    ./run_local.sh
    ```
    This will boot up all individual microservices and the web app processes concurrently.

5.  **Access the App:**
    Open **http://localhost:8000** in your browser.

---

## 🚢 Deployment

To deploy to Google Cloud Run, containerize and deploy each service individually, then configure the Dispatcher/Orchestrator service with the secure endpoint URLs of the downstream microservices.

1.  **Deploy Microservices:**
    Deploy the `ingestion/`, `valuation/`, `underwriting/`, `compliance/`, `risk_critic/`, and `dispatcher/` folders as separate Cloud Run services. Note down their assigned HTTPS service URLs (e.g., `https://ingestion-xyz.a.run.app`).

2.  **Deploy Agent App & Configure Environment Variables:**
    Deploy the dispatcher/app folder to Cloud Run and configure the following environment variables to wire up the Agent-to-Agent network via Agent Cards:
    *   `INGESTION_AGENT_CARD_URL`: `https://<ingestion-url>/.well-known/agent-card.json`
    *   `VALUATION_AGENT_CARD_URL`: `https://<valuation-url>/.well-known/agent-card.json`
    *   `UNDERWRITING_AGENT_CARD_URL`: `https://<underwriting-url>/.well-known/agent-card.json`
    *   `COMPLIANCE_AGENT_CARD_URL`: `https://<compliance-url>/.well-known/agent-card.json`
    *   `RISK_CRITIC_AGENT_CARD_URL`: `https://<risk-critic-url>/.well-known/agent-card.json`
    *   `AGENT_URL`: `https://<dispatcher-url>`

3.  **Access:**
    Open the deployed Dispatcher App URL in your browser.

