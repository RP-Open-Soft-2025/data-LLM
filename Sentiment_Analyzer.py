from agno.agent import Agent
from agno.models.groq import Groq
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase
import os
import json
from typing import Dict, Any, Optional, Tuple, Union, List

class SentimentAnalyzer:
    """
    A sentiment analyzer that evaluates the emotional tone of user responses,
    providing a sentiment score and contextual analysis based on guidelines from a PDF.
    """
    
    def __init__(
        self,
        pdf_path: str,
        groq_api_key: str,
        huggingface_api_key: str,
        model_id: str = "llama-3.3-70b-versatile",
        table_name: str = "sentiment_guidelines",
        vector_db_path: str = "tmp/lancedb",
        load_knowledge: bool = True,
        sentiment_scale: Tuple[int, int] = (-5, 5)
    ):
        """
        Initialize the SentimentAnalyzer.
        
        Args:
            pdf_path: Path to the PDF containing sentiment analysis guidelines
            groq_api_key: API key for Groq
            huggingface_api_key: API key for Huggingface
            model_id: Model ID to use for the Groq LLM
            table_name: Name of the table to store embeddings
            vector_db_path: Path to store the vector database
            load_knowledge: Whether to load the knowledge base on initialization
            sentiment_scale: Tuple representing the min and max possible sentiment scores
                             (e.g., (-5, 5) where -5 is very negative, 0 is neutral, 5 is very positive)
        """
        self.pdf_path = pdf_path
        self.sentiment_scale = sentiment_scale
        
        # Initialize the knowledge base
        self.knowledge_base = PDFKnowledgeBase(
            path=pdf_path,
            vector_db=LanceDb(
                table_name=table_name,
                uri=vector_db_path,
                search_type=SearchType.vector,
                embedder=HuggingfaceCustomEmbedder(api_key=huggingface_api_key),
            ),
        )
        
        # Load the knowledge base if specified
        if load_knowledge:
            self.knowledge_base.load()
        
        # Initialize the agent
        self.agent = Agent(
            model=Groq(id=model_id, api_key=groq_api_key),
            knowledge=self.knowledge_base,
            description="You are a sentiment analysis expert specializing in evaluating emotional content in psychological responses.",
            instructions=[
                f"Analyze user responses to determine their emotional tone and sentiment on a scale from {sentiment_scale[0]} to {sentiment_scale[1]}.",
                f"A score of {sentiment_scale[0]} represents extremely negative sentiment.",
                "A score of 0 represents neutral sentiment.",
                f"A score of {sentiment_scale[1]} represents extremely positive sentiment.",
                "Provide detailed context explaining the sentiment analysis.",
                "Identify emotional keywords, tone indicators, and sentiment patterns.",
                "Follow the specific guidelines from the provided PDF for sentiment analysis.",
                "Always return a valid JSON object with 'score' and 'context' fields."
            ],
            add_references=True,
            search_knowledge=True,
            show_tool_calls=False,
            markdown=True,
        )
    
    def analyze_sentiment(
        self, 
        user_response: str, 
        question: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze the sentiment of a user's response.
        
        Args:
            user_response: The user's response to analyze
            question: The question that prompted the user's response (optional)
            stream: Whether to stream the response
            
        Returns:
            A dictionary containing the sentiment score and contextual analysis
        """
        # Build the analysis prompt
        prompt = "ANALYZE SENTIMENT OF THE FOLLOWING USER RESPONSE:\n\n"
        
        if question:
            prompt += f"QUESTION: \"{question}\"\n\n"
            
        prompt += f"USER RESPONSE: \"{user_response}\"\n\n"
        
        # Add instructions for sentiment analysis
        prompt += f"""
        Based on the sentiment analysis guidelines in the provided PDF, please analyze the emotional tone of this response.
        
        Return your analysis as a JSON object with the following structure:
        
        {{
            "score": (numeric value between {self.sentiment_scale[0]} and {self.sentiment_scale[1]}),
            "sentiment_category": (one of: "very negative", "negative", "slightly negative", "neutral", "slightly positive", "positive", "very positive"),
            "context": "Detailed explanation of the sentiment analysis...",
            "emotional_keywords": ["keyword1", "keyword2", ...],
            "tone_indicators": ["indicator1", "indicator2", ...],
            "emotional_patterns": ["pattern1", "pattern2", ...]
        }}
        
        Remember: 
        - A score of {self.sentiment_scale[0]} represents extremely negative sentiment
        - A score of 0 represents neutral sentiment
        - A score of {self.sentiment_scale[1]} represents extremely positive sentiment
        - The context should explain WHY you assigned this score, referring to specific elements in the response
        """
        
        # Get the analysis from the agent
        response = self.agent.run(prompt, stream=stream)
        
        # Extract the JSON result from the response
        try:
            # Try to parse the entire response as JSON
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*({\s*"score".*})\s*```', response.content, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    # If extraction from code blocks fails, return a fallback result
                    result = {
                        "score": 0,
                        "sentiment_category": "neutral",
                        "context": "Failed to parse sentiment analysis result. Please check the model output format.",
                        "raw_response": response.content,
                        "error": "JSON parsing failed"
                    }
            else:
                # If no JSON or code block found, return the fallback result
                result = {
                    "score": 0,
                    "sentiment_category": "neutral",
                    "context": "Failed to parse sentiment analysis result. Please check the model output format.",
                    "raw_response": response.content,
                    "error": "No JSON found in response"
                }
        
        # Ensure required fields exist
        if "score" not in result:
            result["score"] = 0
            result["error"] = "Score field missing in response"
        
        if "context" not in result:
            result["context"] = "No context provided for sentiment analysis."
            result["error"] = "Context field missing in response"
            
        if "sentiment_category" not in result:
            # Derive category from score
            score = result["score"]
            if score <= self.sentiment_scale[0] * 0.66:
                category = "very negative"
            elif score <= self.sentiment_scale[0] * 0.33:
                category = "negative"
            elif score < 0:
                category = "slightly negative"
            elif score == 0:
                category = "neutral"
            elif score <= self.sentiment_scale[1] * 0.33:
                category = "slightly positive"
            elif score <= self.sentiment_scale[1] * 0.66:
                category = "positive"
            else:
                category = "very positive"
            
            result["sentiment_category"] = category
        
        # Validate score is within range
        if not isinstance(result["score"], (int, float)) or result["score"] < self.sentiment_scale[0] or result["score"] > self.sentiment_scale[1]:
            result["original_score"] = result["score"]
            result["score"] = max(min(float(result["score"]), self.sentiment_scale[1]), self.sentiment_scale[0]) if isinstance(result["score"], (int, float)) else 0
            result["warning"] = f"Score was adjusted to be within range {self.sentiment_scale[0]}-{self.sentiment_scale[1]}"
        
        # Add original user response and question to the result
        result["user_response"] = user_response
        if question:
            result["question"] = question
        
        return result
    
    def get_sentiment_category(self, score: float) -> str:
        """
        Convert a numeric sentiment score to a categorical label.
        
        Args:
            score: Numeric sentiment score
            
        Returns:
            String category label
        """
        min_score, max_score = self.sentiment_scale
        
        if score <= min_score * 0.66:
            return "very negative"
        elif score <= min_score * 0.33:
            return "negative"
        elif score < 0:
            return "slightly negative"
        elif score == 0:
            return "neutral"
        elif score <= max_score * 0.33:
            return "slightly positive"
        elif score <= max_score * 0.66:
            return "positive"
        else:
            return "very positive"
    
    def color_code_sentiment(self, score: float) -> str:
        """
        Get a color code for displaying sentiment (useful for UI integration).
        
        Args:
            score: Numeric sentiment score
            
        Returns:
            Hex color code
        """
        min_score, max_score = self.sentiment_scale
        
        if score < 0:
            # Red gradient for negative scores
            intensity = min(255, int(255 * (abs(score) / abs(min_score))))
            return f"#{intensity:02x}0000"
        elif score > 0:
            # Green gradient for positive scores
            intensity = min(255, int(255 * (score / max_score)))
            return f"#00{intensity:02x}00"
        else:
            # Gray for neutral
            return "#808080"


# Example usage
if __name__ == "__main__":
    # Initialize the analyzer with your API keys
    grok_key = os.environ.get("GROQ_API_KEY", "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")
    huggingface_key = os.environ.get("HF_API_KEY", "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")
    
    # Create the sentiment analyzer
    analyzer = SentimentAnalyzer(
        pdf_path="Sentiment.pdf",  # PDF with sentiment guidelines
        groq_api_key=grok_key,
        huggingface_api_key=huggingface_key,
        load_knowledge=True,  # Set to False after the first run
        sentiment_scale=(-5, 5)  # Use a -5 to 5 scoring scale
    )
    
    # Example of analyzing a response from question_answer_agent.py
    question = "How do you feel about your current work-life balance?"
    user_response = "It's been really challenging lately. I feel overwhelmed most days and don't have time for myself anymore."
    
    # Get sentiment analysis
    sentiment_result = analyzer.analyze_sentiment(user_response, question)
    
    # Print the results
    print(f"Sentiment Score: {sentiment_result['score']} ({sentiment_result['sentiment_category']})")
    print(f"Context: {sentiment_result['context']}")
    
    if 'emotional_keywords' in sentiment_result:
        print(f"Emotional Keywords: {', '.join(sentiment_result['emotional_keywords'])}")
    
    if 'tone_indicators' in sentiment_result:
        print(f"Tone Indicators: {', '.join(sentiment_result['tone_indicators'])}")