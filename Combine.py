# Example integration with question_answer_agent.py

# 1. Run the question-answer agent to get a response
from Question_Response_Agent import QuestionAnswerAgent

qa_agent = QuestionAnswerAgent(
    pdf_path="Questions.pdf",
    groq_api_key="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",
)

# Get a single question-answer interaction
qa_result = qa_agent.run_single_interaction()

# 2. Pass the user's response to the sentiment analyzer
from Sentiment_Analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer(
    pdf_path="Sentiment.pdf",
    groq_api_key="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",
)

# Analyze the sentiment of the user's response
sentiment_result = analyzer.analyze_sentiment(
    user_response=qa_result["user_answer"],
    question=qa_result["question"]
)

# 3. Use the sentiment analysis result
print(f"Sentiment Score: {sentiment_result['score']} ({sentiment_result['sentiment_category']})")
print(f"Analysis Context: {sentiment_result['context']}")