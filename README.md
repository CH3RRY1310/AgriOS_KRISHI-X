# AGRI-OS Hackathon Build

AGRI-OS is a goal-driven Agentic AI prototype for coordinated farm decision-making.

## What is inside

- Mission Control dashboard
- Farm Digital Twin
- Goal → Plan Studio
- 8-agent network
- Conflict Resolver
- Live Signals dashboard
- Decision & Audit Log
- System Architecture view
- SQLite backend
- Human-in-the-loop approval gate
- Adaptive replanning concept
- Demo telemetry that can later be replaced by real APIs/sensors

## Core story

Farmer Goal → Coordinator → Specialist Agents → Shared Farm State → Conflict Resolution → Verification → Farmer Approval → Monitoring → Re-plan

## Tech stack

- Python
- Streamlit
- SQLite
- Pandas
- Plotly

No Java, Node.js or separate database server is required for the starter build.

## Windows setup

Open Command Prompt in this folder:

```bat
python --version
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The browser should open automatically. If not, open the local address shown in the terminal.

## Important

The current Live Signals page uses simulated telemetry for a reliable offline hackathon demo.
Clearly label demo data during judging.

For a stronger final integration, connect:
- Weather API
- Soil/IoT sensor API
- Satellite/remote-sensing source
- Crop disease/image model
- Market-price source
- Optional LLM/agent framework

The UI and SQLite state model are already structured around these adapters.

## Reset demo database

Close Streamlit and delete:

```text
agri_os.db
```

Then restart the app. It will recreate the database.

## Suggested 5-minute judging demo

1. Mission Control: explain the farmer goal.
2. Run Mission: show multiple agents reasoning in one cycle.
3. Conflict Resolver: show an explicit disagreement and resolution.
4. Farm Twin: change water reserve or budget.
5. Run again: show adaptive planning.
6. Approve plan: demonstrate farmer control.
7. Decision Log: show auditability.
8. System Architecture: explain scale to real data.

## Research grounding

The design follows current digital-agriculture themes including precision farming, climate resilience, integrated data, responsible AI, resource efficiency, and farmer-centered decision support. See `RESEARCH_NOTES.md`.
