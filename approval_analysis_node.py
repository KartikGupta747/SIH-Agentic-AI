from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from graph_state import WorkbenchState
import json

class ApprovalVerificationResult(BaseModel):
    subject: str = Field(description="The main subject of the analysis")
    request_summary: str = Field(description="Summary of the user's request")
    facts_presented: List[str] = Field(description="Facts explicitly stated by the user")
    governing_documents: List[str] = Field(description="Names or titles of the retrieved policy/governance documents")
    applicable_rules: List[str] = Field(description="Specific rules identified from the evidence")
    financial_value: Optional[str] = Field(description="The financial value if applicable")
    procurement_route: Optional[str] = Field(description="The procurement route (e.g., single vendor, open tender)")
    authority_requirement: Optional[str] = Field(description="Who must approve this based on policy")
    compliance_status: str = Field(description="One of: COMPLIANT, NON_COMPLIANT, CONDITIONAL, INSUFFICIENT_EVIDENCE, REQUIRES_APPROVAL")
    findings: List[str] = Field(description="Key findings from comparing facts to rules")
    missing_information: List[str] = Field(description="Information needed but not available in evidence")
    required_actions: List[str] = Field(description="Actions the user must take")
    approval_recommendation: str = Field(description="Final grounded recommendation")
    evidence: List[dict] = Field(description="List of evidence snippets used, e.g. {{'claim': '...', 'source': '...'}}")

SYSTEM_PROMPT = """You are an industrial procurement and governance verification analyst.

Your task is to assess the user's request ONLY against the retrieved local governance/procurement documents.

Separate:
1. user-provided facts
2. retrieved policy evidence
3. conclusions

CRITICAL RULES:
- Never invent a delegation threshold.
- Never invent an approving authority.
- Never assume an exception exists.
- Never treat absence of evidence as permission.
- If the retrieved documents do not explicitly contain the necessary information to make a decision, set compliance_status to 'INSUFFICIENT_EVIDENCE' and explain why.

Output a structured JSON response matching the required schema.
"""

HUMAN_PROMPT = """
### TASK CONTEXT
[USER REQUEST]: {user_query}

[RETRIEVED GOVERNANCE EVIDENCE]: 
{retrieved_documents}

### INSTRUCTIONS:
Assess the compliance of the request based strictly on the evidence above.
"""

def approval_analysis_node(state: WorkbenchState) -> dict:
    if "approval_analysis" not in state.get("active_plan", []):
        return {}

    llm = ChatOllama(model="qwen2.5:3b", temperature=0.0, keep_alive=0)
    structured_llm = llm.with_structured_output(ApprovalVerificationResult)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT)
    ])
    
    chain = prompt | structured_llm
    
    result: ApprovalVerificationResult = chain.invoke({
        "user_query": state.get("user_query", ""),
        "retrieved_documents": state.get("retrieved_documents", "")
    })
    
    # Also generate a final response text for knowledge queries
    final_response = f"Analysis Complete. Status: {result.compliance_status}\n\nRecommendation: {result.approval_recommendation}"
    
    return {
        "approval_verification": result.dict(),
        "final_response": final_response,
        "evidence": result.evidence
    }
