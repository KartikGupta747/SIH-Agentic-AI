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

def get_supervisor_chain():
    # keep_alive=0 flushes the model from VRAM immediately after use
    llm = ChatOllama(model="qwen2.5:3b", temperature=0.0, keep_alive=0)
    structured_llm = llm.with_structured_output(SubAgentPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the Elite Supervisor Agent. Your job is to analyze the user's query and determine which sub-agents are needed to fulfill the request.
You must output a reasoning string and a list of active_plan tools. 
The available tools are exactly: "vision", "rag", "coder", "deliverable".

Here are two examples demonstrating how to map queries to the exact literal tool names:

Example 1:
User Query: "Read the invoice from invoice.png and save the total to a file."
Output: {{"reasoning": "Need to extract text from an image, then write code to save it.", "active_plan": ["vision", "coder", "deliverable"]}}

Example 2:
User Query: "Find our company policy on remote work and write a python script to email it to new hires."
Output: {{"reasoning": "Need to search documents for the policy, then write a script.", "active_plan": ["rag", "coder", "deliverable"]}}
"""),
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
