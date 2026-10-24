# ❄️ Autonomous Cold-Chain Logistics FDE Agent

[![Architecture](https://img.shields.io/badge/Orchestration-LangGraph-blue.svg)](https://langchain-ai.github.io/langgraph/)
[![Database](https://img.shields.io/badge/Database-MS%20SQL%20Server%202022-red.svg)](https://www.microsoft.com/en-us/sql-server)
[![Vector Store](https://img.shields.io/badge/Vector%20Store-Pinecone-green.svg)](https://www.pinecone.io/)
[![Embeddings](https://img.shields.io/badge/Embeddings-BAAI%2Fbge--m3-orange.svg)](https://huggingface.co/BAAI/bge-m3)
[![Inference](https://img.shields.io/badge/LLM%20Inference-Groq-black.svg)](https://groq.com/)
[![Video Walkthrough](https://img.shields.io/badge/Walkthrough-Loom%20Demo-5A67D8?logo=loom)](https://www.loom.com/share/92639047b94246f3b5633c59ee1293f9)

An enterprise-grade Forward Deployed Engineering (FDE) agent designed to autonomously detect in-transit cold-chain anomalies, assess real-time corridor environmental conditions, and synthesize deterministic, SOP-compliant mitigation plans for critical biologics and pharmaceutical cargo.

---

## 📽️ System Demo & Architecture Walkthrough

[![Watch the Demo](https://img.shields.io/badge/▶%20Watch%202--Minute%20Architecture%20Demo-Loom-blueviolet?style=for-the-badge&logo=loom)](https://www.loom.com/share/92639047b94246f3b5633c59ee1293f9)

> **Key Scenario Demonstrated:** Real-time detection of a multi-degree reefer compressor excursion, corridor thermal analysis via weather APIs, and dynamic regulatory retrieval of emergency cross-dock procedures.

---

## 🏗️ System Architecture

```text
                                  +-----------------------------+
                                  |   Streamlit Dispatcher UI   |
                                  |         (src/ui.py)         |
                                  +--------------+--------------+
                                                 |
                                     (HTTPS Zero-Trust Ingress)
                                                 |
                                  +--------------v--------------+
                                  |    Cloudflare Secure Tunnel |
                                  |       (cloudflared.exe)     |
                                  +--------------+--------------+
                                                 |
                                  +--------------v--------------+
                                  |    LangGraph Orchestrator   |
                                  |     (src/orchestrator.py)   |
                                  +---+----------+----------+---+
                                      |          |          |
            +-------------------------+          |          +-------------------------+
            |                                    |                                    |
+-----------v-----------+            +-----------v-----------+            +-----------v-----------+
| Containerized MSSQL   |            |  Open-Meteo REST API  |            |   Pinecone Vector DB  |
|  - Security View      |            |  - Real-time corridor |            |  - BAAI/bge-m3 Local  |
|    `VW_ACTIVE_FLEET`  |            |    thermal & ambient  |            |    Embeddings (Zero-  |
|  - Read-Only Excursion|            |    weather conditions |            |    Cost SOP Retrieval)|
|    Telemetry Query    |            +-----------------------+            +-----------------------+
+-----------------------+
```

---

## ⚡ Core Engineering Highlights

* **Stateful Agentic Control Plane:** Built on **LangGraph**, orchestrating complex multi-step reasoning, external tool calling, and deterministic state transitions.
* **Sub-Second Token Inference:** Leverages **Groq** LPUs for high-throughput, low-latency reasoning without cloud compute overhead.
* **Hardened Operational Telemetry:** Interfaces with an enterprise **Microsoft SQL Server 2022** instance running containerized via Docker. Operations access is secured via an air-gapped, read-only architectural abstraction layer (`FDE_VIEWS.VW_ACTIVE_FLEET`) to prevent unauthorized DDL/DML execution.
* **Hybrid Dense Vector Retrieval:** Embeds pharmaceutical standard operating procedures using local **`BAAI/bge-m3`** dense representations indexed into **Pinecone** for deterministic regulatory guidance.
* **Zero-Trust Edge Exposure:** Self-hosts the database and agent locally while establishing an ephemeral **Cloudflare Tunnel (`cloudflared`)** for live dispatcher access over public HTTPS without opening inbound router ports.

---

## 📂 Repository Layout

```text
Cold-chain-Logisitics-FDE/
├── .streamlit/
│   └── config.toml                 # Streamlit UI theme & server configuration
├── Business_pitch/
│   ├── FDE-YT-Project-Business-Presentation.pdf
│   └── Technical Design Document (TDD)_ Cold-Chain Logistics FDE.pdf
├── Data/
│   ├── cache/
│   │   └── ingestion_hash_cache.json   # Deduplication & ingestion checkpoint state
│   ├── Policy/
│   │   └── Cold_Chain_Incident_SOP.md  # Unstructured regulatory compliance SOPs
│   └── Raw/
│       └── dynamic_supply_chain_logistics_dataset.csv # Fleet telematics & sensor logs
├── Docs/
│   └── instructions.md             # Detailed engineering specifications
├── Scripts/
│   ├── ingest_legacydata.py        # Pipeline: Raw CSV -> MSSQL telemetry store
│   ├── ingest_sop_pinecone.py      # Pipeline: Markdown SOP -> BGE-M3 -> Pinecone
│   └── setup_security_and_view.sql # DDL: Schema creation & read-only operational views
├── src/
│   ├── prompts/
│   │   └── system_prompt.txt       # Hardened role and tool invocation prompt
│   ├── agent_tools.py              # Structured tool definitions (DB, Weather, SOP)
│   ├── orchestrator.py             # LangGraph state machine & reasoning logic
│   └── ui.py                       # Real-time Streamlit monitoring dashboard
├── .env.example
├── .gitattributes
├── .gitignore
├── cloudflared.exe                 # Zero-trust tunnel binary
├── docker-compose.yml              # Container orchestration for SQL Server 2022
├── README.md
└── requirements.txt                # Production dependencies
```

---

## 🚀 Quick Reproduction Guide

### 1. Prerequisites
* **Python:** 3.10+
* **Docker Desktop:** Installed and running
* **API Keys:** [Groq Cloud](https://console.groq.com) & [Pinecone](https://www.pinecone.io)

### 2. Environment Configuration
Clone the repository and set up your virtual environment:

```bash
git clone [https://github.com/sahanakannan05/Cold-chain-Logisitics-FDE.git](https://github.com/sahanakannan05/Cold-chain-Logisitics-FDE.git)
cd Cold-chain-Logisitics-FDE

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=cold-chain-sop
SQL_SERVER=localhost
SQL_PORT=1433
SQL_DATABASE=ColdChainDB
SQL_USER=sa
SQL_ADMIN_PASSWORD=YourStrongPassword!123
```

### 3. Spin Up Containerized Telemetry DB
Launch the Microsoft SQL Server container:

```bash
docker compose up -d
```

### 4. Seed Data & Security Schemas
Initialize the database schemas, seed historical fleet telemetry, and build the Pinecone SOP vector index:

```bash
# Ingest historical telemetry dataset into SQL Server
python Scripts/ingest_legacydata.py

# Vectorize compliance SOPs into Pinecone
python Scripts/ingest_sop_pinecone.py
```

### 5. Launch the Dispatcher Dashboard

Run the Streamlit frontend:

```bash
streamlit run src/ui.py
```

### 6. (Optional) Ephemeral Zero-Trust Public Ingress
To create a public, secure HTTPS endpoint via Cloudflare Tunnel:

```bash
cloudflared.exe tunnel --url http://localhost:8501
```

---

## 🛡️ Telemetry & Security Model

The database access layer strictly adheres to the principle of least privilege:
* The LLM agent **never** executes unbounded `SELECT *` statements against raw telemetry tables.
* Telemetry queries are restricted to the hardened view `FDE_VIEWS.VW_ACTIVE_FLEET`.
* Outlier sensor pings, GPS drift, and velocity anomalies are scrubbed at the SQL view layer prior to context injection, minimizing token usage and eliminating hallucination risks.

---

## 📈 Example Operational Queries

* *"Identify any active shipments experiencing critical temperature excursions and evaluate live corridor conditions for mitigation."*
* *"Reefer unit TRK-8092 reported an internal cargo temperature of 10.2°C while transporting biologics. Formulate an immediate incident response runbook."*
* *"Retrieve regulatory cross-dock requirements for ambient exposure exceeding 90 minutes under GxP compliance."*