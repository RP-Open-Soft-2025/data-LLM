"""Implementation of individual agents for employee analysis."""

from typing import Dict, Any, List, Union
import json
from .config import get_llm
from .models import AgentReport
from .prompt_templates import (
    ACTIVITY_AGENT_PROMPT,
    LEAVE_AGENT_PROMPT,
    ONBOARDING_AGENT_PROMPT,
    PERFORMANCE_AGENT_PROMPT,
    REWARDS_AGENT_PROMPT,
    # VIBEMETER_AGENT_PROMPT,
    CONSOLIDATION_AGENT_PROMPT,
)


class BaseAgent:
    """Base agent class with common functionality."""

    def __init__(self, prompt_template, data_key):
        self.llm = get_llm()
        self.prompt_template = prompt_template
        self.data_key = data_key
        # Create the chain - works with both older and newer LangChain
        try:
            # Try newer pipe syntax
            self.chain = prompt_template | self.llm
        except:
            # Fall back to LLMChain for older versions
            from langchain.chains import LLMChain

            self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def format_data(self, data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> str:
        """Format data for prompt input."""
        return json.dumps(data, indent=2)

    def process(self, employee_data: Dict[str, Any]) -> AgentReport:
        """Process data and generate report."""
        # Get the data for this agent's section
        data = employee_data.get("company_data", {}).get(self.data_key, [])
        formatted_data = self.format_data(data)

        # Create input for the prompt
        prompt_input = {f"{self.data_key}_data": formatted_data}
        if self.data_key != "vibemeter":
            vibemeter_data = employee_data.get("company_data", {}).get("vibemeter", [])
            formatted_vibemeter_data = self.format_data(vibemeter_data)
            prompt_input["vibemeter_data"] = formatted_vibemeter_data
        # Generate report
        result = self.chain.invoke(prompt_input)

        # Extract content based on result type
        if hasattr(result, "content"):
            # New LangChain returns a message with content
            analysis = result.content
        elif isinstance(result, dict) and "text" in result:
            # Old LLMChain returns dict with text
            analysis = result["text"]
        else:
            # Generic fallback
            analysis = str(result)

        # Create a structured report
        report = AgentReport(
            analysis=analysis, raw_data=data  # This now accepts both list and dict
        )
        return report


class ActivityAgent(BaseAgent):
    """Agent for analyzing employee activity data."""

    def __init__(self):
        super().__init__(ACTIVITY_AGENT_PROMPT, "activity")


class LeaveAgent(BaseAgent):
    """Agent for analyzing employee leave data."""

    def __init__(self):
        super().__init__(LEAVE_AGENT_PROMPT, "leave")


class OnboardingAgent(BaseAgent):
    """Agent for analyzing employee onboarding data."""

    def __init__(self):
        super().__init__(ONBOARDING_AGENT_PROMPT, "onboarding")


class PerformanceAgent(BaseAgent):
    """Agent for analyzing employee performance data."""

    def __init__(self):
        super().__init__(PERFORMANCE_AGENT_PROMPT, "performance")


class RewardsAgent(BaseAgent):
    """Agent for analyzing employee rewards data."""

    def __init__(self):
        super().__init__(REWARDS_AGENT_PROMPT, "rewards")


# class VibemeterAgent(BaseAgent):
#     """Agent for analyzing employee vibemeter data."""

#     def __init__(self):
#         super().__init__(VIBEMETER_AGENT_PROMPT, "vibemeter")


class ConsolidationAgent:
    """Agent for consolidating individual reports."""

    def __init__(self):
        self.llm = get_llm(
            temperature=0.3
        )  # Slightly higher temperature for creative synthesis
        self.prompt_template = CONSOLIDATION_AGENT_PROMPT
        # Create the chain - works with both older and newer LangChain
        try:
            # Try newer pipe syntax
            self.chain = self.prompt_template | self.llm
        except:
            # Fall back to LLMChain for older versions
            from langchain.chains import LLMChain

            self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def process(self, reports: Dict[str, AgentReport]) -> Dict[str, Any]:
        """Process individual reports and generate a consolidated report."""
        # Create input for the prompt
        prompt_input = {
            "activity_report": reports["activity"].analysis,
            "leave_report": reports["leave"].analysis,
            "onboarding_report": reports["onboarding"].analysis,
            "performance_report": reports["performance"].analysis,
            "rewards_report": reports["rewards"].analysis,
            # "vibemeter_report": reports["vibemeter"].analysis,
        }

        # Generate consolidated report
        result = self.chain.invoke(prompt_input)

        # Extract content based on result type
        if hasattr(result, "content"):
            # New LangChain returns a message with content
            analysis = result.content
        elif isinstance(result, dict) and "text" in result:
            # Old LLMChain returns dict with text
            analysis = result["text"]
        else:
            # Generic fallback
            analysis = str(result)

        # Create a structured consolidated report
        consolidated_report = {
            "individual_reports": reports,
            "overall_analysis": analysis,
        }
        return consolidated_report
