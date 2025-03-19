# Example integration with question_answer_agent.py

# 1. Run the question-answer agent to get a response
from Question_Response_Agent import QuestionAnswerAgent

qa_agent = QuestionAnswerAgent(
    pdf_path="psychometric_questions.pdf",
    groq_api_key="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",
    huggingface_api_key="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"
)

# Get a single question-answer interaction
qa_result = qa_agent.run_single_interaction()

# 2. Pass the user's response to the sentiment analyzer
from Sentiment_Analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer(
    pdf_path="sentiment_analysis_guidelines.pdf",
    groq_api_key="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",
    huggingface_api_key="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"
)

# Analyze the sentiment of the user's response
sentiment_result = analyzer.analyze_sentiment(
    user_response=qa_result["user_answer"],
    question=qa_result["question"]
)

# 3. Use the sentiment analysis result
print(f"Sentiment Score: {sentiment_result['score']} ({sentiment_result['sentiment_category']})")
print(f"Analysis Context: {sentiment_result['context']}")