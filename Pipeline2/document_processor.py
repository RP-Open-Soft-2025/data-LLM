import os
import PyPDF2
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def read_pdf(self, file_path: str) -> str:
        """Read a PDF file and extract text content."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        text = ""
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        
        return text
    
    def read_txt(self, file_path: str) -> str:
        """Read a TXT file and extract content."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"TXT file not found: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    
    def process_documents(self, pdf_path: str, txt_path: str) -> List[Dict[str, Any]]:
        """Process both PDF and TXT files and prepare them for vectorization."""
        pdf_text = self.read_pdf(pdf_path)
        txt_text = self.read_txt(txt_path)
        
        pdf_chunks = self.text_splitter.split_text(pdf_text)
        txt_chunks = self.text_splitter.split_text(txt_text)
        
        documents = []
        for chunk in pdf_chunks:
            documents.append({
                "content": chunk,
                "source": "behavioral_questions_pdf"
            })
        
        for chunk in txt_chunks:
            documents.append({
                "content": chunk,
                "source": "employee_report_txt"
            })
        
        return documents