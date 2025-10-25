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

EXTRACTION_PROMPT_TEMPLATE = """You are an expert financial advisor AI. Extract investment parameters from this user query.

User Query: "{query}"

**CONTEXT**: Our portfolio contains 27 stocks across sectors: IT (AAPL, MSFT, CSCO, DDOG, NOW), Finance (JPM, V), Healthcare (JNJ, UNH), Agriculture (AGCO, BG, CALM), Engineering (CAT, DE, GE), Military Engineering (BA, LMT), Natural Resources (CVX), Food & Beverages (KO), and Pharmaceuticals.

**EXTRACTION RULES**:

1. **Risk Profile** (REQUIRED - default to 'medium' if unclear):
   - LOW: conservative, safe, cautious, low risk, capital preservation
   - MEDIUM: moderate, balanced, medium risk, standard, typical
   - HIGH: aggressive, growth, high risk, maximum returns
   - **Age inference**: 
     * 18-30 years old → medium-high risk
     * 30-50 years old → medium risk  
     * 50+ years old → low-medium risk

2. **Investment Horizon** (REQUIRED - infer from age/context):
   - Explicit years: look for "5 years", "10 year", etc.
   - **Age-based defaults**:
     * Age 20-30 → 15 years (long-term wealth building)
     * Age 30-40 → 12 years (career growth phase)
     * Age 40-50 → 10 years (mid-career)
     * Age 50-60 → 7 years (pre-retirement)
     * Age 60+ → 5 years (retirement)
   - Life events: retirement (15y), house (5-7y), college (10y)
   - DEFAULT: 10 years if nothing specified

3. **Sector Preferences** (OPTIONAL):
   - Only include if user explicitly mentions sectors
   - Available: IT, Finance, Healthcare, Agriculture, Engineering, Military Engineering, Natural Resources, Food & Beverages, Pharmaceuticals

4. **Constraints** (OPTIONAL):
   - Specific stocks to exclude/include
   - Ethical considerations (ESG, etc.)

**EXAMPLES**:
- "hi im 30 with medium risk tolerance" → {{"risk_profile": "medium", "horizon_years": 12}}
- "im 20, moderate risk" → {{"risk_profile": "medium", "horizon_years": 15}}
- "conservative portfolio, 5 years" → {{"risk_profile": "low", "horizon_years": 5}}
- "aggressive growth" → {{"risk_profile": "high", "horizon_years": 10}}

**OUTPUT FORMAT** (ONLY return valid JSON, no explanations):
{{
  "risk_profile": "low|medium|high",
  "horizon_years": <integer between 1-30>,
  "sector_preferences": [],
  "constraints": {{}},
  "confidence": <0.0-1.0>,
  "reasoning": "<one sentence explaining what you extracted>"
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
