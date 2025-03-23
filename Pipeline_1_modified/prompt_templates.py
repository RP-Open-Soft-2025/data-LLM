"""Prompt templates for each agent in the employee analysis system."""

from langchain.prompts import PromptTemplate

# Activity Agent Prompt Template
AGENT_1 = PromptTemplate.from_template(
'''You are an expert in analyzing employee performance and career progression trends to detect potential frustration and disengagement.  
Review the following employee data:  

{employee_performance_data}  

Using this data, analyze:  
1. The employee’s overall performance trends based on historical ratings and manager feedback.  
2. Whether the employee has been considered for promotion and the potential reasons why not.  
3. Any correlations between performance ratings, feedback, and other work-related factors (e.g., workload, mentorship, rewards).  
4. Possible signs of disengagement or frustration due to lack of career progression.  

Generate a detailed report that:  
- Assesses whether the employee is stagnating in their role.  
- Identifies patterns indicating frustration or dissatisfaction.  
- Provides insights into whether the lack of promotion is justified or a sign of organizational oversight.  
- Recommends possible interventions to improve engagement and career satisfaction.  

Use specific data points to support your conclusions and ensure a balanced evaluation.  
'''
)
AGENT_2=PromptTemplate.from_template(
    '''You are an expert in evaluating employee productivity and engagement to identify recognition gaps.  
Review the following employee activity data:  

{employee_activity_data}  

Using this data, analyze:  
1. The employee’s workload in terms of hours, emails, messages, and meetings.  
2. Whether the employee is maintaining consistently high activity levels.  
3. Whether the employee has received any form of recognition (awards, promotions, rewards).  
4. Potential signs of burnout or disengagement due to a lack of recognition.  

Generate a detailed report that:  
- Assesses the employee’s workload and contributions.  
- Identifies whether the employee is being overlooked for recognition.  
- Highlights potential risks of dissatisfaction and disengagement.  
- Suggests actions to ensure recognition and retention.  

Use specific data points to support your insights.  
'''
)
AGENT_3=PromptTemplate.from_template(
    '''You are an expert in evaluating employee onboarding experiences to detect potential gaps in support.  
Review the following employee onboarding data:  

{employee_onboarding_data}  

Using this data, analyze:  
1. The quality of the employee’s onboarding experience based on feedback scores.  
2. Whether the employee was assigned a mentor for guidance.  
3. Any early performance challenges or disengagement signs due to poor onboarding.  
4. Potential risks of slow adaptation, frustration, or turnover.  

Generate a detailed report that:  
- Assesses the effectiveness of the employee’s onboarding.  
- Identifies gaps in mentorship and training support.  
- Highlights risks of long-term disengagement.  
- Suggests possible interventions for better onboarding experiences.  

Use specific data points to support your findings.  
'''
)
AGENT_4=PromptTemplate.from_template(
    '''You are an expert in analyzing employee health-related trends and their impact on performance.  
Review the following employee leave and performance data:  

{employee_leave_performance_data}  

Using this data, analyze:  
1. The frequency and pattern of sick leave taken.  
2. The employee’s performance trends over time.  
3. Any correlation between health-related absences and declining productivity.  
4. Possible signs of health-related burnout or stress.  

Generate a detailed report that:  
- Assesses whether frequent leave is affecting work performance.  
- Identifies patterns of potential long-term health concerns.  
- Highlights risks of disengagement or work stress due to declining health.  
- Recommends actions such as workload adjustments or well-being initiatives.  

Use specific data points to strengthen your conclusions.  
'''
)   
AGENT_5=PromptTemplate.from_template(
    '''You are an expert in identifying employee well-being concerns based on leave patterns and mood indicators.  
Review the following employee leave and sentiment data:  

{employee_leave_vibe_data}  

Using this data, analyze:  
1. The frequency and nature of unpaid leaves taken.  
2. The employee’s historical vibe scores and mood trends.  
3. Any correlation between financial strain (unpaid leave) and declining morale.  
4. Possible signs of dissatisfaction, stress, or disengagement.  

Generate a detailed report that:  
- Assesses whether unpaid leave is affecting the employee’s morale.  
- Identifies patterns of emotional distress or financial hardship.  
- Highlights risks of turnover or mental health challenges.  
- Recommends actions to support the employee’s well-being.  

Use specific data points to provide concrete insights.  
'''
)   
AGENT_6=PromptTemplate.from_template(
    '''You are an expert in career progression analysis, identifying employees at risk of stagnation.  
Review the following employee performance and promotion history data:  

{employee_performance_promotion_data}  

Using this data, analyze:  
1. The employee’s performance trends over time.  
2. Whether the employee has been considered for promotion despite strong performance.  
3. Any gaps in career growth opportunities.  
4. Potential risks of frustration and disengagement due to stagnation.  

Generate a detailed report that:  
- Assesses the fairness of promotion decisions.  
- Identifies if the employee is being overlooked.  
- Highlights potential risks of talent loss.  
- Suggests career development interventions.  

Use data-driven insights to support your conclusions.  
'''
)
AGENT_7=PromptTemplate.from_template(
    '''You are an expert in assessing employee recognition gaps.  
Review the following employee performance and rewards data:  

{employee_performance_rewards_data}  

Using this data, analyze:  
1. The employee’s performance history and consistency.  
2. Whether the employee has received any rewards despite high performance.  
3. The potential impact of unrecognized contributions on engagement.  
4. Any signs of dissatisfaction or declining motivation.  

Generate a detailed report that:  
- Evaluates the employee’s reward history.  
- Identifies whether the lack of recognition is a concern.  
- Highlights risks of disengagement or attrition.  
- Recommends strategies for proper recognition.  

Use specific data points to strengthen your findings.  
'''
)   
AGENT_8=PromptTemplate.from_template(
    '''You are an expert in assessing support gaps for low-performing employees.  
Review the following employee performance and mentorship data:  

{employee_performance_mentorship_data}  

Using this data, analyze:  
1. The employee’s performance ratings over time.  
2. Whether the employee was assigned a mentor for guidance.  
3. Potential struggles due to lack of support.  
4. Possible signs of frustration or stagnation.  

Generate a detailed report that:  
- Evaluates whether the employee is struggling due to lack of guidance.  
- Identifies risks of continued poor performance.  
- Highlights possible intervention strategies.  
- Suggests mentorship or training programs for improvement.  

Use specific data points to justify your findings.  
''')
AGENT_9=PromptTemplate.from_template(
    '''You are an expert in analyzing employee performance trends and manager feedback discrepancies.  
Review the following employee performance and feedback data:  

{employee_performance_feedback_data}  

Using this data, analyze:  
1. The employee’s performance ratings over time.  
2. Whether there is a mismatch between performance and manager feedback.  
3. Possible reasons for inconsistent feedback.  
4. Potential risks of confusion, frustration, or disengagement.  

Generate a detailed report that:  
- Evaluates the fairness of manager feedback.  
- Identifies if the employee is being unfairly evaluated.  
- Highlights risks of dissatisfaction due to unclear expectations.  
- Suggests possible actions to address the issue.  

Use specific data points to support your conclusions.  
'''
)
AGENT_10=PromptTemplate.from_template(
    '''You are an expert in detecting performance trends and employee motivation factors.  
Review the following employee performance and rewards data:  

{employee_low_performance_rewards_data}  

Using this data, analyze:  
1. The employee’s performance trajectory over time.  
2. Whether the employee has received recognition despite fluctuations in performance.  
3. Any patterns suggesting demotivation due to lack of rewards.  
4. Risks of continued performance decline.  

Generate a detailed report that:  
- Assesses whether lack of rewards is affecting performance.  
- Identifies if motivation issues are emerging.  
- Highlights risks of disengagement or resignation.  
- Recommends strategies to encourage improvement.  

Use data-backed insights in your analysis.  
'''
)   
AGENT_11=PromptTemplate.from_template(
    '''You are an expert in identifying workplace adaptation challenges.  
Review the following employee onboarding and leave data:  

{employee_onboarding_leave_data}  

Using this data, analyze:  
1. The quality of the employee’s onboarding experience.  
2. The frequency of unpaid leave taken.  
3. Any correlations between poor onboarding and financial/work-related disengagement.  
4. Possible risks of turnover or continued disengagement.  

Generate a detailed report that:  
- Assesses whether onboarding issues contributed to work challenges.  
- Identifies signs of financial strain or dissatisfaction.  
- Highlights risks of further disengagement.  
- Suggests actions to improve employee retention.  

Use specific data points to provide actionable insights.  
'''
)
AGENT_12=PromptTemplate.from_template(
    '''You are an expert in detecting employee oversight in performance evaluations.  
Review the following employee activity and performance review data:  

{employee_activity_review_data}  

Using this data, analyze:  
1. The employee’s work activity levels (emails, meetings, work hours).  
2. Whether the employee has received performance reviews at expected intervals.  
3. Potential risks of frustration due to lack of feedback.  
4. Possible impacts on motivation or retention.  

Generate a detailed report that:  
- Assesses whether the employee is being overlooked for reviews.  
- Identifies risks of disengagement due to lack of feedback.  
- Suggests corrective actions for better engagement.  

Use specific data points to back your analysis.  
'''
)   
AGENT_13=PromptTemplate.from_template(
    '''You are an expert in assessing inefficiencies in employee productivity.  
Review the following employee performance and activity data:  

{employee_low_performance_high_activity_data}  

Using this data, analyze:  
1. The employee’s performance ratings over time.  
2. The employee’s work activity levels (messages, meetings, work hours).  
3. Whether high activity is translating into productive outcomes.  
4. Potential risks of burnout due to inefficiencies.  

Generate a detailed report that:  
- Identifies whether the employee is overworking without results.  
- Assesses if performance issues stem from workload mismanagement.  
- Highlights risks of frustration and inefficiency.  
- Recommends strategies to improve performance.  

Support conclusions with specific data points.  
'''
)
AGENT_14=PromptTemplate.from_template(
    '''You are an expert in identifying employee stagnation due to lack of recognition.  
Review the following employee tenure and recognition data:  

{employee_tenure_recognition_data}  

Using this data, analyze:  
1. The duration of the employee’s tenure.  
2. Whether the employee has received any rewards or promotions.  
3. Any signs of long-term stagnation despite experience.  
4. Risks of dissatisfaction or disengagement.  

Generate a detailed report that:  
- Assesses if the employee is feeling undervalued.  
- Identifies risks of turnover due to lack of recognition.  
- Suggests interventions to retain and motivate long-tenured employees.  

Use specific data points for your conclusions.  
'''
)
AGENT_15=PromptTemplate.from_template(
    '''You are an expert in identifying employee well-being issues.  
Review the following employee vibe score and leave data:  

{employee_vibe_leave_data}  

Using this data, analyze:  
1. The employee’s vibe score trends over time.  
2. Whether the employee is taking breaks or time off.  
3. Potential risks of burnout due to prolonged work without leave.  
4. Possible impacts on productivity and morale.  

Generate a detailed report that:  
- Assesses whether declining mood is linked to overwork.  
- Identifies risks of exhaustion and stress.  
- Suggests strategies for better work-life balance.  

Use data-driven insights in your analysis.  
'''
)
AGENT_16=PromptTemplate.from_template(
    '''You are an expert in detecting career stagnation among high-performing employees.  
Review the following employee performance and promotion data:  

{employee_high_performance_promotion_data}  

Using this data, analyze:  
1. The employee’s performance history.  
2. Whether they have been considered for promotions or role expansions.  
3. Any gaps in career growth opportunities.  
4. Risks of dissatisfaction or talent loss.  

Generate a detailed report that:  
- Evaluates whether the employee is being overlooked.  
- Identifies career stagnation risks.  
- Suggests retention strategies to maintain engagement.  

Use specific data points for concrete insights.  
'''
)
AGENT_17=PromptTemplate.from_template(
    '''You are an expert in detecting disengagement in low-performing employees.  
Review the following employee performance and vibe score data:  

{employee_performance_vibe_data}  

Using this data, analyze:  
1. The employee’s performance history.  
2. Whether they have participated in vibe score assessments.  
3. Possible reasons for disengagement or inactivity.  
4. Risks of continued low motivation.  

Generate a detailed report that:  
- Assesses whether the employee is becoming disengaged.  
- Identifies risks of performance stagnation.  
- Suggests interventions for re-engagement.  

Support your insights with specific data points.  
'''
)
AGENT_18=PromptTemplate.from_template(
    '''You are an expert in detecting potential burnout among employees with high work engagement.  
Review the following employee leave and recognition data:  

{employee_leave_rewards_data}  

Using this data, analyze:  
1. Whether the employee has taken sufficient leave.  
2. Whether they have received any recognition for their efforts.  
3. Potential risks of overwork leading to dissatisfaction.  
4. Signs of possible disengagement despite high work activity.  

Generate a detailed report that:  
- Assesses risks of burnout.  
- Identifies lack of recognition despite consistent effort.  
- Recommends interventions to improve work-life balance.  

Use specific data points to justify your findings.  
'''
)
AGENT_19=PromptTemplate.from_template(
    '''You are an expert in identifying financial and career growth challenges among employees.  
Review the following employee leave and promotion data:  

{employee_leave_promotion_data}  

Using this data, analyze:  
1. The frequency of unpaid leave.  
2. Whether the employee has been considered for promotions.  
3. Any financial struggles affecting career growth.  
4. Risks of disengagement due to job instability.  

Generate a detailed report that:  
- Assesses financial concerns affecting motivation.  
- Identifies career stagnation risks.  
- Suggests possible interventions for career and financial stability.  

Use specific data-driven insights.  
'''
)
AGENT_20=PromptTemplate.from_template(
    '''You are an expert in analyzing employee adaptation and motivation trends.  
Review the following employee onboarding and rewards data:  

{employee_onboarding_rewards_data}  

Using this data, analyze:  
1. The quality of the employee’s onboarding experience based on feedback.  
2. Whether the employee has received any rewards or recognition.  
3. Any correlation between a poor onboarding experience and lack of motivation.  
4. Risks of disengagement due to feeling undervalued.  

Generate a detailed report that:  
- Assesses the impact of poor onboarding on long-term engagement.  
- Identifies if the lack of rewards is affecting employee morale.  
- Highlights risks of early dissatisfaction and turnover.  
- Suggests interventions to improve employee experience and motivation.  

Use specific data points to support your analysis.  
'''
)
# Consolidation Agent Prompt Template
CONSOLIDATION_AGENT_PROMPT = PromptTemplate.from_template(
"""You are an expert people analyst who specializes in synthesizing multiple data sources to develop a comprehensive understanding of employee behavior and mood.
You have received the following reports about an employee:

Report from Agent1:
{report1}

Report from Agent2:
{report2}

Report from Agent3:
{report3}

Report from Agent4:
{report4}

Report from Agent5:
{report5}

Report from Agent6:
{report6}

Report from Agent7:
{report7}

Report from Agent8:
{report8}

Report from Agent9:
{report9}

Report from Agent10:
{report10}

Report from Agent11:
{report11}

Report from Agent12:
{report12}

Report from Agent13:
{report13}

Report from Agent14:
{report14}

Report from Agent15:
{report15}

Report from Agent16:
{report16}

Report from Agent17:
{report17}

Report from Agent18:
{report18}

Report from Agent19:
{report19}

Report from Agent20:
{report20}

Your task is to:
1. Synthesize these reports into a cohesive understanding of the employee's current behavioral patterns and emotional state
2. Identify any contradictions or reinforcing patterns across the reports
3. Provide a nuanced assessment of the employee's overall mood and well-being
4. Determine if the employee requires any special support or intervention
5. Recommend specific, personalized actions to improve the employee's well-being and performance

Generate a comprehensive report that:
- Provides a holistic analysis of the employee's behavior and mood
- Offers evidence-based conclusions drawn from multiple data sources
- Presents clear, actionable recommendations
- Prioritizes the employee's well-being while considering organizational goals

Be balanced, empathetic, and specific in your analysis.
"""
)