import re
import ast
import subprocess
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from graph_state import WorkbenchState

SYSTEM_PROMPT = """
You are the Sovereign Industrial Calculation Engine for Mangalore Refinery and Petrochemicals Limited (MRPL).
Your sole function is to write a standalone, executable Python 3 script that performs deterministic engineering calculations based strictly on the provided context.

### CORE OPERATIONAL DIRECTIVES:
1. ZERO-ASSUMPTION PRINCIPLE (ANTI-HALLUCINATION):
   - You must declare all input variables at the very beginning under the `# --- INPUT VARIABLES ---` section.
   - Extract numerical values ONLY from the [Vision Data] and governing equations ONLY from the [Retrieved Standards].
   - NEVER assume, estimate, or fabricate missing numerical values (e.g., design pressure, joint efficiency, allowable stress).
   - If any critical parameter required by the engineering formula is missing from the input context, the script MUST explicitly terminate with:
     sys.exit("CRITICAL ERROR: Missing parameter [<parameter_name>] from input data.")

2. EXECUTION ENVIRONMENT CONSTRAINTS:
   - Use ONLY Python 3 Standard Library modules (`math`, `sys`, `json`, `datetime`).
   - DO NOT import external libraries (`scipy`, `numpy`, `pandas`, `sympy`, `openpyxl`).
   - All code must run in an air-gapped, isolated environment with zero network calls.

3. DUAL-CHANNEL OUTPUT FORMAT:
   - Your script must print human-auditable calculation steps prefixed with `[AUDIT_LOG]`.
   - Your script must conclude by printing a single JSON string prefixed with `[PAYLOAD_JSON]`.
   - Never print raw floating-point numbers without rounding (use round(val, 3) or round(val, 4)).

4. OUTPUT ENVELOPE:
   - Output ONLY executable Python code enclosed in a single ```python ... ``` block.
   - Do NOT write introductions, explanations, summaries, or post-scripts.
   - Do NOT include markdown text outside the code fence.
CRITICAL: You must explicitly close all dictionaries with `}}` before calling `print()`. Never truncate the final JSON output.
"""

HUMAN_PROMPT = """
### ENGINEERING TASK CONTEXT

[USER REQUEST]:
{user_query}

[VISION DATA - EXTRACTED FROM INSPECTION SCAN/P&ID]:
{extracted_vision_data}

[RETRIEVED STANDARDS - GOVERNING SOPs / API / ASME FORMULAS]:
{retrieved_documents}

[EVALUATOR FEEDBACK / PREVIOUS RUN LOGS]:
{evaluator_feedback}

---

### MANDATORY SCRIPT SKELETON:
Your generated Python script MUST strictly follow this sequential structure:

```python
import sys
import json
import math

# -------------------------------------------------------------
# 1. INPUT VARIABLE BINDING & VALIDATION
# -------------------------------------------------------------
# Bind values extracted from [Vision Data]. If missing, trigger sys.exit().
try:
    # Example: t_actual = 7.2  # mm
    pass
except Exception as e:
    sys.exit(f"DATA PARSING ERROR: {{e}}")

# -------------------------------------------------------------
# 2. DETERMINISTIC FORMULAS & CALCULATION (API / ASME Standards)
# -------------------------------------------------------------
# Implement the mathematical equations from [Retrieved Standards].

# -------------------------------------------------------------
# 3. AUDIT TRAIL GENERATION ([AUDIT_LOG])
# -------------------------------------------------------------
# print("[AUDIT_LOG] Step 1: Baseline inputs verified...")

# -------------------------------------------------------------
# 4. STRUCTURED DELIVERABLE PAYLOAD ([PAYLOAD_JSON])
# -------------------------------------------------------------
# print(f"[PAYLOAD_JSON] {{json.dumps(results)}}")
```
Generate the complete, runnable Python script now adhering strictly to the skeleton above:
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
