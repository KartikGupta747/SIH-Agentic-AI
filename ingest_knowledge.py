import os
import pickle
import pymupdf4llm
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

def build_hierarchical_hybrid_index(pdf_directory: str, index_dir: str):
    """
    Ingests PDFs incrementally. Existing indices will be loaded and updated 
    without duplication.
    """
    print("Initializing OllamaEmbeddings (nomic-embed-text)...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    headers_to_split_on = [
        ("#", "Header 1"), 
        ("##", "Header 2"), 
        ("###", "Header 3")
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    
    if not os.path.exists(pdf_directory):
        os.makedirs(pdf_directory, exist_ok=True)
        print(f"Created directory {pdf_directory}. Please add PDFs and run again.")
        return
        
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDFs found in {pdf_directory}.")
        return

    faiss_dir = os.path.join(index_dir, "faiss")
    bm25_path = os.path.join(index_dir, "bm25.pkl")
    
    existing_faiss = None
    existing_chunks = []
    processed_files = set()
    
    # 1 & 2. Load existing indices if they exist
    if os.path.exists(faiss_dir) and os.path.exists(bm25_path):
        print("Loading existing index to perform incremental update...")
        existing_faiss = FAISS.load_local(faiss_dir, embeddings, allow_dangerous_deserialization=True)
        # Extract existing documents to rebuild BM25 later
        existing_docs = list(existing_faiss.docstore._dict.values())
        existing_chunks.extend(existing_docs)
        for doc in existing_docs:
            if "source" in doc.metadata:
                processed_files.add(doc.metadata["source"])
                
    new_chunks = []

    for filename in pdf_files:
        # 4. Check to prevent duplication
        if filename in processed_files:
            print(f"Skipping {filename}: Already ingested.")
            continue
            
        filepath = os.path.join(pdf_directory, filename)
        print(f"Processing: {filename}")
        
        # 3. Process new PDFs exactly as before
        md_text = pymupdf4llm.to_markdown(filepath)
        parent_docs = markdown_splitter.split_text(md_text)
        
        for doc in parent_docs:
            breadcrumb = f"{filename}"
            for header_key in ["Header 1", "Header 2", "Header 3"]:
                if header_key in doc.metadata:
                    breadcrumb += f" > {doc.metadata[header_key]}"
            
            enriched_content = f"Context: {breadcrumb}\n\n{doc.page_content}"
            # Add metadata source
            doc.metadata["source"] = filename 
            
            chunks = text_splitter.split_text(enriched_content)
            for chunk in chunks:
                new_chunks.append(Document(page_content=chunk, metadata=doc.metadata.copy()))
                
    if not new_chunks:
        print("No new documents to index.")
        return
        
    os.makedirs(index_dir, exist_ok=True)
    
    # 5. Append and Re-fit
    print("Updating FAISS Vector Store...")
    if existing_faiss:
        existing_faiss.add_documents(new_chunks)
        faiss_store = existing_faiss
    else:
        faiss_store = FAISS.from_documents(new_chunks, embeddings)
        
    faiss_store.save_local(faiss_dir)
    
    print("Updating BM25 Retriever...")
    all_chunks = existing_chunks + new_chunks
    bm25_retriever = BM25Retriever.from_documents(all_chunks)
    with open(bm25_path, "wb") as f:
        pickle.dump(bm25_retriever, f)
        
    print(f"Index built/updated successfully in {index_dir}. Added {len(new_chunks)} new chunks.")

if __name__ == "__main__":
    pdf_dir = "sample_pdfs"
    idx_dir = "index_data"
    build_hierarchical_hybrid_index(pdf_dir, idx_dir)