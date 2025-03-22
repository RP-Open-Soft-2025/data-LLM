"""LangGraph workflow implementation for the employee analysis system."""

from typing import Dict, List, Any, Annotated, TypedDict, Literal
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
import json

from agents import (
    ActivityAgent, 
    LeaveAgent, 
    OnboardingAgent, 
    PerformanceAgent, 
    RewardsAgent, 
    VibemeterAgent,
    ConsolidationAgent
)
from models import AgentReport

# Define the state for our graph
class EmployeeAnalysisState(TypedDict):
    employee_data: Dict[str, Any]
    activity_report: AgentReport
    leave_report: AgentReport
    onboarding_report: AgentReport
    performance_report: AgentReport
    rewards_report: AgentReport
    vibemeter_report: AgentReport
    consolidated_report: Dict[str, Any]
    status: str

# Initialize all agents
activity_agent = ActivityAgent()
leave_agent = LeaveAgent()
onboarding_agent = OnboardingAgent()
performance_agent = PerformanceAgent()
rewards_agent = RewardsAgent()
vibemeter_agent = VibemeterAgent()
consolidation_agent = ConsolidationAgent()

# Define agent functions that will be nodes in our graph
def process_activity(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process activity data and update state with report."""
    report = activity_agent.process(state["employee_data"])
    return {"activity_report": report}

def process_leave(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process leave data and update state with report."""
    report = leave_agent.process(state["employee_data"])
    return {"leave_report": report}

def process_onboarding(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process onboarding data and update state with report."""
    report = onboarding_agent.process(state["employee_data"])
    return {"onboarding_report": report}

def process_performance(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process performance data and update state with report."""
    report = performance_agent.process(state["employee_data"])
    return {"performance_report": report}

def process_rewards(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process rewards data and update state with report."""
    report = rewards_agent.process(state["employee_data"])
    return {"rewards_report": report}

def process_vibemeter(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process vibemeter data and update state with report."""
    report = vibemeter_agent.process(state["employee_data"])
    return {"vibemeter_report": report}

def consolidate_reports(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Consolidate all reports into a single analysis."""
    reports = {
        "activity": state["activity_report"],
        "leave": state["leave_report"],
        "onboarding": state["onboarding_report"],
        "performance": state["performance_report"],
        "rewards": state["rewards_report"],
        "vibemeter": state["vibemeter_report"]
    }
    consolidated_report = consolidation_agent.process(reports)
    return {
        "consolidated_report": consolidated_report,
        "status": "complete"
    }

def determine_next_step(state: EmployeeAnalysisState) -> Literal["process_activity", "process_leave", "process_onboarding", 
                                                               "process_performance", "process_rewards", "process_vibemeter",
                                                               "consolidate_reports", "end"]:
    """Determine which node to execute next based on current state."""
    # Check if consolidation is complete
    if state.get("status") == "complete":
        return "end"
    
    # Check if all reports exist and we can consolidate
    if (state.get("activity_report") and 
        state.get("leave_report") and 
        state.get("onboarding_report") and 
        state.get("performance_report") and 
        state.get("rewards_report") and 
        state.get("vibemeter_report") and
        not state.get("consolidated_report")):
        return "consolidate_reports"
    
    # Otherwise determine which report to process next
    if not state.get("activity_report"):
        return "process_activity"
    elif not state.get("leave_report"):
        return "process_leave"
    elif not state.get("onboarding_report"):
        return "process_onboarding"
    elif not state.get("performance_report"):
        return "process_performance"
    elif not state.get("rewards_report"):
        return "process_rewards"
    elif not state.get("vibemeter_report"):
        return "process_vibemeter"
    
    # Default to consolidation if all reports exist
    return "consolidate_reports"

# Create the graph
def create_employee_analysis_graph():
    """Create and configure the LangGraph workflow."""
    # Initialize the graph
    graph = StateGraph(EmployeeAnalysisState)
    
    # Add nodes for each agent process
    graph.add_node("process_activity", process_activity)
    graph.add_node("process_leave", process_leave)
    graph.add_node("process_onboarding", process_onboarding)
    graph.add_node("process_performance", process_performance)
    graph.add_node("process_rewards", process_rewards)
    graph.add_node("process_vibemeter", process_vibemeter)
    graph.add_node("consolidate_reports", consolidate_reports)
    
    # Add conditional edges from each node to determine next step
    graph.add_conditional_edges(
        "process_activity",
        determine_next_step,
        {
            "process_activity": "process_activity",
            "process_leave": "process_leave",
            "process_onboarding": "process_onboarding",
            "process_performance": "process_performance",
            "process_rewards": "process_rewards",
            "process_vibemeter": "process_vibemeter",
            "consolidate_reports": "consolidate_reports",
            "end": END
        }
    )
    
    graph.add_conditional_edges(
        "process_leave",
        determine_next_step,
        {
            "process_activity": "process_activity",
            "process_leave": "process_leave",
            "process_onboarding": "process_onboarding",
            "process_performance": "process_performance",
            "process_rewards": "process_rewards",
            "process_vibemeter": "process_vibemeter",
            "consolidate_reports": "consolidate_reports",
            "end": END
        }
    )
    
    graph.add_conditional_edges(
        "process_onboarding",
        determine_next_step,
        {
            "process_activity": "process_activity",
            "process_leave": "process_leave",
            "process_onboarding": "process_onboarding",
            "process_performance": "process_performance",
            "process_rewards": "process_rewards",
            "process_vibemeter": "process_vibemeter",
            "consolidate_reports": "consolidate_reports",
            "end": END
        }
    )
    
    graph.add_conditional_edges(
        "process_performance",
        determine_next_step,
        {
            "process_activity": "process_activity",
            "process_leave": "process_leave",
            "process_onboarding": "process_onboarding",
            "process_performance": "process_performance",
            "process_rewards": "process_rewards",
            "process_vibemeter": "process_vibemeter",
            "consolidate_reports": "consolidate_reports",
            "end": END
        }
    )
    
    graph.add_conditional_edges(
        "process_rewards",
        determine_next_step,
        {
            "process_activity": "process_activity",
            "process_leave": "process_leave",
            "process_onboarding": "process_onboarding",
            "process_performance": "process_performance",
            "process_rewards": "process_rewards",
            "process_vibemeter": "process_vibemeter",
            "consolidate_reports": "consolidate_reports",
            "end": END
        }
    )
    
    graph.add_conditional_edges(
        "process_vibemeter",
        determine_next_step,
        {
            "process_activity": "process_activity",
            "process_leave": "process_leave",
            "process_onboarding": "process_onboarding",
            "process_performance": "process_performance",
            "process_rewards": "process_rewards",
            "process_vibemeter": "process_vibemeter",
            "consolidate_reports": "consolidate_reports",
            "end": END
        }
    )
    
    graph.add_conditional_edges(
        "consolidate_reports",
        determine_next_step,
        {
            "process_activity": "process_activity",
            "process_leave": "process_leave",
            "process_onboarding": "process_onboarding",
            "process_performance": "process_performance",
            "process_rewards": "process_rewards",
            "process_vibemeter": "process_vibemeter",
            "consolidate_reports": "consolidate_reports",
            "end": END
        }
    )
    
    # Set the entry point - start with determining next step from initial state
    # This needs to be a node that corresponds to a conditional function
    # For initial entry, we'll use the first process node and let the conditional logic take over
    graph.set_entry_point("process_activity")
    
    # Compile the graph
    return graph.compile()

# Create a runnable graph
employee_analysis_graph = create_employee_analysis_graph()