"""Implementation of individual agents for employee analysis."""

from typing import Dict, Any, List, Union
import json
from config import get_llm
from models import AgentReport
import prompt_templates

class BaseAgent:
    """Base agent class with common functionality."""
    
    def __init__(self, prompt_template, data_key1, data_key2=None):
        self.llm = get_llm()
        self.prompt_template = prompt_template
        self.data_key1 = data_key1
        self.data_key2 = data_key2
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
        # Retrieve data for the primary key
        data1 = employee_data.get("company_data", {}).get(self.data_key1, [])
        # Retrieve data for the secondary key if provided
        data2 = []
        if self.data_key2:
            data2 = employee_data.get("company_data", {}).get(self.data_key2, [])
        # Combine the data lists
        combined_data = data1 + data2
        formatted_data = self.format_data(combined_data)
        
        # Prepare prompt input based on provided keys
        prompt_key = f"{self.data_key1}_data" if not self.data_key2 else f"{self.data_key1}_{self.data_key2}_data"
        prompt_input = { prompt_key: formatted_data }
        
        # Generate report
        result = self.chain.invoke(prompt_input)
        if hasattr(result, 'content'):
            analysis = result.content
        elif isinstance(result, dict) and 'text' in result:
            analysis = result['text']
        else:
            analysis = str(result)
        
        report = AgentReport(
            analysis=analysis,
            raw_data=combined_data
        )
        return report

class Agent1(BaseAgent):
    """Agent for analyzing Poor Performance & No Promotion Consideration."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_1, "performance")
        
class Agent2(BaseAgent):
    """Agent for analyzing High Work Activity but No Recognition."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_2, "activity", "rewards")
        
class Agent3(BaseAgent):
    """Agent for analyzing Poor Onboarding & No Mentor Assigned."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_3, "onboarding")
        
class Agent4(BaseAgent):
    """Agent for analyzing Frequent Sick Leave & Declining Performance."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_4, "performance","leaves")
        
class Agent5(BaseAgent):
    """Agent for analyzing Frequent Unpaid Leave & Low Vibe Score."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_5, "leave", "vibemeter")
        
class Agent6(BaseAgent):
    """Agent for analyzing High Performance but No Promotion Consideration."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_6, "performance")
        
class Agent7(BaseAgent):
    """Agent for analyzing High Performance but No Recognition (Rewards)."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_7, "performance", "rewards")
        
class Agent8(BaseAgent):
    """Agent for analyzing Low Performance & No Mentor Assigned."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_8, "performance", "onboarding")
        
class Agent9(BaseAgent):
    """Agent for analyzing Good Performance but Poor Manager Feedback."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_9, "performance")
        
class Agent10(BaseAgent):
    """Agent for analyzing Declining Performance & No Rewards."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_10, "performance", "rewards")
        
class Agent11(BaseAgent):
    """Agent for analyzing Poor Onboarding & Frequent Unpaid Leave."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_11, "onboarding", "leave")
        
class Agent12(BaseAgent):
    """Agent for analyzing High Work Activity but No Performance Reviews."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_12, "activity", "performance")
        
class Agent13(BaseAgent):
    """Agent for analyzing Low Performance & High Work Activity."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_13, "performance", "activity")
        
class Agent14(BaseAgent):
    """Agent for analyzing No Recognition Despite Long Tenure."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_14, "rewards","onboarding")
        
class Agent15(BaseAgent):
    """Agent for analyzing Declining Vibe Score & No Leave Taken."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_15, "vibemeter", "leave")
        
class Agent16(BaseAgent):
    """Agent for analyzing High Performance But No Career Progression."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_16, "performance")
        
class Agent17(BaseAgent):
    """Agent for analyzing Low Performance & No Vibe Score Updates."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_17, "performance", "vibemeter")
        
class Agent18(BaseAgent):
    """Agent for analyzing No Leave Taken & No Rewards."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_18, "leave", "rewards")
        
class Agent19(BaseAgent):
    """Agent for analyzing Frequent Unpaid Leave & No Promotion Consideration."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_19, "leave", "performance")
        
class Agent20(BaseAgent):
    """Agent for analyzing Poor Onboarding & No Rewards Given."""
    def __init__(self):
        super().__init__(prompt_templates.AGENT_20,  "onboarding", "rewards")

class ConsolidationAgent:
    """Agent for consolidating individual reports."""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.3)  # Slightly higher temperature for creative synthesis
        self.prompt_template = prompt_templates.CONSOLIDATION_AGENT_PROMPT
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
            "agent1_report": reports["agent1"].analysis,
            "agent2_report": reports["agent2"].analysis,
            "agent3_report": reports["agent3"].analysis,
            "agent4_report": reports["agent4"].analysis,
            "agent5_report": reports["agent5"].analysis,
            "agent6_report": reports["agent6"].analysis,
            "agent7_report": reports["agent7"].analysis,
            "agent8_report": reports["agent8"].analysis,
            "agent9_report": reports["agent9"].analysis,
            "agent10_report": reports["agent10"].analysis,
            "agent11_report": reports["agent11"].analysis,
            "agent12_report": reports["agent12"].analysis,
            "agent13_report": reports["agent13"].analysis,
            "agent14_report": reports["agent14"].analysis,
            "agent15_report": reports["agent15"].analysis,
            "agent16_report": reports["agent16"].analysis,
            "agent17_report": reports["agent17"].analysis,
            "agent18_report": reports["agent18"].analysis,
            "agent19_report": reports["agent19"].analysis,
            "agent20_report": reports["agent20"].analysis
        }
        
        # Generate consolidated report
        result = self.chain.invoke(prompt_input)
        
        # Extract content based on result type
        if hasattr(result, 'content'):
            # New LangChain returns a message with content
            analysis = result.content
        elif isinstance(result, dict) and 'text' in result:
            # Old LLMChain returns dict with text
            analysis = result['text']
        else:
            # Generic fallback
            analysis = str(result)
        
        # Create a structured consolidated report
        consolidated_report = {
            "individual_reports": reports,
            "overall_analysis": analysis
        }
        return consolidated_report