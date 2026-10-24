# Phase 0

## Ingesting data

- Download the dataset from 'data\source\data.txt'
- Spin up the Legacy MSSQL Server
```
docker run -e ACCEPT_EULA=Y -e MSSQL_SA_PASSWORD="YourStrong@Passw0rd!" -p 1433:1433 --name mssql-legacy -d mcr.microsoft.com/mssql/server:2022-latest
```
# Phase 1

## SOP Ingestion

- https://app.pinecone.io/ > get api key
- Use it in .env
- run python scripts\ingest_sop_pinecone.py
# Phase 2

## Data Security

- Click on file : scripts\setup_security_and_view.sql
- VS-code will show you Start button directly on top else run like we were running the commands previously.
- Once done, create a new connection now with Agent-Profile
```
* Profile Name: agent-fde-ro
* Connection Group: Leave it on <Default>
* Input type: Select Parameters (Do not click "Load from Connection String", "Browse Azure", or "Browse Fabric")
* Server name*: localhost
* Port: 1433
* Trust server certificate: 🟩 Check this box / Turn it ON
* Authentication type*: SQL Login
* User name*: USR_FDE_RO
* Password*: AgentPassword2026!
* Save Password: 🟩 Check this box / Turn it ON
* Database name: Type master (or click "Select a database" and select master)
* Encrypt: Change this from Mandatory to Optional (or False)
```

Connect and test below commands :
```
-- TEST 1: This SHOULD work perfectly (Access to clean view)
SELECT TOP 5 * FROM FDE_VIEWS.VW_ACTIVE_FLEET;

-- TEST 2: This SHOULD fail instantly (Access to raw legacy table is DENIED)
SELECT TOP 5 * FROM dbo.TBL_SC_FLEET_HIST_RAW;
```
## Phase 3

run src\agent_tools.py
run src\orchestrator.py

Step-1 : Pass below in the dispatcher >
- Question-1 (The "Domino Effect" Test)
```
Find any active shipments near Los Angeles (Latitude ~33.8, Longitude ~-118.1). Check the local weather there, and tell me if the current cargo temperature violates the SOP for fresh perishables.
```

- Question-2 (The "Restraint" Test (No-Tool Routing))
```
I'm a new dispatcher on the night shift. Can you quickly explain the difference between a Tier 1 and Tier 2 escalation?
```


## Phase 4
Go to VS-code > CTRL + N > 'click on plain-text' and use 'sql'

Select the su user and write below :

CREATE TABLE FDE_VIEWS.AgentAuditLog (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    Timestamp DATETIME DEFAULT GETDATE(),
    SessionID VARCHAR(50),
    NodeExecuted VARCHAR(50),
    ToolName VARCHAR(100),
    Content NVARCHAR(MAX) -- NVARCHAR to safely handle JSON strings and large LLM outputs
);

-- Grant the agent user permission to write only to this specific table
```
GRANT INSERT ON FDE_VIEWS.AgentAuditLog TO USR_FDE_RO;
```

## Phase 5
streamlit run src\ui.py
