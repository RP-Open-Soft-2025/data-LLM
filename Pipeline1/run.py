"""Simple example to run the employee analysis system."""

import json
import os
from langraph_workflow import employee_analysis_graph

def load_employee_data(file_path: str) -> dict:
    """Load employee data from a JSON file."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_report_to_text(report: dict, output_file: str) -> None:
    """Save the consolidated report to a text file."""
    with open(output_file, 'w') as file:
        file.write("=== EMPLOYEE MOOD AND BEHAVIOR ANALYSIS ===\n\n")
        
        # Overall analysis
        file.write("OVERALL ANALYSIS\n")
        file.write("=" * 80 + "\n")
        file.write(report.get("overall_analysis", "No overall analysis available.") + "\n\n")
        
        # Individual reports
        file.write("DETAILED ANALYSIS BY CATEGORY\n")
        file.write("=" * 80 + "\n\n")
        
        individual_reports = report.get("individual_reports", {})
        
        # Activity report
        file.write("ACTIVITY ANALYSIS\n")
        file.write("-" * 80 + "\n")
        activity_report = individual_reports.get("activity")
        if activity_report:
            file.write(activity_report.analysis + "\n\n")
        else:
            file.write("No activity analysis available.\n\n")
            
        # Leave report
        file.write("LEAVE ANALYSIS\n")
        file.write("-" * 80 + "\n")
        leave_report = individual_reports.get("leave")
        if leave_report:
            file.write(leave_report.analysis + "\n\n")
        else:
            file.write("No leave analysis available.\n\n")
            
        # Onboarding report
        file.write("ONBOARDING ANALYSIS\n")
        file.write("-" * 80 + "\n")
        onboarding_report = individual_reports.get("onboarding")
        if onboarding_report:
            file.write(onboarding_report.analysis + "\n\n")
        else:
            file.write("No onboarding analysis available.\n\n")
            
        # Performance report
        file.write("PERFORMANCE ANALYSIS\n")
        file.write("-" * 80 + "\n")
        performance_report = individual_reports.get("performance")
        if performance_report:
            file.write(performance_report.analysis + "\n\n")
        else:
            file.write("No performance analysis available.\n\n")
            
        # Rewards report
        file.write("REWARDS ANALYSIS\n")
        file.write("-" * 80 + "\n")
        rewards_report = individual_reports.get("rewards")
        if rewards_report:
            file.write(rewards_report.analysis + "\n\n")
        else:
            file.write("No rewards analysis available.\n\n")
            
        # Vibemeter report
        file.write("EMOTIONAL STATE ANALYSIS\n")
        file.write("-" * 80 + "\n")
        vibemeter_report = individual_reports.get("vibemeter")
        if vibemeter_report:
            file.write(vibemeter_report.analysis + "\n\n")
        else:
            file.write("No emotional state analysis available.\n\n")
        
        # Timestamp
        from datetime import datetime
        file.write(f"\nReport generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def main():
    """Run example analysis on employee data."""
    print("Starting employee analysis using LangGraph...")
    
    # Load employee data from employee.json
    employee_data = load_employee_data("employee.json")
    
    # Initialize the state
    initial_state = {
        "employee_data": employee_data,
        "status": "started"
    }
    
    # Run the analysis
    result = employee_analysis_graph.invoke(initial_state)
    
    # Print the result summary
    print("\n=== ANALYSIS COMPLETE ===\n")
    print("Overall Analysis:")
    print(result.get("consolidated_report", {}).get("overall_analysis", "No analysis available"))
    
    # Save to text file for inspection
    save_report_to_text(result.get("consolidated_report", {}), "EMP0108_report.txt")
    
    print("\nFull report saved to employee_report.txt")

if __name__ == "__main__":
    main()