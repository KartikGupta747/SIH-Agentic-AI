from langgraph.graph import StateGraph, START, END
from graph_state import WorkbenchState
from supervisor_node import supervisor_node
from vision_node import vision_node
from rag_node import rag_node
from coder_node import coder_node
from evaluator_node import evaluator_node
from deliverable_node import deliverable_node

# --- ROUTING LOGIC ---

def route_from_supervisor(state: WorkbenchState) -> str:
    plan = state.get("active_plan", [])
    if "vision" in plan:
        return "vision"
    elif "rag" in plan:
        return "rag"
    elif "coder" in plan:
        return "coder"
    return END

def route_from_vision(state: WorkbenchState) -> str:
    plan = state.get("active_plan", [])
    if "rag" in plan:
        return "rag"
    elif "coder" in plan:
        return "coder"
    elif "deliverable" in plan:
        return "deliverable"
    return END

def route_from_rag(state: WorkbenchState) -> str:
    plan = state.get("active_plan", [])
    if "coder" in plan:
        return "coder"
    elif "deliverable" in plan:
        return "deliverable"
    return END

def route_from_evaluator(state: WorkbenchState) -> str:
    feedback = state.get("evaluator_feedback")
    if feedback == "PASS":
        if "deliverable" in state.get("active_plan", []):
            return "deliverable"
        return END
    elif feedback == "FAIL_MAX_RETRIES":
        return END
    return "coder"

# --- WORKFLOW INITIALIZATION ---
workflow = StateGraph(WorkbenchState)

# --- ADD NODES ---
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("vision", vision_node)
workflow.add_node("rag", rag_node)
workflow.add_node("coder", coder_node)
workflow.add_node("evaluator", evaluator_node)
workflow.add_node("deliverable", deliverable_node)

# --- DEFINE EDGES ---
workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges("supervisor", route_from_supervisor)
workflow.add_conditional_edges("vision", route_from_vision)
workflow.add_conditional_edges("rag", route_from_rag)

workflow.add_edge("coder", "evaluator")
workflow.add_conditional_edges("evaluator", route_from_evaluator)

workflow.add_edge("deliverable", END)

# --- COMPILE ---
app = workflow.compile()

if __name__ == "__main__":
    # Test execution block
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
        "payload_json": {}
    }
    
    print("--- Starting AI Workbench LangGraph Orchestrator ---")
    print(f"Initial Query: {initial_state['user_query']}\n")
    
    # Run the graph
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
