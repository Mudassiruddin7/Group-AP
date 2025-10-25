"""
F2 Portfolio Recommender Agent - Agentic AI Core
Multi-step reasoning agent using LangChain for autonomous portfolio optimization
Demonstrates tool use, reasoning chains, and guardrail integration
"""
import os
import json
from typing import Dict, List, Optional, Any
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, AGENT_SYSTEM_PROMPT
from portfolio_optimizer import portfolio_optimizer_tool
from guardrails import check_input_safety, apply_output_guardrails, GuardrailSystem


class PortfolioRecommenderAgent:
    """
    Autonomous agentic AI for personalized portfolio recommendations
    Implements multi-step reasoning: understand → plan → execute → validate → explain
    """
    
    def __init__(self, api_key: Optional[str] = None, verbose: bool = True):
        """
        Initialize the agentic system
        
        Args:
            api_key: OpenAI API key (defaults to env variable)
            verbose: Enable detailed logging of agent reasoning
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.verbose = verbose
        self.guardrail = GuardrailSystem()
        
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY in .env file.")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            api_key=self.api_key
        )
        
        # Define agent tools
        self.tools = self._setup_tools()
        
        # Create agent
        self.agent = self._create_agent()
        
        # Execution tracking
        self.execution_log = []
    
    def _setup_tools(self) -> List[Tool]:
        """
        Define tools available to the agent
        
        Returns:
            List of LangChain Tool objects
        """
        tools = [
            Tool(
                name="portfolio_optimizer",
                func=self._portfolio_optimizer_wrapper,
                description="""
                Optimizes investment portfolio allocation based on user risk profile and time horizon.
                
                Input: JSON string with required fields:
                  - risk_profile (str): 'low', 'medium', or 'high'
                  - horizon_years (int): Investment time horizon in years (1-30)
                  - constraints (dict, optional): Additional optimization constraints
                
                Output: JSON with portfolio weights, performance metrics, and explanation
                
                Example input: {"risk_profile": "medium", "horizon_years": 5}
                
                Use this tool whenever user mentions:
                - Risk tolerance/appetite (conservative/moderate/aggressive)
                - Investment timeline/horizon
                - Portfolio allocation/recommendation request
                """
            ),
            Tool(
                name="extract_user_preferences",
                func=self._extract_preferences_wrapper,
                description="""
                Extracts structured risk profile and horizon from natural language user input.
                
                Input: User's natural language query
                
                Output: JSON with extracted parameters:
                  - risk_profile: 'low', 'medium', or 'high'
                  - horizon_years: integer
                  - confidence: extraction confidence score
                
                Use this tool FIRST to parse user intent before calling portfolio_optimizer.
                """
            )
        ]
        
        return tools
    
    def _portfolio_optimizer_wrapper(self, tool_input: str) -> str:
        """
        Wrapper for portfolio optimizer tool with error handling
        
        Args:
            tool_input: JSON string with optimization parameters
            
        Returns:
            JSON string with portfolio result
        """
        try:
            # Parse input
            params = json.loads(tool_input) if isinstance(tool_input, str) else tool_input
            
            # Call optimizer
            result = portfolio_optimizer_tool(
                risk_profile=params.get('risk_profile'),
                horizon_years=params.get('horizon_years'),
                constraints=params.get('constraints')
            )
            
            # Log execution
            self.execution_log.append({
                "tool": "portfolio_optimizer",
                "input": params,
                "success": 'error' not in result or not result['error'],
                "output_summary": {
                    "num_holdings": len(result.get('portfolio_weights', {})),
                    "expected_return": result.get('metrics', {}).get('expected_annual_return')
                }
            })
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {"error": f"Tool execution failed: {str(e)}"}
            return json.dumps(error_result)
    
    def _extract_preferences_wrapper(self, user_query: str) -> str:
        """
        Extract structured parameters from natural language using LLM
        
        Args:
            user_query: User's natural language input
            
        Returns:
            JSON string with extracted parameters
        """
        extraction_prompt = f"""
        Extract the investment preferences from this user query:
        
        Query: "{user_query}"
        
        Determine:
        1. Risk Profile: Map user's risk tolerance to 'low', 'medium', or 'high'
           - Keywords like conservative, safe, low-risk → 'low'
           - Keywords like balanced, moderate → 'medium'  
           - Keywords like aggressive, high-growth, high-risk → 'high'
           - Default to 'medium' if unclear
        
        2. Horizon Years: Extract investment time period in years
           - Look for explicit years mentioned
           - Map life events: "retirement" (assume 10-20 years), "short-term" (1-3), etc.
           - Default to 5 years if not specified
        
        3. Confidence: Rate 0.0-1.0 how confident you are in the extraction
        
        Return ONLY a JSON object with this exact structure:
        {{
          "risk_profile": "low|medium|high",
          "horizon_years": <integer>,
          "confidence": <float>,
          "reasoning": "<brief explanation>"
        }}
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=extraction_prompt)])
            
            # Parse LLM response
            response_text = response.content
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                extracted = json.loads(response_text[json_start:json_end])
            else:
                # Fallback defaults
                extracted = {
                    "risk_profile": "medium",
                    "horizon_years": 5,
                    "confidence": 0.3,
                    "reasoning": "Failed to parse, using defaults"
                }
            
            self.execution_log.append({
                "tool": "extract_user_preferences",
                "input": user_query,
                "success": True,
                "output": extracted
            })
            
            return json.dumps(extracted, indent=2)
            
        except Exception as e:
            return json.dumps({
                "risk_profile": "medium",
                "horizon_years": 5,
                "confidence": 0.0,
                "reasoning": f"Extraction failed: {str(e)}"
            })
    
    def _create_agent(self) -> AgentExecutor:
        """
        Create the LangChain agent with tools and prompts
        
        Returns:
            Configured AgentExecutor
        """
        # Define agent prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor with memory
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            max_iterations=5,
            early_stopping_method="generate",
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point: process user query through full agentic pipeline
        
        Pipeline:
        1. Input Guardrails: Check for PII, validate safety
        2. Agent Reasoning: Multi-step tool use and planning
        3. Output Guardrails: Validate results, enforce disclaimers
        4. Format Response: Structure for user consumption
        
        Args:
            user_query: Natural language investment query
            
        Returns:
            Complete response with portfolio, explanation, and metadata
        """
        # Step 1: Input Guardrails
        is_safe, safety_error = check_input_safety(user_query)
        
        if not is_safe:
            return {
                "success": False,
                "error": "Input Safety Violation",
                "message": safety_error,
                "portfolio": None,
                "explanation": None
            }
        
        # Step 2: Agent Execution
        try:
            # Invoke agent
            agent_response = self.agent.invoke({
                "input": user_query
            })
            
            # Extract portfolio data from agent output
            output_text = agent_response.get('output', '')
            
            # Parse portfolio data from agent's tool usage
            portfolio_data = self._extract_portfolio_from_logs()
            
            if not portfolio_data:
                # Fallback: try to parse from output text
                portfolio_data = {
                    "portfolio_weights": {},
                    "metrics": {},
                    "explanation": output_text
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": "Agent Execution Failed",
                "message": str(e),
                "portfolio": None,
                "explanation": None,
                "execution_log": self.execution_log
            }
        
        # Step 3: Output Guardrails
        validated_response = apply_output_guardrails(portfolio_data)
        
        # Step 4: Add execution metadata
        validated_response['agent_metadata'] = {
            "model": OPENAI_MODEL,
            "tool_calls": len(self.execution_log),
            "execution_log": self.execution_log
        }
        
        return validated_response
    
    def _extract_portfolio_from_logs(self) -> Optional[Dict]:
        """
        Extract the last successful portfolio optimization from execution log
        
        Returns:
            Portfolio data dictionary or None
        """
        for log_entry in reversed(self.execution_log):
            if log_entry.get('tool') == 'portfolio_optimizer' and log_entry.get('success'):
                # The output is in the tool wrapper
                # We need to get it from the actual execution
                return None
        
        return None
    
    def get_execution_summary(self) -> Dict:
        """
        Get summary of agent's reasoning and tool usage
        
        Returns:
            Execution statistics and logs
        """
        return {
            "total_tool_calls": len(self.execution_log),
            "tools_used": list(set([log['tool'] for log in self.execution_log])),
            "success_rate": sum([1 for log in self.execution_log if log.get('success', False)]) / max(len(self.execution_log), 1),
            "detailed_log": self.execution_log
        }


# Simple interface function for direct use
def get_portfolio_recommendation(
    user_query: str,
    api_key: Optional[str] = None,
    verbose: bool = False
) -> Dict:
    """
    Simplified interface for getting portfolio recommendations
    
    Args:
        user_query: Natural language investment query
        api_key: OpenAI API key (optional)
        verbose: Enable detailed logging
        
    Returns:
        Portfolio recommendation response
    """
    agent = PortfolioRecommenderAgent(api_key=api_key, verbose=verbose)
    return agent.process_query(user_query)


if __name__ == "__main__":
    # Test the agent
    print("="*70)
    print("F2 Portfolio Recommender Agent - Test Mode")
    print("="*70)
    
    # Check for API key
    if not OPENAI_API_KEY:
        print("\n❌ ERROR: OPENAI_API_KEY not set!")
        print("Please create a .env file with your OpenAI API key.")
        print("See .env.example for template.")
        exit(1)
    
    test_queries = [
        "I'm 30 years old, moderately risk-tolerant, and want to invest for 7 years for a house down payment.",
        "Conservative investor, 10-year horizon, capital preservation focus",
        "Aggressive growth portfolio for 3 years"
    ]
    
    print("\nRunning test queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {query}")
        print('='*70)
        
        try:
            response = get_portfolio_recommendation(query, verbose=True)
            
            if response.get('success'):
                print("\n✅ Success!")
                print(f"\n📊 Portfolio: {response.get('portfolio', {})}")
                print(f"\n📈 Metrics: {response.get('metrics', {})}")
                print(f"\n📝 Explanation:\n{response.get('explanation', '')[:300]}...")
            else:
                print(f"\n❌ Failed: {response.get('error')}")
                print(f"Message: {response.get('message')}")
                
        except Exception as e:
            print(f"\n❌ Exception: {str(e)}")
