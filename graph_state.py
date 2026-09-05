from typing import TypedDict, List

class WorkbenchState(TypedDict):
    user_query: str
    image_path: str
    active_plan: List[str]
    extracted_vision_data: str
    retrieved_documents: str
    sandbox_code: str
    execution_logs: str
    evaluator_feedback: str
    retry_count: int
    final_deliverable_path: str
    audit_log: str
    payload_json: dict
    
    # New generalized fields
    task_type: str
    plan_metadata: dict
    analysis_result: dict
    approval_verification: dict
    evidence: list
    final_response: str
