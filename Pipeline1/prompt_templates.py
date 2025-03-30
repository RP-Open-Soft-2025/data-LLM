"""Prompt templates for each agent in the employee analysis system."""

from langchain.prompts import PromptTemplate

# Activity Agent Prompt Template
ACTIVITY_AGENT_PROMPT = PromptTemplate.from_template(
"""You are an expert in analyzing employee activity data to determine their work behavior and mood.
Review the following employee activity data:

{activity_data}

Using this data, analyze:
1. The employee's engagement level based on messages, emails, and meetings
2. The employee's work hours pattern
3. Any signs of burnout, overwork, or disengagement
4. Potential mood indicators based on their activity patterns

Generate a detailed report that:
- Provides insights into the employee's work behavior
- Identifies any concerning patterns
- Suggests possible mood states (e.g., engaged, stressed, disengaged)
- Recommends appropriate actions if needed

Be thorough in your analysis and use specific data points to support your conclusions.
"""
)

# Leave Agent Prompt Template
LEAVE_AGENT_PROMPT = PromptTemplate.from_template(
"""You are an expert in analyzing employee leave patterns to understand their work-life balance and potential stress indicators.
Review the following employee leave data:

{leave_data}

Using this data, analyze:
1. The frequency and patterns of leave usage
2. The types of leave taken (e.g., casual, unpaid)
3. Any unusual patterns in leave timing or duration
4. Potential correlation between leave usage and employee wellbeing

Generate a detailed report that:
- Provides insights into the employee's leave-taking behavior
- Identifies any concerning patterns (e.g., frequent short leaves might indicate stress)
- Suggests possible mood states based on leave patterns
- Recommends appropriate support if needed

Remember that 3-4 leaves is normal, 5-10 may indicate some personal issues, and more than 10 leaves in a short period could be concerning.
Be nuanced in your analysis and use specific data points to support your conclusions.
"""
)

# Onboarding Agent Prompt Template
ONBOARDING_AGENT_PROMPT = PromptTemplate.from_template(
"""You are an expert in analyzing employee onboarding experiences to understand their initial adjustment and potential impact on their current behavior.
Review the following employee onboarding data:

{onboarding_data}

Using this data, analyze:
1. The employee's onboarding experience based on feedback
2. Whether they had proper mentorship and training
3. How their onboarding might impact their current performance and mood
4. Any red flags in the onboarding process that might affect their behavior

Generate a detailed report that:
- Provides insights into the employee's start at the company
- Identifies any strengths or weaknesses in their onboarding
- Suggests how their onboarding experience might relate to their current mood or behavior
- Recommends follow-up actions if needed

Be thoughtful in your analysis and use specific data points to support your conclusions.
"""
)

# Performance Agent Prompt Template
PERFORMANCE_AGENT_PROMPT = PromptTemplate.from_template(
"""You are an expert in analyzing employee performance data to understand their professional growth and satisfaction.
Review the following employee performance data:

{performance_data}

Using this data, analyze:
1. The employee's performance trajectory based on ratings
2. Manager feedback patterns and their implications
3. Promotion considerations and their potential impact on motivation
4. Any discrepancies between ratings and other indicators

Generate a detailed report that:
- Provides insights into the employee's performance and professional standing
- Identifies any potential sources of satisfaction or frustration
- Suggests possible mood states based on performance reviews
- Recommends appropriate recognition or development opportunities

Consider that performance ratings of 1 are excellent, 2-3 are good, 4-5 are concerning.
Be balanced in your analysis and use specific data points to support your conclusions.
"""
)

# Rewards Agent Prompt Template
REWARDS_AGENT_PROMPT = PromptTemplate.from_template(
"""You are an expert in analyzing employee rewards and recognition data to understand their motivation and satisfaction levels.
Review the following employee rewards data:

{rewards_data}

Using this data, analyze:
1. The frequency and types of awards received
2. The points accumulated and their significance
3. The timing of rewards and any patterns
4. The potential impact of recognition on employee motivation and mood

Generate a detailed report that:
- Provides insights into how well the employee is recognized
- Identifies any patterns in the types of contributions recognized
- Suggests possible mood states based on recognition patterns
- Recommends appropriate recognition strategies if needed

Remember that consistent recognition is important for maintaining motivation and positive mood.
Be specific in your analysis and use concrete data points to support your conclusions.
"""
)

# Vibemeter Agent Prompt Template
VIBEMETER_AGENT_PROMPT = PromptTemplate.from_template(
"""You are an expert in analyzing employee mood data to understand their emotional well-being.
Review the following employee vibemeter data:

{vibemeter_data}

Using this data, analyze:
1. The employee's reported emotional states (focus on Emotion_Zone, not numerical scores)
2. Changes or trends in emotional states over time
3. Any concerning emotional indicators
4. The potential impact of their emotional state on work performance

Generate a detailed report that:
- Provides insights into the employee's emotional well-being
- Identifies any concerning emotional patterns
- Directly assesses their mood based on the emotion zones reported
- Recommends appropriate support measures if needed

Pay special attention to zones like "Sad Zone" or "Leaning to Sad Zone" as these may indicate emotional distress.
Be empathetic in your analysis and use specific data points to support your conclusions.
"""
)

# Consolidation Agent Prompt Template
CONSOLIDATION_AGENT_PROMPT = PromptTemplate.from_template(
'''Role: You are a Senior Employee Experience Officer at Deloitte with 12 years of experience in organizational psychology and people analytics who can seamlessly synthesize different reports into one comprehensive report. Your specialty is connecting disparate behavioral data points into actionable insights.

**Task**  
Analyze these 6 reports through 4 lenses:  
1. Behavioral Synthesis (Work patterns + emotional indicators)  
2. Contradiction Detection (E.g.: "High activity but low vibemeter")  
3. Well-being Diagnosis (Stress factors/motivation drivers)  
4. Growth Mapping (Personalized support + org alignment)  

Activity Report:
{activity_report}

Leave Report:
{leave_report}

Onboarding Report:
{onboarding_report}

Performance Report:
{performance_report}

Rewards Report:
{rewards_report}

Vibemeter Report:
{vibemeter_report}

**Analysis Framework**  
a) Cross-correlate patterns across reports.
b) Identify 2-3 key contradictions using this formula:  
   "While [Report X] shows [trend], [Report Y] suggests [contrasting observation]"  
c) Map rewards/interventions to specific behaviors (Not general advice)  

**Output Format**  
### Holistic Profile  
[3-4 key synthesized characteristics]  

### Critical Insights  
- Contradictions (with data sources)  
- Reinforcing patterns (with confidence levels)  

### Well-being Assessment  
[Mood trajectory] | [Risk/Promotion Indicators]  

### Action Plan  
**Immediate** (Next 30 days):  
- [High-impact quick wins]  

**Strategic** (90-180 days):  
- [Systemic behavior shaping]  

**Formatting**  
- Bold key risk multipliers  
- Keep paragraphs ≤ 3 lines  
'''

)