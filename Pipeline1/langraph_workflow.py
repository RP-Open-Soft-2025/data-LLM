"""LangGraph workflow implementation for the employee analysis system with parallel processing."""

from typing import Dict, List, Any, Annotated, TypedDict, Literal
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
import json
import os
import urllib.parse
import urllib.request
import concurrent.futures
import asyncio

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

# Initial node that just passes the data through
def initialize_analysis(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Initialize the analysis and pass through the employee data."""
    print("Initializing employee analysis...")
    return {}

# Define agent functions that will be nodes in our graph
def process_activity(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process activity data and update state with report."""
    print("Processing activity data...")
    report = activity_agent.process(state["employee_data"])
    return {"activity_report": report}

def process_leave(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process leave data and update state with report."""
    print("Processing leave data...")
    report = leave_agent.process(state["employee_data"])
    return {"leave_report": report}

def process_onboarding(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process onboarding data and update state with report."""
    print("Processing onboarding data...")
    report = onboarding_agent.process(state["employee_data"])
    return {"onboarding_report": report}

def process_performance(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process performance data and update state with report."""
    print("Processing performance data...")
    report = performance_agent.process(state["employee_data"])
    return {"performance_report": report}

def process_rewards(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process rewards data and update state with report."""
    print("Processing rewards data...")
    report = rewards_agent.process(state["employee_data"])
    return {"rewards_report": report}

def process_vibemeter(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Process vibemeter data and update state with report."""
    print("Processing vibemeter data...")
    report = vibemeter_agent.process(state["employee_data"])
    return {"vibemeter_report": report}

def consolidate_reports(state: EmployeeAnalysisState) -> EmployeeAnalysisState:
    """Consolidate all reports into a single analysis."""
    print("Consolidating all reports...")
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

# Helper function to process reports in parallel using ThreadPoolExecutor
def process_reports_in_parallel(employee_data):
    """Process all reports in parallel using ThreadPoolExecutor."""
    reports = {}
    
    # Define the processing functions and their names
    processors = [
        (process_activity, "activity_report"),
        (process_leave, "leave_report"),
        (process_onboarding, "onboarding_report"),
        (process_performance, "performance_report"),
        (process_rewards, "rewards_report"),
        (process_vibemeter, "vibemeter_report")
    ]
    
    # Create a state with employee data for each processor
    states = [{"employee_data": employee_data} for _ in processors]
    
    # Process in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        # Submit all tasks
        futures = [executor.submit(processor, state) for (processor, _), state in zip(processors, states)]
        
        # Collect results as they complete
        for (_, report_key), future in zip(processors, futures):
            try:
                result = future.result()
                reports.update(result)
            except Exception as e:
                print(f"Error processing {report_key}: {str(e)}")
    
    return reports

# Helper function to process reports in parallel using asyncio for even better performance
async def process_reports_async(employee_data):
    """Process all reports in parallel using asyncio."""
    # Run all agents concurrently
    activity_task = activity_agent.aprocess(employee_data)
    leave_task = leave_agent.aprocess(employee_data)
    onboarding_task = onboarding_agent.aprocess(employee_data)
    performance_task = performance_agent.aprocess(employee_data)
    rewards_task = rewards_agent.aprocess(employee_data)
    vibemeter_task = vibemeter_agent.aprocess(employee_data)
    
    # Gather results
    activity_report, leave_report, onboarding_report, performance_report, rewards_report, vibemeter_report = await asyncio.gather(
        activity_task, leave_task, onboarding_task, performance_task, rewards_task, vibemeter_task
    )
    
    # Combine reports
    reports = {
        "activity": activity_report,
        "leave": leave_report,
        "onboarding": onboarding_report,
        "performance": performance_report,
        "rewards": rewards_report,
        "vibemeter": vibemeter_report
    }
    
    # Consolidate reports
    consolidated_report = await consolidation_agent.aprocess(reports)
    
    return {
        "reports": reports,
        "consolidated_report": consolidated_report
    }

# Create the graph
def create_employee_analysis_graph():
    """Create and configure the LangGraph workflow with fan-out fan-in pattern."""
    # Initialize the graph
    graph = StateGraph(EmployeeAnalysisState)
    
    # Add nodes
    graph.add_node("initialize", initialize_analysis)
    graph.add_node("process_activity", process_activity)
    graph.add_node("process_leave", process_leave)
    graph.add_node("process_onboarding", process_onboarding)
    graph.add_node("process_performance", process_performance)
    graph.add_node("process_rewards", process_rewards)
    graph.add_node("process_vibemeter", process_vibemeter)
    graph.add_node("consolidate_reports", consolidate_reports)
    
    # Fan-out: Add edges from initialize to all processing nodes
    graph.add_edge("initialize", "process_activity")
    graph.add_edge("initialize", "process_leave")
    graph.add_edge("initialize", "process_onboarding")
    graph.add_edge("initialize", "process_performance")
    graph.add_edge("initialize", "process_rewards")
    graph.add_edge("initialize", "process_vibemeter")
    
    # Fan-in: Add edges from all processing nodes to consolidate
    graph.add_edge("process_activity", "consolidate_reports")
    graph.add_edge("process_leave", "consolidate_reports")
    graph.add_edge("process_onboarding", "consolidate_reports")
    graph.add_edge("process_performance", "consolidate_reports")
    graph.add_edge("process_rewards", "consolidate_reports")
    graph.add_edge("process_vibemeter", "consolidate_reports")
    
    # Final edge
    graph.add_edge("consolidate_reports", END)
    
    # Set the entry point
    graph.set_entry_point("initialize")
    
    # Compile the graph
    return graph.compile()

# Create a runnable graph
employee_analysis_graph = create_employee_analysis_graph()