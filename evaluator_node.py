from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from graph_state import WorkbenchState

def evaluator_node(state: WorkbenchState) -> dict:
    if "evaluator" not in state.get("active_plan", []):
        return {}
        
    task_type = state.get("task_type", "CALCULATION")
    retry_count = state.get("retry_count", 0)
    
    if retry_count >= 3:
        return {"evaluator_feedback": "FAIL_MAX_RETRIES"}

    if task_type == "CALCULATION":
        execution_logs = state.get("execution_logs", "")
        payload_json = state.get("payload_json", {})
        
        has_errors = False
        error_keywords = ["Traceback", "SyntaxError", "CRITICAL ERROR", "Execution error", "Execution timed out"]
        if any(keyword in execution_logs for keyword in error_keywords):
            has_errors = True
            
        if "STDERR:" in execution_logs:
            parts = execution_logs.split("STDERR:\n")
            if len(parts) > 1 and parts[1].strip():
                has_errors = True
                
        if not has_errors and payload_json:
            return {"evaluator_feedback": "PASS"}
            
        llm = ChatOllama(model="qwen2.5:3b", temperature=0.0, keep_alive=0)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an elite QA Manager overseeing Python code execution. The coder's script failed. Review the execution logs and provide a short, 1-line explicit instruction to the coder on how to fix the code."),
            ("human", "Execution Logs with error:\n{execution_logs}")
        ])
        chain = prompt | llm
        response = chain.invoke({"execution_logs": execution_logs})
        
        return {
            "evaluator_feedback": response.content.strip(),
            "retry_count": retry_count + 1
        }
    else:
        # General non-calculation validation
        # For example, check if approval_verification was successfully created
        if task_type in ["APPROVAL_VERIFICATION", "POLICY_COMPLIANCE", "PROCUREMENT_VERIFICATION"]:
            if state.get("approval_verification"):
                return {"evaluator_feedback": "PASS"}
            return {"evaluator_feedback": "Failed to generate approval verification structure.", "retry_count": retry_count + 1}
        
        # Default pass for other tasks
        return {"evaluator_feedback": "PASS"}
