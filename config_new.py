"""
Configuration for F2 Portfolio Recommender Agent (Restructured)
Centralized settings for Cerebras API and dataset-based analysis
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ========== Project Paths ==========
PROJECT_ROOT = Path(__file__).parent
DATASETS_DIR = PROJECT_ROOT / "datasets"

# Dataset files
PORTFOLIO_CSV = DATASETS_DIR / "Portfolio.csv"
PORTFOLIO_PRICES_CSV = DATASETS_DIR / "Portfolio_prices.csv"
SP500_CSV = DATASETS_DIR / "SP500.csv"
NASDAQ_CSV = DATASETS_DIR / "NASDAQ .csv"
DOW_JONES_CSV = DATASETS_DIR / "Dow_Jones.csv"

# ========== Cerebras API Configuration ==========
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "csk-3pdf28w2dmhpx3vxjkjw5ydpwrf4kj5p6tkj9dcyp443m2wr")
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "llama3.1-70b")
CEREBRAS_TEMPERATURE = float(os.getenv("CEREBRAS_TEMPERATURE", "0.7"))
CEREBRAS_TOP_P = float(os.getenv("CEREBRAS_TOP_P", "0.8"))
CEREBRAS_MAX_TOKENS = int(os.getenv("CEREBRAS_MAX_TOKENS", "20000"))

# ========== Portfolio Analysis Configuration ==========
# Analysis will be based on actual portfolio data from CSV files
LOOKBACK_PERIOD_DAYS = 252  # 1 year of trading days
RISK_FREE_RATE = 0.04  # 4% annual risk-free rate

# Risk profile mappings (based on actual portfolio data)
RISK_PROFILES = {
    "low": {
        "target_volatility": 0.15,  # 15% annual volatility
        "max_sector_weight": 0.25,  # Max 25% in any sector
        "min_diversification": 8,    # At least 8 different holdings
        "preferred_sectors": ["Healthcare", "Food & Beverages", "IT"]
    },
    "medium": {
        "target_volatility": 0.22,  # 22% annual volatility
        "max_sector_weight": 0.35,  # Max 35% in any sector
        "min_diversification": 6,    # At least 6 different holdings
        "preferred_sectors": ["Finance", "Engineering", "IT", "Natural Resources"]
    },
    "high": {
        "target_volatility": 0.35,  # 35% annual volatility
        "max_sector_weight": 0.50,  # Max 50% in any sector
        "min_diversification": 4,    # At least 4 different holdings
        "preferred_sectors": ["Military Engineering", "Pharmaceuticals", "Agriculture"]
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

# ========== Agent System Prompts (Cerebras-Optimized) ==========
AGENT_SYSTEM_PROMPT = """You are an autonomous Portfolio Recommender Agent specializing in personalized investment portfolio optimization.

**Your Core Capabilities:**
1. Analyze user risk profile (low/medium/high) and investment horizon (years)
2. Use quantitative portfolio optimization tools with REAL historical data
3. Provide clear, jargon-free explanations of recommendations
4. Maintain strict compliance with safety guardrails

**Data Source:**
You have access to a real portfolio containing stocks from multiple sectors:
- IT (AAPL, MSFT, CSCO, DDOG)
- Finance (JPM, MS, IBKR, MSCI)
- Healthcare (HUM, PFE)
- Military Engineering (BA, LMT)
- Agriculture (AGCO, BG, CALM, DE, GRWG)
- Engineering (CAT, IEX)
- Natural Resources (CVX)
- Food & Beverages (KO)
- Pharmaceuticals (ADAP)

**Your Workflow:**
1. Understand user's risk tolerance and investment timeline
2. Call the portfolio_optimizer tool with appropriate parameters
3. Explain recommendations in plain English
4. Always include mandatory disclaimers

**Safety First:**
- Never make up data or recommendations without tool support
- Always validate user inputs for PII
- Include disclaimers in all outputs
- Provide transparency in your reasoning

**Output Format:**
1. Portfolio Allocation (JSON): ticker-to-weight mapping
2. Plain English Explanation: risk rationale, diversification logic, sector allocation
3. Performance Metrics: expected return, volatility, Sharpe ratio
4. Disclaimer: mandatory regulatory notice"""

EXTRACTION_PROMPT_TEMPLATE = """Analyze this user query and extract investment parameters:

User Query: "{query}"

Extract:
1. **Risk Profile**: Classify as 'low', 'medium', or 'high'
   - Keywords: conservative/safe/cautious → low
   - Keywords: balanced/moderate/medium → medium  
   - Keywords: aggressive/growth/high → high
   - Age-based inference: 
     * Young (18-30) → typically medium-high risk tolerance
     * Mid-career (30-50) → typically medium risk tolerance
     * Near retirement (50+) → typically low-medium risk tolerance

2. **Horizon (Years)**: Extract investment timeline
   - Look for explicit years or time periods
   - Age-based inference if mentioned:
     * Age 18-25 → assume 15-20 years for long-term goals
     * Age 25-35 → assume 10-15 years
     * Age 35-50 → assume 8-12 years
     * Age 50+ → assume 5-10 years
   - Map life events: retirement (assume 15y), house (5-7y), education (10-15y)
   - Default: 10 years if young age mentioned, 5 years otherwise

3. **Sector Preferences** (optional): Any specific industry interests
   - Available sectors: IT, Finance, Healthcare, Agriculture, Engineering, Military Engineering, Natural Resources, Food & Beverages, Pharmaceuticals

4. **Constraints** (optional): Any specific requirements

**IMPORTANT**: Even if the query is brief (e.g., "im 20, moderate risk"), extract what you can:
- If age is mentioned, infer a reasonable horizon
- If risk level is mentioned, use it directly
- Always return valid JSON even for minimal input

Return ONLY valid JSON:
{{
  "risk_profile": "low|medium|high",
  "horizon_years": <integer>,
  "sector_preferences": [<list of sectors or empty>],
  "constraints": {{}},
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation of what was extracted>"
}}"""

# ========== Streamlit Configuration ==========
STREAMLIT_CONFIG = {
    "page_title": "F2 Portfolio Recommender",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Color scheme for visualizations
COLOR_SCHEME = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff9900",
    "info": "#17a2b8",
    "sectors": {
        "IT": "#3498db",
        "Finance": "#2ecc71",
        "Healthcare": "#e74c3c",
        "Military Engineering": "#95a5a6",
        "Agriculture": "#f39c12",
        "Engineering": "#9b59b6",
        "Natural Resources": "#1abc9c",
        "Food & Beverages": "#e67e22",
        "Pharmaceuticals": "#34495e"
    }
}

# ========== Evaluation Metrics ==========
EVALUATION_METRICS = [
    "tool_selection_accuracy",
    "argument_correctness",
    "output_format_validity",
    "explanation_quality",
    "guardrail_compliance",
    "reasoning_coherence"
]
