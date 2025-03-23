from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.huggingface import HuggingFace
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
grok_key='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'


# Create a knowledge base of PDFs from URLs
knowledge_base = PDFKnowledgeBase(
    path='PREFERENCE ADAPTATION OF LLMS.pdf',
    # Use LanceDB as the vector database and store embeddings in the `recipes` table
    vector_db=LanceDb(
        table_name="recipes",
        uri="tmp/lancedb",
        search_type=SearchType.vector,
        embedder=HuggingfaceCustomEmbedder(api_key='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'),
    ),
)
# Load the knowledge base: Comment after first run as the knowledge base is already loaded
knowledge_base.load()

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile",api_key=grok_key),
    knowledge=knowledge_base,
    # Enable RAG by adding references from AgentKnowledge to the user prompt.
    add_references=True,
    # Set as False because Agents default to `search_knowledge=True`
    search_knowledge=False,
    show_tool_calls=True,
    markdown=True,
)
agent.print_response(
    "explain the FOLLOW-THE-REGULARIZED-LEADER ALGORITHM from the AMULET paper", stream=True
)