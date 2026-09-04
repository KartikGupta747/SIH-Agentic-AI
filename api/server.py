import os
import sys
import shutil
import json
import uuid
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from main import app as langgraph_app
    from airgap_monitor import AirGapAuditor
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    sys.exit(1)

app = FastAPI(title="MRPL Sovereign AI Workbench API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for runs
RUN_JOBS = {}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/workflow/run")
async def create_workflow_run(
    image: UploadFile = File(...),
    user_query: str = Form(...)
):
    run_id = str(uuid.uuid4())
    temp_image_path = f"temp_{run_id}_{image.filename}"
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    full_temp_path = os.path.join(project_root, temp_image_path)
    
    with open(full_temp_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
        
    initial_state = {
        "user_query": user_query,
        "image_path": temp_image_path,
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
    
    RUN_JOBS[run_id] = {
        "initial_state": initial_state,
        "status": "created",
        "timestamp": time.time()
    }
    
    return {"run_id": run_id}

@app.get("/api/workflow/stream/{run_id}")
async def stream_workflow(run_id: str):
    job = RUN_JOBS.get(run_id)
    if not job:
        raise HTTPException(status_code=404, detail="Run not found")
        
    initial_state = job["initial_state"]
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    async def async_event_generator():
        original_cwd = os.getcwd()
        try:
            os.chdir(project_root)
            auditor = AirGapAuditor()
            auditor.start_audit()
            
            yield f"data: {json.dumps({'type': 'workflow_started', 'run_id': run_id, 'timestamp': time.time()})}\n\n"
            
            final_state = dict(initial_state)
            
            try:
                async for event in langgraph_app.astream_events(initial_state, version="v2"):
                    event_type = event["event"]
                    name = event["name"]
                    tags = event.get("tags") or []
                    
                    if "graph:step" in str(tags) or name in ["supervisor", "vision", "rag", "coder", "evaluator", "deliverable"]:
                        if event_type == "on_chain_start":
                            yield f"data: {json.dumps({'type': 'agent_started', 'run_id': run_id, 'agent': name, 'timestamp': time.time()})}\n\n"
                            
                        elif event_type == "on_chain_end":
                            output_data = event.get("data", {}).get("output", {})
                            if isinstance(output_data, dict):
                                for k, v in output_data.items():
                                    final_state[k] = v
                                    
                            if name == "supervisor":
                                plan = output_data.get("active_plan", [])
                                yield f"data: {json.dumps({'type': 'plan_created', 'run_id': run_id, 'plan': plan, 'timestamp': time.time()})}\n\n"
                                
                            yield f"data: {json.dumps({'type': 'agent_completed', 'run_id': run_id, 'agent': name, 'output': output_data, 'timestamp': time.time()})}\n\n"
                            
                        elif event_type == "on_chain_error":
                            yield f"data: {json.dumps({'type': 'agent_failed', 'run_id': run_id, 'agent': name, 'error': str(event.get('data', {}).get('error', 'Unknown Error')), 'timestamp': time.time()})}\n\n"

                auditor.stop_audit()
                audit_results = auditor.verify_sovereignty()
                final_state["security"] = audit_results
                
                yield f"data: {json.dumps({'type': 'workflow_completed', 'run_id': run_id, 'final_state': final_state, 'timestamp': time.time()})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'workflow_failed', 'run_id': run_id, 'error': str(e), 'timestamp': time.time()})}\n\n"
        finally:
            try:
                os.chdir(original_cwd)
            except:
                pass

    return StreamingResponse(async_event_generator(), media_type="text/event-stream")

@app.get("/api/download")
def download_deliverable(path: str):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    full_path = os.path.join(project_root, path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path, filename="final_approval_note.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    raise HTTPException(status_code=404, detail="Deliverable not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
