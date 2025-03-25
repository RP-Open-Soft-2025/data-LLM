"""Main entry point for the employee analysis system."""

import json
import argparse
from typing import Dict, Any
from .langraph_workflow import employee_analysis_graph
from .models import EmployeeData

def load_employee_data(file_path: str) -> Dict[str, Any]:
    """Load employee data from a JSON file."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_report_to_text(report: Dict[str, Any], output_file: str) -> None:
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

def format_report_for_display(report: Dict[str, Any]) -> str:
    """Format the consolidated report for human-readable display."""
    consolidated = report.get("consolidated_report", {})
    overall_analysis = consolidated.get("overall_analysis", "No analysis available.")
    
    formatted_report = "=== EMPLOYEE BEHAVIOR AND MOOD ANALYSIS ===\n\n"
    formatted_report += overall_analysis
    
    return formatted_report

def main():
    """Main function to run the employee analysis system."""
    parser = argparse.ArgumentParser(description="Analyze employee behavior and mood.")
    parser.add_argument("--input", "-i", required=True, help="Path to employee data JSON file")
    parser.add_argument("--output", "-o", default="employee_report.txt", help="Path to save output report")
    args = parser.parse_args()
    
    # Load employee data
    print(f"Loading employee data from {args.input}...")
    employee_data = load_employee_data(args.input)
    
    # Validate data format (simple check)
    if "employee_id" not in employee_data or "company_data" not in employee_data:
        print("Error: Invalid employee data format.")
        return
    
    # Initialize the state
    initial_state = {
        "employee_data": employee_data,
        "status": "started"
    }
    
    # Run the analysis
    print("Analyzing employee data...")
    result = employee_analysis_graph.invoke(initial_state)
    
    # Extract the consolidated report
    consolidated_report = result.get("consolidated_report", {})
    
    # Save the full report to a text file
    print(f"Saving detailed report to {args.output}...")
    save_report_to_text(consolidated_report, args.output)
    
    # Display a human-readable summary
    print("\n" + "="*50)
    print(format_report_for_display(result))
    print("="*50)
    print(f"\nFull report saved to {args.output}")

if __name__ == "__main__":
    main()