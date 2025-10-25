"""
Configuration for F2 Portfolio Recommender Agent
Centralizes settings for reproducibility and easy customization
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

# ========== LLM Configuration ==========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

# ========== Portfolio Configuration ==========
# Sample Indian and Global stocks for demo
STOCK_UNIVERSE = {
    "conservative": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS"],
    "moderate": ["RELIANCE.NS", "TCS.NS", "TATAMOTORS.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS"],
    "aggressive": ["ZOMATO.NS", "ADANIENT.NS", "TATAMOTORS.NS", "BAJFINANCE.NS", "PAYTM.NS", "NYKAA.NS"]
}

# Risk profile mappings
RISK_PROFILES = {
    "low": {
        "target_return": 0.10,  # 10% annual return
        "max_volatility": 0.15,
        "stock_set": "conservative"
    },
    "medium": {
        "target_return": 0.15,  # 15% annual return
        "max_volatility": 0.25,
        "stock_set": "moderate"
    },
    "high": {
        "target_return": 0.25,  # 25% annual return
        "max_volatility": 0.40,
        "stock_set": "aggressive"
    }
}

# Time horizon adjustments (years)
HORIZON_ADJUSTMENTS = {
    "short": (0, 3),      # 0-3 years: more conservative
    "medium": (3, 7),     # 3-7 years: balanced
    "long": (7, float('inf'))  # 7+ years: can be more aggressive
}

# ========== Guardrails Configuration ==========
PII_PATTERNS = [
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',  # Credit card
    r'\b[A-Z]{5}\d{4}[A-Z]\b',  # PAN card (India)
    r'\b\d{12}\b',  # Aadhaar (India)
]

MANDATORY_DISCLAIMER = (
    "⚠️ DISCLAIMER: This is an AI-generated portfolio recommendation for "
    "demonstration purposes only and is NOT financial advice. Please consult "
    "a registered financial advisor before making investment decisions. "
    "Past performance does not guarantee future results. Investments are subject to market risks."
)

# ========== Evaluation Metrics ==========
EVALUATION_METRICS = [
    "tool_selection_accuracy",
    "argument_correctness",
    "output_format_validity",
    "explanation_quality",
    "guardrail_compliance",
    "reasoning_coherence"
]

# ========== Agent System Prompts ==========
AGENT_SYSTEM_PROMPT = """You are an autonomous Portfolio Recommender Agent specializing in personalized investment portfolio optimization for Indian and global retail investors.

**Your Core Capabilities:**
1. Analyze user risk profile (low/medium/high) and investment horizon (years)
2. Use quantitative portfolio optimization tools to generate optimal asset allocations
3. Provide clear, jargon-free explanations of recommendations
4. Maintain strict compliance with safety guardrails

**Operational Guidelines:**
- Always reason step-by-step: understand user context → select appropriate tools → validate outputs → explain clearly
- Use the portfolio_optimizer tool for all quantitative calculations
- Never make up financial data or recommendations without tool support
- Always include mandatory disclaimers in user-facing output
- Detect and reject any requests containing PII (personal identifiable information)
- Output both machine-readable JSON and human-readable explanations

**Compliance & Safety:**
- You are demonstrating agentic AI capabilities for educational/hackathon purposes
- All recommendations must include clear disclaimers
- Refuse requests that violate regulatory guidelines or contain sensitive personal data

**Response Format:**
1. Portfolio Allocation (JSON): ticker-to-weight mapping
2. Plain English Explanation: risk rationale, diversification logic, horizon alignment
3. Disclaimer: mandatory regulatory notice

Remember: Transparency, explainability, and user trust are paramount in financial AI applications."""

TOOL_SELECTION_PROMPT = """Given the user query, determine which tool(s) to use and with what arguments.

Available Tools:
- portfolio_optimizer: Optimizes portfolio allocation based on risk profile and horizon
  Arguments: risk_profile (str: 'low'/'medium'/'high'), horizon_years (int), constraints (dict, optional)

Selection Logic:
- If user mentions risk tolerance or investment timeline → portfolio_optimizer
- If user asks for explanation of existing portfolio → explanation_generator
- If unclear → ask clarifying questions

Output the tool name and arguments as JSON."""

# ========== Testing Configuration ==========
TEST_CASES = [
    {
        "name": "Conservative Long-term Investor",
        "input": "I'm 25 years old, risk-averse, and want to invest for 10 years.",
        "expected_risk": "low",
        "expected_horizon": 10
    },
    {
        "name": "Moderate Short-term Investor",
        "input": "Medium risk tolerance, 3-year investment horizon",
        "expected_risk": "medium",
        "expected_horizon": 3
    },
    {
        "name": "Aggressive Investor",
        "input": "High risk appetite, investing for 5 years for wealth creation",
        "expected_risk": "high",
        "expected_horizon": 5
    },
    {
        "name": "PII Detection Test",
        "input": "My PAN is ABCDE1234F, can you recommend a portfolio?",
        "expected_blocked": True
    }
]
