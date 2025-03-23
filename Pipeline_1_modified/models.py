"""Data models for the employee analysis system."""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
## Agent 1
class employee_performance_data(BaseModel):
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool
    total_rewards_received: int
    total_reward_points: int
    Award_Type: str
    Award_Date: str
    Reward_Points: int

## Agent 2
class employee_activity_data(BaseModel):
    Date: str
    Teams_Messages_Sent: int
    Emails_Sent: int
    Meetings_Attended: int
    Work_Hours: float
    total_rewards_received: int
    total_reward_points: int
    Award_Type: str
    Award_Date: str
    Reward_Points: int

## Agent 3
class employee_onboarding_data(BaseModel):
    Joining_Date: str
    Onboarding_Feedback: str
    Mentor_Assigned: bool
    Initial_Training_Completed: bool

## Agent 4
class employee_leave_performance_data(BaseModel):
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool
    Leave_Type: str
    Leave_Days: int
    Leave_Start_Date: str
    Leave_End_Date: str

## Agent 5
class employee_leave_vibe_data(BaseModel):
    Response_Date: str
    Vibe_Score: int
    Emotion_Zone: str
    Leave_Type: str
    Leave_Days: int
    Leave_Start_Date: str
    Leave_End_Date: str

## Agent 6
class employee_performance_promotion_data(BaseModel):
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool

## Agent 7
class employee_performance_rewards_data(BaseModel):
    employee_id: str
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool
    total_rewards_received: int
    total_reward_points: int
    Award_Type: str
    Award_Date: str
    Reward_Points: int

## Agent 8
class employee_performance_mentorship_data(BaseModel):
    employee_id: str
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool
    Mentor_Assigned: bool
    Joining_Date: str
    Onboarding_Feedback: str
    Initial_Training_Completed: bool

## Agent 9
class employee_performance_feedback_data(BaseModel):
    employee_id: str
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool


class employee_low_performance_rewards_data(BaseModel):
    employee_id: str
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool
    total_rewards_received: int
    total_reward_points: int
    Award_Type: str
    Award_Date: str
    Reward_Points: int

class employee_onboarding_leave_data(BaseModel):
    Joining_Date: str
    Onboarding_Feedback: str
    Mentor_Assigned: bool
    Initial_Training_Completed: bool
    Leave_Type: str
    Leave_Days: int
    Leave_Start_Date: str
    Leave_End_Date: str

## Agent 12
class employee_activity_review_data(BaseModel):
    Date: str
    Teams_Messages_Sent: int
    Emails_Sent: int
    Meetings_Attended: int
    Work_Hours: float
    employee_id: str
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool
    
## Agent 13
class employee_low_performance_high_activity_data(BaseModel):
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool
    Date: str
    Teams_Messages_Sent: int
    Emails_Sent: int
    Meetings_Attended: int
    Work_Hours: float
    Response_Date: str
    Vibe_Score: int
    Emotion_Zone: str


class employee_tenure_recognition_data(BaseModel):
    Joining_Date: str
    total_rewards_received: int
    total_reward_points: int
    Award_Type: str
    Award_Date: str
    Reward_Points: int

class employee_vibe_leave_data(BaseModel):
    Leave_Type: str
    Leave_Days: int
    Leave_Start_Date: str
    Leave_End_Date: str
    Response_Date: str
    Vibe_Score: int
    Emotion_Zone: str

## Agent 16
class employee_high_performance_promotion_data(BaseModel):
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool

## Agent 17
class employee_performance_vibe_data(BaseModel):
    Response_Date: str
    Vibe_Score: int
    Emotion_Zone: str
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool
    Date: str
    Teams_Messages_Sent: int
    Emails_Sent: int
    Meetings_Attended: int
    Work_Hours: float

class employee_leave_rewards_data(BaseModel):
    Leave_Type: str
    Leave_Days: int
    Leave_Start_Date: str
    Leave_End_Date: str
    Award_Type: str
    Award_Date: str
    Reward_Points: int

## Agent 19
class employee_leave_promotion_data(BaseModel):
    Leave_Type: str
    Leave_Days: int
    Leave_Start_Date: str
    Leave_End_Date: str
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool
    Date: str
    Teams_Messages_Sent: int
    Emails_Sent: int
    Meetings_Attended: int
    Work_Hours: float

class employee_onboarding_rewards_data(BaseModel):
    Joining_Date: str
    Onboarding_Feedback: str
    Mentor_Assigned: bool
    Initial_Training_Completed: bool
    Award_Type: str
    Award_Date: str
    Reward_Points: int