from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
import random

class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the vector store with HuggingFace embeddings."""
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB
        self.db = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        
        # Keep track of previously retrieved chunks to avoid repetition
        self.recently_used_chunks = set()
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store."""
        texts = [doc["content"] for doc in documents]
        metadatas = [{"source": doc["source"]} for doc in documents]
        
        self.db.add_texts(texts=texts, metadatas=metadatas)
    
    def search(self, query: str, k: int = 3, source_filter: str = None) -> List[Dict[str, Any]]:
        """Search the vector store for documents relevant to the query."""
        # If a specific source filter is requested, apply it
        filter_dict = {"source": source_filter} if source_filter else None
        
        # Retrieve more results than needed to allow for filtering
        extra_k = min(k * 2, 10)  # Get more results but cap at 10
        
        # Perform the search
        results = self.db.similarity_search_with_score(
            query, 
            k=extra_k,
            filter=filter_dict
        )
        
        docs = []
        for doc, score in results:
            content_hash = hash(doc.page_content)
            docs.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "relevance": score,
                "content_hash": content_hash
            })
        
        # Filter out recently used chunks if possible
        filtered_docs = [doc for doc in docs if doc["content_hash"] not in self.recently_used_chunks]
        
        # If filtering removed too many, just use the original results
        if len(filtered_docs) < k:
            filtered_docs = docs
        
        # Take only the requested number of results
        result_docs = filtered_docs[:k]
        
        # Update the recently used chunks
        for doc in result_docs:
            self.recently_used_chunks.add(doc["content_hash"])
            
        # If we're tracking too many, remove the oldest ones
        if len(self.recently_used_chunks) > 50:
            self.recently_used_chunks = set(list(self.recently_used_chunks)[-50:])
            
        # Remove content_hash before returning
        return [{k: v for k, v in doc.items() if k != "content_hash"} for doc in result_docs]
    
    def get_employee_context(self, query: str = "employee background skills experience", k: int = 2) -> str:
        """Get relevant employee context from the vector store."""
        # Add some randomness to the query to ensure diversity
        diversifiers = ["background", "skills", "experience", "strengths", "challenges", "goals", "personality"]
        random_diversifier = random.choice(diversifiers)
        diverse_query = f"{query} {random_diversifier}"
        
        results = self.search(diverse_query, k=k, source_filter="employee_report_txt")
        
        # Combine the results into a context string
        context = ""
        for doc in results:
            context += doc["content"] + "\n\n"
            
        return context.strip()
    
    def get_behavioral_context(self, query: str = "behavioral interview questions evaluation", k: int = 2) -> str:
        """Get relevant behavioral questions context from the vector store."""
        # Add some randomness to the query to ensure diversity
        diversifiers = ["assessment", "evaluation", "interview", "behavior", "skills", "competency", "traits"]
        random_diversifier = random.choice(diversifiers)
        diverse_query = f"{query} {random_diversifier}"
        
        results = self.search(diverse_query, k=k, source_filter="behavioral_questions_pdf")
        
        # Combine the results into a context string
        context = ""
        for doc in results:
            context += doc["content"] + "\n\n"
            
        return context.strip()
    
    def get_relevant_context(self, query: str, k: int = 3) -> Dict[str, str]:
        """Get relevant context from both sources based on the query."""
        # Search employee information
        employee_results = self.search(query, k=k//2, source_filter="employee_report_txt")
        
        # Search behavioral questions
        behavioral_results = self.search(query, k=k//2, source_filter="behavioral_questions_pdf")
        
        # Combine results
        employee_context = "\n\n".join([doc["content"] for doc in employee_results])
        behavioral_context = "\n\n".join([doc["content"] for doc in behavioral_results])
        
        return {
            "employee_context": employee_context,
            "behavioral_context": behavioral_context
        }