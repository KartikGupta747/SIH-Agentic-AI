import os
import pickle
import numpy as np
from typing import List
from pydantic import BaseModel, Field
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from graph_state import WorkbenchState
from sentence_transformers import CrossEncoder

class SearchPlan(BaseModel):
    queries: List[str] = Field(description="A list of 3 targeted search queries.")

def generate_search_queries(state: WorkbenchState) -> list[str]:
    """Generates targeted search queries based on user intent and vision context."""
    # keep_alive=0 is critical for 6GB VRAM constraint (flush immediately)
    llm = ChatOllama(model="qwen2.5:3b", temperature=0.0, keep_alive=0)
    structured_llm = llm.with_structured_output(SearchPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert engineering assistant. Generate exactly 3 targeted search queries to find the most relevant information in the technical manuals. Consider both the user query and any extracted vision data (e.g., tables or formulas)."),
        ("human", "User Query: {user_query}\nExtracted Vision Data: {vision_data}")
    ])
    
    chain = prompt | structured_llm
    vision_data = state.get("extracted_vision_data") or "None"
    
    plan: SearchPlan = chain.invoke({
        "user_query": state.get("user_query", ""),
        "vision_data": vision_data
    })
    
    return plan.queries

def rag_node(state: WorkbenchState) -> dict:
    """
    RAG Node: Executes Ensemble Retrieval (BM25 + FAISS) fetching broad context,
    then applies a Two-Stage Cross-Encoder Re-ranker (forced on CPU) for high precision.
    """
    active_plan = state.get("active_plan", [])
    if "rag" not in active_plan:
        return {} 
        
    index_dir = "index_data" 
    faiss_dir = os.path.join(index_dir, "faiss")
    bm25_path = os.path.join(index_dir, "bm25.pkl")
    
    if not os.path.exists(faiss_dir) or not os.path.exists(bm25_path):
        return {"retrieved_documents": "Error: Knowledge index not found. Please run ingest_knowledge.py first."}
        
    # Load Retrievers
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    faiss_store = FAISS.load_local(faiss_dir, embeddings, allow_dangerous_deserialization=True)
    # 2. Retrieve broadly: fetch up to 15 chunks
    faiss_retriever = faiss_store.as_retriever(search_kwargs={"k": 25})
    
    with open(bm25_path, "rb") as f:
        bm25_retriever = pickle.load(f)
    bm25_retriever.k = 25 # Fetch up to 15 chunks from BM25
        
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],
        weights=[0.5, 0.5]
    )
    
    queries = generate_search_queries(state)
    print(f"Executing RAG with queries: {queries}")
    
    # 3. Combine and Deduplicate
    unique_docs = {}
    for query in queries:
        docs = ensemble_retriever.invoke(query)
        for doc in docs:
            if doc.page_content not in unique_docs:
                unique_docs[doc.page_content] = doc
                
    if not unique_docs:
        return {"retrieved_documents": "No relevant documents found."}
        
    deduped_docs = list(unique_docs.values())
    
    # 4. Initialize Cross-Encoder on CPU ONLY to protect VRAM
    print(f"Re-ranking {len(deduped_docs)} chunks via Cross-Encoder (CPU)...")
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device='cpu')
    
    # 5. Create scoring pairs
    user_query_str = state.get("user_query", "")
    vision_data_str = state.get("extracted_vision_data", "")
    # Combine intent with extracted facts (like vessel tags) so the reranker knows what to look for
    combined_rerank_context = f"{user_query_str}\nVision Context: {vision_data_str}"
    
    scoring_pairs = [[combined_rerank_context, doc.page_content] for doc in deduped_docs]
    
    # 6. Score the documents
    scores = reranker.predict(scoring_pairs)
    
    # 7. Zip, sort in descending order, and select top 5
    doc_score_pairs = list(zip(deduped_docs, scores))
    doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
    top_k_docs = [pair[0] for pair in doc_score_pairs[:10]]
    
    # 8. Compile the final string
    compiled_string = "\n\n======================\n\n".join(
        [doc.page_content for doc in top_k_docs]
    )
    
    return {"retrieved_documents": compiled_string}

if __name__ == "__main__":
    # Test Harness
    mock_state: WorkbenchState = {
        "user_query": "What is the acceptable tolerance for Section 7 pipeline welds?",
        "image_path": "",
        "active_plan": ["rag"],
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
    
    print("Testing Two-Stage RAG Node...")
    result = rag_node(mock_state)
    print("\n--- Retrieved Documents ---")
    doc_text = result.get("retrieved_documents", "")
    if "Error" in doc_text:
        print(doc_text)
    else:
        print(doc_text[:1000] + "\n...[truncated]")