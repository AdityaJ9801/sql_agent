import os
import pandas as pd
from typing import TypedDict, Annotated, List
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))

# --- TOOLS ---
def get_schema_tool() -> str:
    """Check the database for table names and column names."""
    inspector = inspect(engine)
    results = []
    for table in inspector.get_table_names():
        cols = [f"{c['name']} ({c['type']})" for c in inspector.get_columns(table)]
        results.append(f"Table: {table} | Columns: {', '.join(cols)}")
    return "\n".join(results)

def db_query_tool(query: str) -> str:
    """Execute a SQL SELECT query."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
            df.to_csv("temp_results.csv", index=False)
            return df.to_string(index=False) if not df.empty else "No rows found."
    except Exception as e:
        return f"Database Error: {str(e)}"

tools = [get_schema_tool, db_query_tool]
tool_node = ToolNode(tools)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    mode: str

model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

def call_model(state: AgentState):
    sys_prompt = SystemMessage(content=(
        "You are a SQL Data Expert. Always check the schema first. "
        "Use db_query_tool to get data. If mode is '3', end with 'DATA_READY_FOR_VISUALIZATION'."
    ))
    return {"messages": [model.invoke([sys_prompt] + state["messages"])]}

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", lambda x: "tools" if x["messages"][-1].tool_calls else END, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")
app = workflow.compile()