from agno.knowledge.text import TextKnowledgeBase
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.document.chunking.agentic import AgenticChunking
import os

class KnowledgeBaseManager:
    def __init__(self, employee_data_path, questions_pdf_path, db_uri="tmp/counselling_db"):
        """
        Initialize the knowledge bases for employee data and counseling questions.
        
        Args:
            employee_data_path: Path to the employee.txt file containing employee data
            questions_pdf_path: Path to the Questions.pdf containing question templates
            db_uri: Path to store the vector database
        """
        # Using SentenceTransformerEmbedder which doesn't need an API key or model specification
        self.embedder = SentenceTransformerEmbedder()
        
        # Create knowledge base for employee data
        self.employee_kb = TextKnowledgeBase(
            path=employee_data_path,
            chunking_strategy=AgenticChunking(),
            vector_db=LanceDb(
                table_name="employee_data",
                uri=db_uri,
                search_type=SearchType.vector,
                embedder=self.embedder
            )
        )
        
        # Create knowledge base for questions
        self.questions_kb = PDFKnowledgeBase(
            chunking_strategy=AgenticChunking(),
            path=questions_pdf_path,
            vector_db=LanceDb(
                table_name="question_templates",
                uri=db_uri,
                search_type=SearchType.vector,
                embedder=self.embedder
            )
        )
        
        # Flag to track if knowledge bases are loaded
        self.employee_kb_loaded = os.path.exists(os.path.join(db_uri, "employee_data"))
        self.questions_kb_loaded = os.path.exists(os.path.join(db_uri, "question_templates"))
    
    def load_knowledge_bases(self, force_reload=False):
        """
        Load both knowledge bases if they haven't been loaded yet or if force_reload is True
        
        Args:
            force_reload: If True, reload the knowledge bases even if they exist
        """
        if not self.employee_kb_loaded or force_reload:
            print("Loading employee data knowledge base...")
            self.employee_kb.load()
            self.employee_kb_loaded = True
        else:
            print("Employee data knowledge base already loaded.")
        
        if not self.questions_kb_loaded or force_reload:
            print("Loading question templates knowledge base...")
            self.questions_kb.load()
            self.questions_kb_loaded = True
        else:
            print("Question templates knowledge base already loaded.")
        
        print("Knowledge bases ready for use.")
    
    def retrieve_from_employee_data(self, query, num_documents=2):
        """
        Retrieve relevant chunks from employee data
        
        Args:
            query: The query to search for
            num_documents: Maximum number of documents to retrieve
            
        Returns:
            Retrieved content as a string
        """
        docs = self.employee_kb.search(query=query, num_documents=num_documents)
        return "\n\n".join([doc.content for doc in docs]) if docs else ""
    
    def retrieve_from_questions(self, query, num_documents=2):
        """
        Retrieve relevant chunks from questions
        
        Args:
            query: The query to search for
            num_documents: Maximum number of documents to retrieve
            
        Returns:
            Retrieved content as a string
        """
        docs = self.questions_kb.search(query=query, num_documents=num_documents)
        return "\n\n".join([doc.content for doc in docs]) if docs else ""