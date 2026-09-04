import streamlit as st
import os
from airgap_monitor import AirGapAuditor
from main import app as langgraph_app
from graph_state import WorkbenchState

def get_vram_usage():
    """Returns active VRAM usage via nvidia-smi to bypass Windows DLL/AppLocker issues."""
    try:
        import subprocess

        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total",
                "--format=csv,nounits,noheader",
            ],
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW")
            else 0,
        )
        used_mb, total_mb = output.strip().split("\n")[0].split(",")
        used_gb = float(used_mb.strip()) / 1024
        total_gb = float(total_mb.strip()) / 1024
        return f"{used_gb:.2f} GB / {total_gb:.2f} GB"
    except Exception:
        return "Hardware metrics unavailable (Ollama Managed)"

# 1. Header & Initialization
st.set_page_config(page_title="MRPL Sovereign AI Workbench", layout="wide")
st.title("MRPL Sovereign On-Premise AI Workbench")
st.error("🔒 AIR-GAPPED ENVIRONMENT (RTX 4050 6GB VRAM) 🔒")

# 2. Sidebar Configuration
with st.sidebar:
    st.header("Settings & Hardware")
    st.metric(label="Live VRAM Usage", value=get_vram_usage())
    
    st.subheader("Data Ingestion")
    uploaded_file = st.file_uploader("Upload Inspection Report / P&ID", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Saved {uploaded_file.name} to Sandbox.")
        
    st.subheader("Knowledge Base Status")
    idx_status = "🟢 Loaded" if os.path.exists("index_data/faiss") else "🔴 Not Found"
    st.write(f"FAISS / BM25 Indices: **{idx_status}**")
    if st.button("Re-Index Documents"):
        st.info("Run `python ingest_knowledge.py` in the terminal to rebuild the Hybrid Index.")

# 3. Main Execution Area
st.subheader("Task Definition")
user_query = st.text_area(
    "Engineering Task / Prompt", 
    value="Extract the data from the scan, calculate minimum required thickness per API 510, and generate the final approval note."
)

if st.button("▶ Run Sovereign Workbench", type="primary"):
    if not uploaded_file:
        st.warning("Please upload an image/scan first for the vision node to process.")
    else:
        # Initialize Air-Gap Security Auditor
        auditor = AirGapAuditor()
        auditor.start_audit()
        
        initial_state: WorkbenchState = {
            "user_query": user_query,
            "image_path": uploaded_file.name,
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
        
        # UI Progress Indicators
        with st.status("Executing Multi-Agent Workflow...") as status:
            st.write("Initializing Air-Gap Auditor...")
            st.write("Invoking LangGraph Supervisor...")
            
            try:
                final_state = langgraph_app.invoke(initial_state)
                status.update(label="Workflow Complete!", state="complete")
            except Exception as e:
                st.error(f"Fatal error during execution: {e}")
                final_state = None

        if final_state:
            st.divider()
            st.subheader("Execution Results")
            
            # Display Structured Payload
            payload = final_state.get("payload_json", {})
            if payload:
                st.write("**[PAYLOAD_JSON] Calculated Metrics:**")
                st.json(payload)
                
            # Display Audit Log
            with st.expander("View [AUDIT_LOG] (Execution Trail)"):
                st.code(final_state.get("audit_log", "No audit log available."))
                
            # Download Deliverable
            doc_path = final_state.get("final_deliverable_path")
            if doc_path and doc_path != "None" and os.path.exists(doc_path):
                with open(doc_path, "rb") as f:
                    st.download_button(
                        label="📄 Download Final Approval Note (DOCX)",
                        data=f,
                        file_name="final_approval_note.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

        # Stop Auditor & Display Security Audit Panel
        auditor.stop_audit()
        audit_results = auditor.verify_sovereignty()
        
        st.divider()
        st.subheader("Security Audit Panel")
        
        if audit_results['status'] == "VERIFIED_AIR_GAPPED":
            st.success(f"✅ WAN Requests: {audit_results['external_calls']} | DNS Leaks: 0 | Sovereign Integrity: 100%")
        else:
            st.error(f"❌ SECURITY BREACH: {audit_results['external_calls']} outbound WAN calls detected!")
