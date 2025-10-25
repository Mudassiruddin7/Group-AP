# F2 Portfolio Recommender Agent - System Architecture

## Overview
AI-powered portfolio optimization system using Cerebras Llama 3.1 70B, PyPortfolioOpt, and Streamlit.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND (app.py)                          │
│                     3 Interactive Modes                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  🤖 AI Chat Mode    ⚡ Quick Recommend    📈 Portfolio Analysis         │
│  • Conversational   • Form-based UI      • Data exploration            │
│  • Real-time viz    • Risk sliders       • Historical charts           │
│  • Chat history     • Sector selection   • Statistics                  │
│                                                                         │
│  User Query: "I'm 30, moderate risk, investing for 7 years"             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   LAYER 1: INPUT GUARDRAILS                             │
│                      (guardrails.py)                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐      │
│  │  PII Detection  │  │ Input Validation │  │ Safety Checks      │      │
│  │  • SSN          │  │ • Length Check   │  │ • Malicious Pattern│      │
│  │  • Credit Cards │  │ • Format Check   │  │ • Compliance Rules │      │
│  │  • PAN/Aadhaar  │  │ • Sanitization   │  │ • Audit Logging    │      │
│  └─────────────────┘  └──────────────────┘  └────────────────────┘      │
│                                                                         │
│  Result: ✅ SAFE or ❌ BLOCKED                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   LAYER 2: AGENTIC REASONING                            │
│                    (agent_cerebras.py)                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │         Cerebras Llama 3.1 70B Agent                           │     │
│  │                                                                │     │
│  │  Step 1: UNDERSTAND (Parameter Extraction)                     │     │
│  │  ┌─────────────────────────────────────────┐                   │     │
│  │  │ LLM Call: Extract Parameters            │                   │     │
│  │  │ • Risk Profile: "medium"                │                   │     │
│  │  │ • Horizon: 7 years                      │                   │     │
│  │  │ • Sector Preferences: []                │                   │     │
│  │  │ • Confidence: 0.95                      │                   │     │
│  │  └─────────────────────────────────────────┘                   │     │
│  │                      │                                         │     │
│  │                      ▼                                         │     │
│  │  Step 2: OPTIMIZE                                              │     │
│  │  ┌─────────────────────────────────────────┐                   │     │
│  │  │ Call Portfolio Optimizer Tool           │                   │     │
│  │  │ → CSVPortfolioOptimizer                 │                   │     │
│  │  │   (risk: medium, horizon: 7)            │                   │     │
│  │  └─────────────────────────────────────────┘                   │     │
│  │                      │                                         │     │
│  │                      ▼                                         │     │
│  │  Step 3: EXPLAIN (Natural Language Generation)                 │     │
│  │  ┌─────────────────────────────────────────┐                   │     │
│  │  │ LLM Call: Generate Explanation          │                   │     │
│  │  │ • Personalized to user query            │                   │     │
│  │  │ • Plain English reasoning               │                   │     │
│  │  │ • Contextual recommendations            │                   │     │
│  │  └─────────────────────────────────────────┘                   │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              LAYER 3: QUANTITATIVE OPTIMIZATION                         │
│              (portfolio_optimizer_csv.py + data_loader.py)              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐                                                   │
│  │ Stock Universe   │                                                   │
│  │ from CSV         │  ──────┐                                          │
│  │ • Medium Risk    │        │                                          │
│  │ → 29 US stocks   │        │                                          │
│  └──────────────────┘        │                                          │
│                               ▼                                         │
│                      ┌─────────────────┐                                │
│  ┌──────────────────┐│ Historical Data │┌────────────────────┐          │
│  │ Risk Adjustment  ││  (CSV Files)    ││ Expected Returns   │          │
│  │ • Horizon: 7y    ││ • Portfolio.csv ││ Mean Historical μ  │          │
│  │ • Factor: 1.08x  ││ • 35K+ records  ││ 252-day lookback   │          │
│  └──────────────────┘│ • OHLCV data    │└────────────────────┘          │
│                      └─────────────────┘                                │
│                               │                                         │
│                               ▼                                         │
│                ┌──────────────────────────────┐                         │
│                │   PyPortfolioOpt Engine      │                         │
│                │                              │                         │
│                │  Strategy by Risk Profile:   │                         │
│                │  • LOW: Minimize Volatility  │                         │
│                │  • MEDIUM: Max Sharpe Ratio  │                         │
│                │  • HIGH: Max Returns         │                         │
│                │                              │                         │
│                │  Constraints:                │                         │
│                │  • Sector limits (25-50%)    │                         │
│                │  • Min position: 1%          │                         │
│                │  • Diversification (4-8)     │                         │
│                └──────────────────────────────┘                         │
│                               │                                         │
│                               ▼                                         │
│                ┌──────────────────────────────┐                         │
│                │   Portfolio Weights          │                         │
│                │   {AAPL: 0.15,               │                         │
│                │    JPM: 0.12,                │                         │
│                │    MSFT: 0.10, ...}          │                         │
│                └──────────────────────────────┘                         │
│                               │                                         │
│                               ▼                                         │
│                ┌──────────────────────────────┐                         │
│                │  Performance Metrics         │                         │
│                │  • Expected Return: 12.5%    │                         │
│                │  • Volatility: 18.2%         │                         │
│                │  • Sharpe Ratio: 2.1         │                         │
│                └──────────────────────────────┘                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 LAYER 4: EXPLANATION GENERATION                         │
│                    (agent_cerebras.py)                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │ Cerebras LLM - Personalized Explanation                   │         │
│  │                                                            │         │
│  │ Input: Portfolio weights + metrics + user context         │         │
│  │                                                            │         │
│  │ Output:                                                    │         │
│  │ "Based on your medium risk profile and 7-year horizon,    │         │
│  │  here's your optimized portfolio: Expected return 12.5%,   │         │
│  │  volatility 18.2%. Diversified across IT (AAPL, MSFT),     │         │
│  │  Finance (JPM, MS), and other sectors..."                 │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  LAYER 5: OUTPUT GUARDRAILS                             │
│                      (guardrails.py)                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐  ┌────────────────────┐  ┌─────────────────┐      │
│  │ Weight Validation│  │ Metrics Validation │  │ Disclaimer      │      │
│  │ • Sum ≈ 1.0      │  │ • Return: -50%-150%│  │ Enforcement     │      │
│  │ • No negatives   │  │ • Vol: 0%-200%     │  │ "Not financial  │      │
│  │ • Min/Max bounds │  │ • Sharpe: realistic│  │  advice..."     │      │
│  └──────────────────┘  └────────────────────┘  └─────────────────┘      │
│                                                                         │
│  Result: ✅ VALIDATED Response                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      FINAL RESPONSE TO USER                             │
│                   (Streamlit Frontend Display)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  📊 Portfolio Allocation (Pie Chart):                                  │
│     AAPL: 15.0%    JPM: 12.0%    MSFT: 10.0%                           │
│     BA: 8.5%       CAT: 7.5%     ... (7 more)                          │
│                                                                         │
│  📈 Expected Performance:                                               │
│     Annual Return: 12.5%    Volatility: 18.2%    Sharpe: 2.1          │
│                                                                         │
│  🎯 Sector Allocation (Bar Chart):                                     │
│     IT: 35%    Finance: 28%    Engineering: 15%    Others: 22%         │
│                                                                         │
│  💡 Explanation: [Personalized natural language explanation...]        │
│                                                                         │
│  ⚠️ DISCLAIMER: This is NOT financial advice...                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                            KEY COMPONENTS
═══════════════════════════════════════════════════════════════════════════

