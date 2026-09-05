from langgraph.graph import StateGraph, START, END
from graph_state import WorkbenchState
from supervisor_node import supervisor_node
from vision_node import vision_node
from rag_node import rag_node
from coder_node import coder_node
from evaluator_node import evaluator_node
from deliverable_node import deliverable_node
from approval_analysis_node import approval_analysis_node

initial_state: WorkbenchState = {
    "user_query": "Read the scanned P&ID, find the API 510 minimum thickness formula in our docs, calculate the corrosion, and generate a Word report.",
    "image_path": "sample.png",
    "active_plan": [],
    "extracted_vision_data": "",
    "retrieved_documents": "",
    "sandbox_code": "",
    "execution_logs": "",
    "evaluator_feedback": "",
    "retry_count": 0,
    "final_deliverable_path": "",
    "audit_log": "",
    "payload_json": {},
    "task_type": "",
    "plan_metadata": {},
    "analysis_result": {},
    "approval_verification": {},
    "evidence": [],
    "final_response": ""
}

def route_next(current_node: str):
    def router(state: WorkbenchState) -> str:
        plan = state.get("active_plan", [])
        if current_node == "supervisor":
            if plan:
                return plan[0]
            return END
            
        if current_node in plan:
            idx = plan.index(current_node)
            if idx + 1 < len(plan):
                return plan[idx+1]
        return END
    return router

def route_from_evaluator(state: WorkbenchState) -> str:
    feedback = state.get("evaluator_feedback")
    if feedback == "PASS" or feedback == "FAIL_MAX_RETRIES":
        plan = state.get("active_plan", [])
        if "evaluator" in plan:
            idx = plan.index("evaluator")
            if idx + 1 < len(plan):
                return plan[idx+1]
        return END
    
    # If not pass or max retries, we assume we need to loop back to the node before evaluator (usually coder)
    # But since coder is the only one generating code right now, we route to coder
    plan = state.get("active_plan", [])
    if "coder" in plan:
        return "coder"
    return END

# --- WORKFLOW INITIALIZATION ---
workflow = StateGraph(WorkbenchState)

# --- ADD NODES ---
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("vision", vision_node)
workflow.add_node("rag", rag_node)
workflow.add_node("coder", coder_node)
workflow.add_node("approval_analysis", approval_analysis_node)
workflow.add_node("evaluator", evaluator_node)
workflow.add_node("deliverable", deliverable_node)

# --- DEFINE EDGES ---
workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges("supervisor", route_next("supervisor"))
workflow.add_conditional_edges("vision", route_next("vision"))
workflow.add_conditional_edges("rag", route_next("rag"))
workflow.add_conditional_edges("approval_analysis", route_next("approval_analysis"))

# coder always goes to evaluator in standard calculation plans
def route_from_coder(state: WorkbenchState) -> str:
    plan = state.get("active_plan", [])
    if "evaluator" in plan:
        return "evaluator"
    return route_next("coder")(state)

workflow.add_conditional_edges("coder", route_from_coder)
workflow.add_conditional_edges("evaluator", route_from_evaluator)
workflow.add_edge("deliverable", END)

app = workflow.compile()

if __name__ == "__main__":
    print("--- Starting AI Workbench LangGraph Orchestrator ---")
    print(f"Initial Query: {initial_state['user_query']}\n")
    try:
        final_state = app.invoke(initial_state)
        deliverable_path = final_state.get("final_deliverable_path")
        print("\n--- Workflow Complete ---")
        if deliverable_path and deliverable_path != "None":
            print(f"Success! Final document saved to: {deliverable_path}")
        else:
            print("Workflow finished, but no document was generated.")
    except Exception as e:
        print(f"\nWorkflow encountered a fatal error: {e}")
