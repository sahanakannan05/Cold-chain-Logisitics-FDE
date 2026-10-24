import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# ==========================================
# 1. SETUP & PATH RESOLUTION
# ==========================================
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agent_tools import query_telemetry_db, fetch_corridor_conditions, search_compliance_sop

load_dotenv(project_root / ".env")

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ==========================================
# 2. FACTORY INITIALIZATION: AGENT REASONER LLM
# ==========================================
AGENT_LLM_SETTING = os.getenv("Agent_llm", "GROQ").strip().upper()

if AGENT_LLM_SETTING == "GROQ":
    print("⚡ Brain Mode: Utilizing Free High-Speed Groq Reasoner (openai/gpt-oss-20b)...")
    from langchain_groq import ChatGroq
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Missing GROQ_API_KEY in .env file.")
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        api_key=groq_api_key
    )

elif AGENT_LLM_SETTING == "OPENAI":
    print("🤖 Brain Mode: Utilizing Cloud OpenAI Reasoner (gpt-4o)...")
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

elif AGENT_LLM_SETTING == "DEEPSEEK":
    print("🐳 Brain Mode: Utilizing DeepSeek Cloud Reasoner...")
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model="deepseek-chat",
        temperature=0,
        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        max_tokens=2048,
    )

else:
    print("🤗 Brain Mode: Local Fallback Activated. Binding Local Ollama (qwen2.5:7b)...")
    from langchain_community.chat_models import ChatOllama
    llm = ChatOllama(model="qwen2.5:7b", temperature=0, num_predict=1024)

fde_tools = [query_telemetry_db, fetch_corridor_conditions, search_compliance_sop]
llm_with_tools = llm.bind_tools(fde_tools)

# ==========================================
# 3. GRAPH ARCHITECTURE ASSEMBLY
# ==========================================
def reasoning_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

print("⚙️ Compiling LangGraph FDE Orchestrator...")
graph_builder = StateGraph(AgentState)
graph_builder.add_node("reasoner", reasoning_node)
graph_builder.add_node("tools", ToolNode(fde_tools))

graph_builder.add_edge(START, "reasoner")
graph_builder.add_conditional_edges("reasoner", tools_condition)
graph_builder.add_edge("tools", "reasoner")

fde_agent = graph_builder.compile(checkpointer=MemorySaver())

# ==========================================
# 4. CHAT LOOP TESTING PANEL
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*55)
    print("🚀 FDE Supply Chain Orchestrator State Machine Online")
    print(f"    Configured Execution: [LLM: {AGENT_LLM_SETTING}] -> [Embeddings: {os.getenv('Embeddings_model', 'LOCAL')}]")
    print("="*55 + "\n")
    
    prompt_path = project_root / "src" / "prompts" / "system_prompt.txt"
    system_instructions = (
        "You are an expert Forward Deployed Engineer (FDE) AI Assistant for cold-chain logistics. "
        "You have tools to query the active fleet telemetry database, retrieve live corridor weather, "
        "and search enterprise Standard Operating Procedures (SOPs). Always verify telemetry and standard "
        "operating guidelines before proposing actionable mitigation steps."
    )
    
    if prompt_path.exists():
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                loaded_text = f.read().strip()
                if loaded_text:
                    system_instructions = loaded_text
        except Exception as e:
            print(f"Warning reading system prompt file: {e}")

    system_prompt = SystemMessage(content=system_instructions)
    thread_config = {"configurable": {"thread_id": "production_test_1"}}
    
    first_turn = True
    
    while True:
        try:
            user_input = input("\nDispatcher > ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting orchestrator.")
            break
            
        if user_input.strip().lower() in ['exit', 'quit']:
            print("Shutting down session.")
            break
        if not user_input.strip():
            continue
            
        if first_turn:
            input_messages = [system_prompt, ("user", user_input)]
            first_turn = False
        else:
            input_messages = [("user", user_input)]
            
        events = fde_agent.stream(
            {"messages": input_messages}, 
            config=thread_config, 
            stream_mode="updates"
        )
        
        for event in events:
            for node_name, node_state in event.items():
                if node_name == "tools":
                    print("   [System] 🔄 Retrieving external data elements via ToolNode...")
                elif node_name == "reasoner":
                    latest_msg = node_state["messages"][-1]
                    if latest_msg.content:
                        print(f"\n🤖 FDE Agent:\n{latest_msg.content}")