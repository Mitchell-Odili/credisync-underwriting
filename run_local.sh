#!/usr/bin/env bash

# Create clean runtime base
rm -rf local_run
mkdir -p local_run

# Symlink each agent folder directly into local_run with its proper name
ln -s ../agents/ingestion_agent local_run/ingestion
ln -s ../agents/valuation_agent local_run/valuation
ln -s ../agents/underwriting_agent local_run/underwriting
ln -s ../agents/compliance_agent local_run/compliance
ln -s ../agents/risk_critic_agent local_run/risk_critic
ln -s ../agents/dispatcher_agent local_run/dispatcher

# Safe cleanup of ports 8000 through 8006
echo "Stopping any existing processes on ports 8000-8006..."
for port in 8000 8001 8002 8003 8004 8005 8006; do
  pid=$(lsof -t -i:$port 2>/dev/null)
  if [ ! -z "$pid" ]; then
    kill -9 $pid 2>/dev/null
  fi
done

# Set the GOOGLE_CLOUD_PROJECT environment variable using the active gcloud config
export GOOGLE_CLOUD_PROJECT="$(gcloud config get-value project 2>/dev/null)"
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
  echo "Error: GOOGLE_CLOUD_PROJECT is not set. Run 'gcloud config set project YOUR_PROJECT' first."
  exit 1
fi

# Set regional boundary, Vertex AI flags, and Python path for module resolution
export GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"
export REGION="${REGION:-global}"
export GOOGLE_GENAI_USE_VERTEXAI="True"
export PYTHONPATH="$(pwd)"

echo "=================================================="
echo "Starting CrediSync Microservices Mesh (Project: $GOOGLE_CLOUD_PROJECT, Region: $GOOGLE_CLOUD_LOCATION)..."
echo "=================================================="

echo "Starting Ingestion Agent on port 8001..."
pushd agents/ingestion_agent
uv run python ../../shared/adk_app.py --host 0.0.0.0 --port 8001 --a2a ../../local_run/ingestion &
INGESTION_PID=$!
popd

echo "Starting Valuation Agent on port 8002..."
pushd agents/valuation_agent
uv run python ../../shared/adk_app.py --host 0.0.0.0 --port 8002 --a2a ../../local_run/valuation &
VALUATION_PID=$!
popd

echo "Starting Underwriting Agent on port 8003..."
pushd agents/underwriting_agent
uv run python ../../shared/adk_app.py --host 0.0.0.0 --port 8003 --a2a ../../local_run/underwriting &
UNDERWRITING_PID=$!
popd

echo "Starting Compliance Agent on port 8004..."
pushd agents/compliance_agent
uv run python ../../shared/adk_app.py --host 0.0.0.0 --port 8004 --a2a ../../local_run/compliance &
COMPLIANCE_PID=$!
popd

echo "Starting Risk Critic Agent on port 8006..."
pushd agents/risk_critic_agent
uv run python ../../shared/adk_app.py --host 0.0.0.0 --port 8006 --a2a ../../local_run/risk_critic &
RISK_CRITIC_PID=$!
popd

# Configure remote connection URLs for the dispatcher orchestrator agent
export INGESTION_AGENT_CARD_URL=http://localhost:8001/a2a/agent/.well-known/agent-card.json
export VALUATION_AGENT_CARD_URL=http://localhost:8002/a2a/agent/.well-known/agent-card.json
export UNDERWRITING_AGENT_CARD_URL=http://localhost:8003/a2a/agent/.well-known/agent-card.json
export COMPLIANCE_AGENT_CARD_URL=http://localhost:8004/a2a/agent/.well-known/agent-card.json
export RISK_CRITIC_AGENT_CARD_URL=http://localhost:8006/a2a/agent/.well-known/agent-card.json

echo "Starting Dispatcher Orchestrator Agent on port 8005..."
pushd agents/dispatcher_agent
uv run python ../../shared/adk_app.py --host 0.0.0.0 --port 8005 --a2a ../../local_run/dispatcher &
DISPATCHER_PID=$!
popd

# Wait a moment for microservices to initialize
sleep 3

echo "Starting ADK Web UI / Dashboard on port 8000..."
export DISPATCHER_AGENT_URL=http://localhost:8005

# Launch the native ADK web interface using uv run
uv run adk web --allow_origins "regex:https://.*\.cloudshell\.dev" --reload_agents --port 8000 &
WEB_PID=$!

echo ""
echo "=================================================="
echo "All CrediSync services and agents are running!"
echo "--------------------------------------------------"
echo "Ingestion Service:      http://localhost:8001"
echo "Valuation Service:      http://localhost:8002"
echo "Underwriting Service:   http://localhost:8003"
echo "Compliance Service:     http://localhost:8004"
echo "Risk Critic Service:    http://localhost:8006"
echo "Dispatcher Service:     http://localhost:8005"
echo "ADK Web UI (Dashboard): http://localhost:8000"
echo "=================================================="
echo "Press Ctrl+C to stop all services cleanly."
echo ""

# Wait for all background processes and handle clean exit
trap "kill $INGESTION_PID $VALUATION_PID $UNDERWRITING_PID $COMPLIANCE_PID $RISK_CRITIC_PID $DISPATCHER_PID $WEB_PID 2>/dev/null; rm -rf local_run; exit" INT
wait