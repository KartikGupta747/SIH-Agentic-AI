from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from graph_state import WorkbenchState

class SubAgentPlan(BaseModel):
    reasoning: str = Field(description="Chain-of-Thought reasoning for the selected active plan.")
    active_plan: List[Literal["vision", "rag", "coder", "deliverable"]] = Field(
        description="The sequence of tools/sub-agents required to fulfill the request."
    )

SYSTEM_PROMPT = """You are the Routing Supervisor for MRPL. You MUST map the user's query to a list of tools.

AVAILABLE TOOLS: "vision", "rag", "coder", "deliverable"

STRICT KEYWORD RULES:
- If the query contains ["image", "scan", "P&ID", "photo", "extract"], YOU MUST output "vision".
- If the query contains ["standards", "API", "SOP", "search", "check", "policy"], YOU MUST output "rag".
- If the query contains ["calculate", "life", "thickness", "formula", "math"], YOU MUST output "coder".
- If the query contains ["note", "report", "document", "generate", "Word"], YOU MUST output "deliverable".

You can select multiple tools. If you do, order them EXACTLY as: ["vision", "rag", "coder", "deliverable"].

EXAMPLE:
Query: "Extract from scan, search standards to calculate life, generate note."
Output: {{"reasoning": "scan=vision, standards=rag, calculate=coder, note=deliverable", "active_plan": ["vision", "rag", "coder", "deliverable"]}}
"""

def get_supervisor_chain():
    # keep_alive=0 flushes the model from VRAM immediately after use
    llm = ChatOllama(model="qwen2.5:3b", temperature=0.0, keep_alive=0)
    structured_llm = llm.with_structured_output(SubAgentPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{user_query}")
    ])
    
    return prompt | structured_llm

def supervisor_node(state: WorkbenchState) -> dict:
    chain = get_supervisor_chain()
    plan: SubAgentPlan = chain.invoke({"user_query": state["user_query"]})
    return {"active_plan": plan.active_plan}

if __name__ == "__main__":
    # Test Harness mocking a WorkbenchState
    mock_state: WorkbenchState = {
        "user_query": "Extract the mathematical formula from equation.jpg, search our docs for its physical meaning, and write a python solver script.",
        "image_path": "equation.jpg",
        "active_plan": [],
        "extracted_vision_data": "",
        "retrieved_documents": "",
        "sandbox_code": "",
        "execution_logs": "",
        "evaluator_feedback": "",
        "retry_count": 0,
        "final_deliverable_path": ""
    }
    
    print(f"User Query: {mock_state['user_query']}")
    print("Invoking Supervisor Node...")
    try:
        result = supervisor_node(mock_state)
        print(f"Resulting state update: {result}")
    except Exception as e:
        print(f"Error during execution: {e}")
