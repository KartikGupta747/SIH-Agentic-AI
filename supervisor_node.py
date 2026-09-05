from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from graph_state import WorkbenchState

class WorkbenchPlan(BaseModel):
    task_type: Literal[
        "CALCULATION", 
        "ENGINEERING_ANALYSIS", 
        "VISUAL_EXTRACTION", 
        "KNOWLEDGE_QUERY", 
        "POLICY_COMPLIANCE", 
        "PROCUREMENT_VERIFICATION", 
        "APPROVAL_VERIFICATION", 
        "DOCUMENT_GENERATION", 
        "GENERAL_ANALYSIS"
    ]
    intent_summary: str = Field(description="Concise operational explanation of the user intent.")
    required_agents: List[Literal["vision", "rag", "coder", "approval_analysis", "deliverable", "evaluator"]] = Field(
        description="The tools/sub-agents required to fulfill the request."
    )
    execution_order: List[Literal["vision", "rag", "coder", "approval_analysis", "deliverable", "evaluator"]] = Field(
        description="The strict sequential execution order."
    )
    requires_visual_input: bool
    requires_knowledge_retrieval: bool
    requires_calculation: bool
    requires_validation: bool
    requires_document: bool

SYSTEM_PROMPT = """You are the Lead Orchestration Supervisor for the MRPL Sovereign AI Workbench.
Your job is to understand the user's intent and classify it to build an execution plan.

TASK TYPES:
- CALCULATION: Requires deterministic math/Python code (e.g. remaining life, thickness).
- APPROVAL_VERIFICATION / POLICY_COMPLIANCE / PROCUREMENT_VERIFICATION: Policy, governance, checking delegation of powers, emergency procurement without math.
- KNOWLEDGE_QUERY: Simple question answering based on docs.
- DOCUMENT_GENERATION: Specifically requesting a note, report, or document.

AVAILABLE CAPABILITIES (AGENTS):
- "vision": Extracts data from an image. ONLY USE if the user provides an image or explicitly asks to extract from an image/scan.
- "rag": Retrieves policy, governance, procurement rules, engineering standards, or SOPs from the knowledge base.
- "coder": Writes and executes Python code for deterministic numerical calculations. ONLY USE if the task actually requires math or code. DO NOT USE for policy/procurement queries.
- "approval_analysis": Assesses compliance, procurement rules, exceptions, and delegation of powers based on retrieved evidence.
- "evaluator": Validates calculation results and execution.
- "deliverable": Generates a formal Word document (approval note, report) IF requested.

CRITICAL RULES:
1. DO NOT force every task into a calculation. If it is about policy, delegation of powers, or procurement limits, DO NOT use "coder" and DO NOT use "evaluator" (unless evaluating code). Instead, use "rag" and "approval_analysis".
2. If the user does not provide an image (image_path is empty), DO NOT use "vision".
3. Order matters. Typical orders:
   - Calculation: ["vision", "rag", "coder", "evaluator", "deliverable"]
   - Procurement/Compliance: ["rag", "approval_analysis", "deliverable"]
   - Knowledge QA: ["rag", "approval_analysis"]
"""

def get_supervisor_chain():
    llm = ChatOllama(model="qwen2.5:3b", temperature=0.0, keep_alive=0)
    structured_llm = llm.with_structured_output(WorkbenchPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "User Query: {user_query}\nImage Present: {image_present}")
    ])
    
    return prompt | structured_llm

def supervisor_node(state: WorkbenchState) -> dict:
    chain = get_supervisor_chain()
    has_image = bool(state.get("image_path"))
    plan: WorkbenchPlan = chain.invoke({"user_query": state["user_query"], "image_present": str(has_image)})
    
    # Filter out vision if no image present, just to be safe
    active_plan = plan.execution_order
    if not has_image and "vision" in active_plan:
        active_plan.remove("vision")
        
    plan_dict = plan.dict()
    plan_dict["execution_order"] = active_plan
    plan_dict["required_agents"] = active_plan

    return {
        "active_plan": active_plan,
        "task_type": plan.task_type,
        "plan_metadata": plan_dict
    }

if __name__ == "__main__":
    mock_state: dict = {
        "user_query": "We received an emergency single-vendor quote from L&T Heavy Engineering for INR 68,00,000 for replacement shell plates without an open public tender. Check the financial delegation of powers and generate an approval verification note.",
        "image_path": "",
    }
    result = supervisor_node(mock_state) # type: ignore
    print(result)
