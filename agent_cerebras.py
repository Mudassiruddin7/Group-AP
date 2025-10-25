"""
Cerebras-Powered Portfolio Recommender Agent
Agentic AI orchestration using Cerebras Cloud SDK
"""
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime

from cerebras.cloud.sdk import Cerebras

from config_new import (
    CEREBRAS_API_KEY,
    CEREBRAS_MODEL,
    CEREBRAS_TEMPERATURE,
    CEREBRAS_TOP_P,
    CEREBRAS_MAX_TOKENS,
    AGENT_SYSTEM_PROMPT,
    EXTRACTION_PROMPT_TEMPLATE,
    MANDATORY_DISCLAIMER
)
from portfolio_optimizer_csv import CSVPortfolioOptimizer, create_optimizer
from guardrails import InputGuardrail, OutputGuardrail

logger = logging.getLogger(__name__)


class CerebrasPortfolioAgent:
    """
    Autonomous portfolio recommendation agent powered by Cerebras
    Orchestrates LLM reasoning with quantitative optimization tools
    """
    
    def __init__(
        self,
        api_key: str = CEREBRAS_API_KEY,
        model: str = CEREBRAS_MODEL,
        optimizer: Optional[CSVPortfolioOptimizer] = None
    ):
        """
        Initialize agent with Cerebras client
        
        Args:
            api_key: Cerebras API key
            model: Model name (llama3.1-70b or qwen-3-235b-a22b-instruct-2507)
            optimizer: Portfolio optimizer instance
        """
        self.client = Cerebras(api_key=api_key)
        self.model = model
        self.optimizer = optimizer or create_optimizer()
        
        # Initialize guardrails
        self.input_guardrail = InputGuardrail()
        self.output_guardrail = OutputGuardrail()
        
        logger.info(f"Initialized CerebrasPortfolioAgent with model={model}")
    
    def process_query(self, user_query: str, chat_history: Optional[List[Dict]] = None) -> Dict:
        """
        Main entry point: process user query and generate portfolio recommendation
        
        Args:
            user_query: User's natural language query
            chat_history: Previous conversation context
            
        Returns:
            Response dictionary with recommendation and metadata
        """
        logger.info(f"Processing query: {user_query[:100]}...")
        
        # Step 1: Input Guardrails
        guardrail_result = self.input_guardrail.check(user_query)
        
        if not guardrail_result["passed"]:
            return {
                "success": False,
                "error": "Input validation failed",
                "issues": guardrail_result["issues"],
                "message": "Your query contains sensitive information or violates safety policies. Please rephrase."
            }
        
        # Step 2: Extract Investment Parameters using Cerebras
        try:
            params = self._extract_parameters(user_query)
            logger.info(f"Extracted parameters: {params}")
        except Exception as e:
            logger.error(f"Parameter extraction failed: {e}")
            return {
                "success": False,
                "error": "Could not understand investment requirements",
                "message": "I couldn't extract clear investment parameters from your query. "
                          "Please specify your risk tolerance (low/medium/high) and investment timeline."
            }
        
        # Step 3: Quantitative Optimization
        try:
            optimization_result = self.optimizer.optimize_portfolio(
                risk_profile=params["risk_profile"],
                horizon_years=params["horizon_years"],
                sector_preferences=params.get("sector_preferences"),
                exclude_tickers=params.get("constraints", {}).get("exclude_tickers")
            )
            logger.info(f"Optimization completed: {len(optimization_result['weights'])} holdings")
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return {
                "success": False,
                "error": "Portfolio optimization failed",
                "message": f"Could not generate portfolio recommendation: {str(e)}"
            }
        
        # Step 4: Generate Enhanced Explanation using Cerebras
        try:
            enhanced_explanation = self._generate_enhanced_explanation(
                user_query=user_query,
                params=params,
                optimization_result=optimization_result
            )
        except Exception as e:
            logger.warning(f"Enhanced explanation failed: {e}")
            enhanced_explanation = optimization_result["explanation"]
        
        # Step 5: Output Guardrails
        final_output = f"{enhanced_explanation}\n\n{MANDATORY_DISCLAIMER}"
        
        output_check = self.output_guardrail.check(final_output)
        
        if not output_check["passed"]:
            # Force disclaimer if missing
            final_output = f"{enhanced_explanation}\n\n{MANDATORY_DISCLAIMER}"
        
        # Construct final response
        response = {
            "success": True,
            "recommendation": {
                "allocation": optimization_result["weights"],
                "metrics": optimization_result["metrics"],
                "sector_allocation": optimization_result["sector_allocation"],
                "explanation": final_output
            },
            "parameters": params,
            "metadata": {
                "model": self.model,
                "optimization_date": optimization_result["optimization_date"],
                "guardrails_passed": True
            }
        }
        
        logger.info("Query processing complete")
        return response
    
    def _extract_parameters(self, user_query: str) -> Dict:
        """
        Use Cerebras to extract investment parameters from natural language
        
        Args:
            user_query: User's query
            
        Returns:
            Extracted parameters dictionary
        """
        logger.info("Extracting parameters with Cerebras")
        
        extraction_prompt = EXTRACTION_PROMPT_TEMPLATE.format(query=user_query)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a financial parameter extraction AI. Extract investment parameters and return ONLY valid JSON."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.3,  # Lower temperature for extraction
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()
            
            params = json.loads(content)
            
            # Validate required fields
            if "risk_profile" not in params:
                params["risk_profile"] = "medium"  # Default
            
            if "horizon_years" not in params:
                params["horizon_years"] = 5  # Default
            
            # Ensure valid risk profile
            if params["risk_profile"] not in ["low", "medium", "high"]:
                params["risk_profile"] = "medium"
            
            return params
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}, content: {content}")
            # Return defaults
            return {
                "risk_profile": "medium",
                "horizon_years": 5,
                "sector_preferences": [],
                "constraints": {},
                "confidence": 0.5,
                "reasoning": "Using default parameters due to extraction failure"
            }
    
    def _generate_enhanced_explanation(
        self,
        user_query: str,
        params: Dict,
        optimization_result: Dict
    ) -> str:
        """
        Use Cerebras to generate a personalized, conversational explanation
        
        Args:
            user_query: Original user query
            params: Extracted parameters
            optimization_result: Optimization results
            
        Returns:
            Enhanced explanation text
        """
        logger.info("Generating enhanced explanation with Cerebras")
        
        # Prepare context for LLM
        context = {
            "user_query": user_query,
            "risk_profile": params["risk_profile"],
            "horizon_years": params["horizon_years"],
            "allocation": optimization_result["weights"],
            "metrics": optimization_result["metrics"],
            "sector_allocation": optimization_result["sector_allocation"],
            "base_explanation": optimization_result["explanation"]
        }
        
        prompt = f"""You are explaining a portfolio recommendation to a client. 

USER QUERY: {user_query}

RECOMMENDATION DETAILS:
- Risk Profile: {params['risk_profile']}
- Investment Horizon: {params['horizon_years']} years
- Expected Annual Return: {optimization_result['metrics']['expected_annual_return']*100:.1f}%
- Annual Volatility: {optimization_result['metrics']['annual_volatility']*100:.1f}%
- Sharpe Ratio: {optimization_result['metrics']['sharpe_ratio']:.2f}

TOP HOLDINGS:
{self._format_top_holdings(optimization_result['weights'])}

SECTOR ALLOCATION:
{self._format_sector_allocation(optimization_result['sector_allocation'])}

BASE EXPLANATION:
{optimization_result['explanation']}

Generate a friendly, personalized explanation that:
1. Directly addresses the user's query
2. Explains the allocation in plain English (no jargon)
3. Highlights why this fits their risk profile and timeline
4. Mentions 2-3 specific stocks and why they're included
5. Keeps a conversational, helpful tone
6. Stays under 300 words

Do NOT include disclaimers (they will be added automatically).
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=CEREBRAS_TEMPERATURE,
            top_p=CEREBRAS_TOP_P,
            max_tokens=1000
        )
        
        enhanced_explanation = response.choices[0].message.content.strip()
        
        return enhanced_explanation
    
    def _format_top_holdings(self, weights: Dict[str, float], top_n: int = 5) -> str:
        """Format top holdings for display"""
        sorted_holdings = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        lines = []
        for ticker, weight in sorted_holdings:
            sector = self.optimizer.sector_mapping.get(ticker, "Unknown")
            lines.append(f"  - {ticker} ({sector}): {weight*100:.1f}%")
        
        return "\n".join(lines)
    
    def _format_sector_allocation(self, sector_allocation: Dict[str, float]) -> str:
        """Format sector allocation for display"""
        sorted_sectors = sorted(sector_allocation.items(), key=lambda x: x[1], reverse=True)
        
        lines = []
        for sector, weight in sorted_sectors:
            lines.append(f"  - {sector}: {weight*100:.1f}%")
        
        return "\n".join(lines)
    
    def chat(self, user_message: str, chat_history: List[Dict]) -> str:
        """
        Simple chat interface for conversational interaction
        
        Args:
            user_message: User's message
            chat_history: Previous messages
            
        Returns:
            Agent's response
        """
        # Check if this is a portfolio recommendation request
        portfolio_keywords = [
            "recommend", "portfolio", "invest", "allocation", "stocks",
            "risk", "diversify", "optimize", "balance"
        ]
        
        is_portfolio_request = any(kw in user_message.lower() for kw in portfolio_keywords)
        
        if is_portfolio_request:
            # Process as portfolio query
            result = self.process_query(user_message, chat_history)
            
            if result["success"]:
                return result["recommendation"]["explanation"]
            else:
                return result.get("message", "I encountered an error processing your request.")
        else:
            # General conversation
            messages = [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT}
            ] + chat_history + [
                {"role": "user", "content": user_message}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=CEREBRAS_TEMPERATURE,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()


def create_agent() -> CerebrasPortfolioAgent:
    """Convenience function to create agent with default configuration"""
    return CerebrasPortfolioAgent()


if __name__ == "__main__":
    # Test agent
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("CEREBRAS PORTFOLIO AGENT TEST")
    print("=" * 60)
    
    agent = create_agent()
    
    # Test queries
    test_queries = [
        "I'm 30 years old saving for retirement. I can handle some risk. What portfolio do you recommend?",
        "I need a conservative portfolio for my kids' college fund in 5 years.",
        "I want aggressive growth with high risk tolerance for 10+ years."
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {query}")
        print(f"{'='*60}\n")
        
        result = agent.process_query(query)
        
        if result["success"]:
            print("✅ SUCCESS\n")
            print(result["recommendation"]["explanation"])
            print(f"\nAllocation ({len(result['recommendation']['allocation'])} holdings):")
            for ticker, weight in sorted(result['recommendation']['allocation'].items(), 
                                        key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {ticker}: {weight*100:.1f}%")
        else:
            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")
