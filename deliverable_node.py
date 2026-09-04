try:
    from docx import Document
except ImportError:
    import sys
    sys.exit("The 'python-docx' library is required. Please install it using: pip install python-docx")

from graph_state import WorkbenchState

def deliverable_node(state: WorkbenchState) -> dict:
    """
    Deliverable Node: Generates a final Word Document report without using an LLM 
    to conserve VRAM and reduce latency.
    """
    if "deliverable" not in state.get("active_plan", []):
        return {"final_deliverable_path": "None"}
        
    audit_log = state.get("audit_log")
    if not audit_log:
        audit_log = "No audit log generated."
        
    payload_json = state.get("payload_json")
    if not payload_json:
        payload_json = {"Result": "No structured data payload generated."}
        
    # Initialize Word Document
    doc = Document()
    
    # 1. Corporate Heading
    doc.add_heading('MRPL Automated Engineering Approval Note', 0)
    
    # 2. Final Metrics
    doc.add_heading('1. Final Calculated Metrics', level=1)
    
    for key, value in payload_json.items():
        doc.add_paragraph(f"{key}: {value}", style='List Bullet')
        
    # 3. Audit Trail
    doc.add_heading('2. Execution Audit Trail', level=1)
    doc.add_paragraph(audit_log)
    
    # Save the document
    file_path = "final_approval_note.docx"
    doc.save(file_path)
    
    return {"final_deliverable_path": file_path}