File                         | Purpose                     | Lines | Tech
──────────────────────────────────────────────────────────────────────────
app.py                       | Streamlit frontend          |  550+ | Streamlit, Plotly
agent_cerebras.py            | AI agent orchestration      |  350+ | Cerebras SDK
portfolio_optimizer_csv.py   | Quant optimization          |  380+ | PyPortfolioOpt
data_loader.py               | CSV data utilities          |  250+ | pandas
guardrails.py                | Safety & compliance         |  280+ | regex, validation
config_new.py                | Configuration & settings    |  280+ | Python
──────────────────────────────────────────────────────────────────────────
TOTAL                        |                             | 2800+ |


═══════════════════════════════════════════════════════════════════════════
                         TECHNOLOGY STACK
═══════════════════════════════════════════════════════════════════════════

┌─────────────────┐   ┌──────────────┐   ┌─────────────────┐
│ Cerebras Llama  │───│  Direct API  │───│ Portfolio Agent │
│   3.1 70B       │   │  Calls       │   │  (Coordinator)  │
└─────────────────┘   └──────────────┘   └─────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
         ┌──────────▼────────┐  ┌────────▼─────────┐
         │ PyPortfolioOpt    │  │ Streamlit UI     │
         │ (MPT Optimization)│  │ (3 Modes)        │
         └───────────────────┘  └──────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
  ┌──────▼──────┐      ┌──────▼────────┐
  │  CSV Data   │      │ Guardrails    │
  │ (35K+ rows) │      │  (Safety)     │
  └─────────────┘      └───────────────┘

```

## System Features

### 🤖 AI-Powered Intelligence
- **Cerebras Llama 3.1 70B** for reasoning and explanation
- Natural language parameter extraction
- Personalized portfolio explanations
- Conversational interface

### 📊 Quantitative Excellence  
- **PyPortfolioOpt** for Modern Portfolio Theory
- Multiple optimization strategies (Min Vol, Max Sharpe, Max Return)
- Real historical data (35K+ OHLCV records)
- Sector constraints and diversification

### 🎨 Interactive Frontend
- **Streamlit** web application
- 3 modes: AI Chat, Quick Recommend, Portfolio Analysis
- Real-time Plotly visualizations
- Professional UI/UX

### 🛡️ Safety & Compliance
- Input/output guardrails
- PII detection (SSN, credit cards, etc.)
- Mandatory disclaimers
- Output validation

### 📈 Data Integration
- CSV-based portfolio (29 US stocks)
- 9 sectors (IT, Finance, Healthcare, etc.)
- Historical price data (2020-2025)
- Market indices support

## Performance Metrics

| Metric | Value |
|--------|-------|
| End-to-End Response | 5-10 seconds |
| Parameter Extraction | 1-2 seconds |
| Optimization | 2-4 seconds |
| Explanation Generation | 2-4 seconds |
| Typical Sharpe Ratio | 1.5 - 2.5 |
| Expected Return | 8% - 15% |
| Volatility Range | 15% - 35% |

## Architecture Principles

1. **Multi-Layer Safety**: Input and output guardrails at every step
2. **Agentic Reasoning**: True AI decision-making, not just templates
3. **Quantitative Rigor**: Modern Portfolio Theory implementation
4. **Transparency**: Clear explanations and reasoning
5. **Production-Ready**: Error handling, validation, logging

---

**Built with:** Cerebras, Streamlit, PyPortfolioOpt, pandas  
**Status:** Production Ready  
**Version:** 1.0.0 (Restructured)
