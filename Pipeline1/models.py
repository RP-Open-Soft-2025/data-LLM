"""Data models for the employee analysis system."""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class ActivityData(BaseModel):
    Date: str
    Teams_Messages_Sent: int
    Emails_Sent: int
    Meetings_Attended: int
    Work_Hours: float

class LeaveData(BaseModel):
    Leave_Type: str
    Leave_Days: int
    Leave_Start_Date: str
    Leave_End_Date: str

class OnboardingData(BaseModel):
    Joining_Date: str
    Onboarding_Feedback: str
    Mentor_Assigned: bool
    Initial_Training_Completed: bool

class PerformanceData(BaseModel):
    Review_Period: str
    Performance_Rating: int
    Manager_Feedback: str
    Promotion_Consideration: bool

class RewardData(BaseModel):
    Award_Type: str
    Award_Date: str
    Reward_Points: int

class VibemeterData(BaseModel):
    Response_Date: str
    Vibe_Score: int
    Emotion_Zone: str

class CompanyData(BaseModel):
    activity: List[ActivityData] = []
    leave: List[LeaveData] = []
    onboarding: List[OnboardingData] = []
    performance: List[PerformanceData] = []
    rewards: List[RewardData] = []
    vibemeter: List[VibemeterData] = []

class EmployeeData(BaseModel):
    employee_id: str
    company_data: CompanyData

class AgentReport(BaseModel):
    analysis: str = ""
    insights: List[str] = []
    mood_indicators: Dict[str, float] = {}
    # Update raw_data to accept both list and dict
    raw_data: Optional[Union[List[Any], Dict[str, Any]]] = None

class CombinedReport(BaseModel):
    activity_report: AgentReport
    leave_report: AgentReport
    onboarding_report: AgentReport
    performance_report: AgentReport
    rewards_report: AgentReport
    vibemeter_report: AgentReport
    overall_analysis: str
    recommended_actions: List[str] = []
    mood_assessment: str
    behavior_patterns: List[str] = []