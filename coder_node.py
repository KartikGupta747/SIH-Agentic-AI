import re
import ast
import subprocess
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from graph_state import WorkbenchState

SYSTEM_PROMPT = """You are the MRPL Sovereign Calculation Engine. 
Your sole task is to write a deterministic Python 3 script to calculate Remaining Operational Life.

### THE ENGINEERING MATH:
Formula: `Remaining Life = (Measured Thickness - Retirement Limit) / Corrosion Rate`

### STRICT EXTRACTION RULES:
1. Measured Thickness: Extract this number from the User Request or Vision Data.
2. Retirement Limit: Extract this from the Retrieved Standards based on the specific material (e.g., SA-516 Grade 70 is 6.50).
3. Corrosion Rate: Extract this from the Retrieved Standards based on the specific equipment tag.

DO NOT INVENT NUMBERS. If a number is missing, the script MUST call: `sys.exit("CRITICAL ERROR: Missing parameter")`

### OUTPUT SCRIPT FORMAT:
You must output exactly one valid ```python ``` block containing the script. You MUST replace the `...` with the ACTUAL numbers extracted from the context.

```python
import sys
import json

# 1. EXACT EXTRACTED VARIABLES (REPLACE '...' WITH ACTUAL NUMBERS)
equipment_id = "..." # e.g., "V-102"
measured_thickness = ... 
retirement_limit = ... 
corrosion_rate = ... 

# 2. CALCULATION
remaining_life = (measured_thickness - retirement_limit) / corrosion_rate

# 3. AUDIT LOG
print(f"[AUDIT_LOG] Equipment ID: {{equipment_id}}")
print(f"[AUDIT_LOG] Measured Thickness: {{measured_thickness}} mm")
print(f"[AUDIT_LOG] Retirement Limit: {{retirement_limit}} mm")
print(f"[AUDIT_LOG] Corrosion Rate: {{corrosion_rate}} mm/year")
print(f"[AUDIT_LOG] Calculated Remaining Life: {{round(remaining_life, 2)}} years")

# 4. JSON PAYLOAD
payload = {{
    "equipment_id": equipment_id,
    "thickness": measured_thickness,
    "retirement_limit": retirement_limit,
    "corrosion_rate": corrosion_rate,
    "remaining_life": round(remaining_life, 2)
}}
print(f"[PAYLOAD_JSON] {{json.dumps(payload)}}")
```
"""

HUMAN_PROMPT = """
### TASK CONTEXT
[USER REQUEST]: {user_query}
[VISION DATA]: {extracted_vision_data}
[RETRIEVED STANDARDS]: {retrieved_documents}
[EVALUATOR FEEDBACK]: {evaluator_feedback}

### INSTRUCTIONS:
Write the complete Python script now following the EXACT structure provided in the system prompt.

CRITICAL KILL SWITCH: If the [RETRIEVED STANDARDS] section above is empty or missing, you MUST NOT calculate anything. You must output exactly this script:
```python
import sys
sys.exit("CRITICAL ERROR: No standards retrieved. Cannot perform hallucinated math.")
```

If standards ARE provided, do not use placeholders like `...`. You MUST replace `...` with the ACTUAL numbers found in the context above.
"""

def coder_node(state: WorkbenchState) -> dict:
    if "coder" not in state.get("active_plan", []):
        return {}

    # Initialize LLM with strict memory constraints
    llm = ChatOllama(model="qwen2.5-coder:3b", temperature=0.0, keep_alive=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT)
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "user_query": state.get("user_query", ""),
        "extracted_vision_data": state.get("extracted_vision_data", ""),
        "retrieved_documents": state.get("retrieved_documents", ""),
        "evaluator_feedback": state.get("evaluator_feedback", "")
    })
    
    generated_text = response.content
    
    # Extract code using regex
    code_match = re.search(r"```(?:python)?(.*?)```", generated_text, re.DOTALL)
    if code_match:
        extracted_code = code_match.group(1).strip()
    else:
        # Fallback
        extracted_code = generated_text.strip()
        
    # AST Pre-Flight Check
    try:
        ast.parse(extracted_code)
    except SyntaxError as e:
        return {
            "sandbox_code": extracted_code,
            "execution_logs": f"AST SyntaxError: {e}",
            "audit_log": "",
            "payload_json": {}
        }
        
    # Sandbox Execution
    sandbox_filename = "sandbox_temp.py"
    with open(sandbox_filename, "w", encoding="utf-8") as f:
        f.write(extracted_code)
        
    try:
        import sys
        result = subprocess.run(
            [sys.executable, sandbox_filename],
            capture_output=True,
            text=True,
            timeout=10)
        stdout = result.stdout
        stderr = result.stderr
        execution_logs = f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    except subprocess.TimeoutExpired as e:
        execution_logs = f"Execution timed out: {e}"
        stdout = ""
    except Exception as e:
        execution_logs = f"Execution error: {e}"
        stdout = ""
        
    # Output Parsing
    audit_lines = []
    payload = {}
    
    for line in stdout.splitlines():
        if line.startswith("[AUDIT_LOG]"):
            audit_lines.append(line)
        elif "[PAYLOAD_JSON]" in line:
            try:
                json_str = line.split("[PAYLOAD_JSON]")[1].strip()
                payload = json.loads(json_str)
            except Exception as e:
                execution_logs += f"\nJSON Parsing Error: {e}"
                
    audit_log = "\n".join(audit_lines)
    
    return {
        "sandbox_code": extracted_code,
        "execution_logs": execution_logs,
        "audit_log": audit_log,
        "payload_json": payload
    }
