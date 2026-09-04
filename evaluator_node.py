from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from graph_state import WorkbenchState

def evaluator_node(state: WorkbenchState) -> dict:
    retry_count = state.get("retry_count", 0)
    
    # 1. Prevent infinite loops
    if retry_count >= 3:
        return {"evaluator_feedback": "FAIL_MAX_RETRIES"}
        
    execution_logs = state.get("execution_logs", "")
    payload_json = state.get("payload_json", {})
    
    # 2. Fast-Pass Logic
    has_errors = False
    
    # Check for tracebacks or explicit exits in logs
    error_keywords = ["Traceback", "SyntaxError", "CRITICAL ERROR", "Execution error", "Execution timed out"]
    if any(keyword in execution_logs for keyword in error_keywords):
        has_errors = True
        
    # Check if STDERR actually contains content
    if "STDERR:" in execution_logs:
        parts = execution_logs.split("STDERR:\n")
        if len(parts) > 1 and parts[1].strip():
            has_errors = True
            
    # If no errors and we successfully parsed the payload JSON, pass!
    if not has_errors and payload_json:
        return {"evaluator_feedback": "PASS"}
        
    # 3. LLM Evaluation
    llm = ChatOllama(model="qwen2.5:3b", temperature=0.0, keep_alive=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an elite QA Manager overseeing Python code execution. The coder's script failed. Review the execution logs and provide a short, 1-line explicit instruction to the coder on how to fix the code (e.g. 'Fix the ZeroDivisionError on line 12 by checking if Delta_t is 0')."),
        ("human", "Execution Logs with error:\n{execution_logs}")
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "execution_logs": execution_logs
    })
    
    return {
        "evaluator_feedback": response.content.strip(),
        "retry_count": retry_count + 1
    }
