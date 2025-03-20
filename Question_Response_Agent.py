from agno.agent import Agent
from agno.models.groq import Groq
from agno.vectordb.lancedb import LanceDb, SearchType
# from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase
import os

class QuestionAnswerAgent:
    """
    A counseling agent that asks a single psychometric question from a PDF,
    gets the user's answer, processes it, and then stops.
    """
    
    def __init__(
        self,
        pdf_path: str,
        groq_api_key: str,
        model_id: str = "llama-3.3-70b-versatile",
        table_name: str = "psychometric_questions",
        vector_db_path: str = "tmp/lancedb",
        load_knowledge: bool = True,
    ):
        """
        Initialize the QuestionAnswerAgent.
        
        Args:
            pdf_path: Path to the PDF containing psychometric questions
            groq_api_key: API key for Groq
            model_id: Model ID to use for the Groq LLM
            table_name: Name of the table to store embeddings
            vector_db_path: Path to store the vector database
            load_knowledge: Whether to load the knowledge base on initialization
        """
        self.pdf_path = pdf_path
        
        # Initialize the knowledge base with SentenceTransformerEmbedder
        self.knowledge_base = PDFKnowledgeBase(
            path=pdf_path,
            vector_db=LanceDb(
                table_name=table_name,
                uri=vector_db_path,
                search_type=SearchType.vector,
                embedder=SentenceTransformerEmbedder(),  # Changed this line
            ),
        )
        
        # Load the knowledge base if specified
        if load_knowledge:
            self.knowledge_base.load()
        
        # Initialize the agent
        self.agent = Agent(
            model=Groq(id=model_id, api_key=groq_api_key),
            knowledge=self.knowledge_base,
            description="You are a professional counseling agent that asks psychometric questions and analyzes responses.",
            instructions=[
                "Ask one psychometric question from the provided PDF.",
                "Process user responses in a supportive and understanding manner.",
                "Don't judge or criticize the user's answers."
            ],
            add_references=True,
            search_knowledge=True,
            show_tool_calls=False,
            markdown=True,
        )
    
    def run_single_interaction(self, stream=False):
        """
        Run a single question-answer interaction:
        1. Ask a question from the PDF
        2. Get the user's answer
        3. Process the answer
        4. Return the result and stop
        
        Args:
            stream: Whether to stream the response
            
        Returns:
            A dictionary containing the question, user answer, and analysis
        """
        # Step 1: Generate a question from the PDF
        prompt = "Based on the psychometric questions in the PDF, ask the user a relevant question."
        question_response = self.agent.run(prompt, stream=stream)
        question = question_response.content
        
        # Print the question to the user
        print(f"\nQuestion: {question}\n")
        
        # Step 2: Get the user's answer
        user_answer = input("Your answer: ")
    
        
        # Return the results
        return {
            "question": question,
            "user_answer": user_answer
        }


# Example usage
if __name__ == "__main__":
    # Initialize the agent with your API keys
    grok_key = os.environ.get("GROQ_API_KEY", "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")
    
    # Create the agent
    qa_agent = QuestionAnswerAgent(
        pdf_path="Questions.pdf",
        groq_api_key=grok_key,
        load_knowledge=True  # Set to False after the first run
    )
    
    # Run a single interaction (ask question, get answer, analyze, then stop)
    result = qa_agent.run_single_interaction()
    
    # The program will exit after this single interaction is complete