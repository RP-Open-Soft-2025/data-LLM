from langchain.prompts import PromptTemplate

# Template for initial question generation using retrieved context
INITIAL_QUESTION_TEMPLATE = """
You are a professional counselor. Your task is to ask meaningful behavioral questions 
based on the following employee information and behavioral questions knowledge.

Employee Information Context:
{employee_context}

Behavioral Questions Context:
{behavioral_context}

Generate a thoughtful, open-ended question that will help understand the employee's behavior 
and thought process better. Make sure the question is specific and relates to the information provided.

IMPORTANT: Your question should be original and creative. Avoid standard or generic questions.
Focus on a specific aspect rather than asking broad questions about multiple topics.

Question:
"""

# Template for subsequent question generation using context
CONTEXTUAL_QUESTION_TEMPLATE = """
You are a professional counselor. Your task is to ask meaningful behavioral questions 
based on the following context.

Employee Information Context:
{employee_context}

Behavioral Questions Context:
{behavioral_context}

Previous Conversation Context:
{conversation_context}

Generate a thoughtful, open-ended follow-up question that builds upon the previous interaction 
and helps understand the employee's behavior and thought process better.

IMPORTANT GUIDELINES:
1. Your question MUST be COMPLETELY DIFFERENT from any previous questions
2. Explore a NEW angle or topic not covered in the conversation so far
3. Make your question specific and focused rather than broad or generic
4. Avoid repeating themes or concepts from previous questions
5. Make the question thought-provoking and insightful

Question:
"""

# Template for generating the final behavioral report
BEHAVIORAL_REPORT_TEMPLATE = """
You are a professional counselor. Your task is to generate a detailed behavioral report based on 
the counseling session that just concluded.

Employee Information Context:
{employee_context}

Behavioral Questions Context:
{behavioral_context}

Conversation Summary:
{conversation_summary}

Based on the questions and answers, generate a comprehensive report that analyzes:
1. The employee's behavioral patterns
2. Emotional responses and mood indicators
3. Strengths and areas for improvement
4. Recommendations for further development

Your report should be detailed, empathetic, and provide actionable insights.

Behavioral Report:
"""

# Create prompt templates
initial_question_prompt = PromptTemplate(
    input_variables=["employee_context", "behavioral_context"],
    template=INITIAL_QUESTION_TEMPLATE
)

contextual_question_prompt = PromptTemplate(
    input_variables=["employee_context", "behavioral_context", "conversation_context"],
    template=CONTEXTUAL_QUESTION_TEMPLATE
)

behavioral_report_prompt = PromptTemplate(
    input_variables=["employee_context", "behavioral_context", "conversation_summary"],
    template=BEHAVIORAL_REPORT_TEMPLATE
)

# Predefined initial questions (as a fallback)
PREDEFINED_INITIAL_QUESTIONS = [
    "Could you describe a challenging situation at work and how you handled it?",
    "Tell me about a time when you had to work with a difficult team member. How did you approach this situation?",
    "What would you consider your greatest professional achievement, and what steps did you take to accomplish it?",
    "Can you share an example of a time when you received constructive criticism? How did you respond to it?",
    "Describe a situation where you had to make a difficult decision with limited information. What was your approach?",
    "Could you tell me about a time when you had to adapt to a significant change at work?",
    "Tell me about a project where you had to collaborate with people from different backgrounds or departments.",
    "Describe a situation where you had to prioritize multiple important tasks. How did you decide what to focus on?",
    "Can you share an experience where you had to persuade others to adopt your idea or approach?",
    "Tell me about a time when you failed to meet a goal or deadline. How did you handle it?",
]