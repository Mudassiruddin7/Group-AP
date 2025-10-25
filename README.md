# 🤖 F2 Portfolio Recommender Agent

**Autonomous AI-Powered Portfolio Optimization with Cerebras Cloud SDK**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![AI](https://img.shields.io/badge/AI-Cerebras%20Llama%203.1%2070B-purple)

---

## 🎯 Overview

The **F2 Portfolio Recommender Agent** is a cutting-edge autonomous financial AI system that provides personalized investment portfolio recommendations by combining:

- 🧠 **Agentic AI** (Cerebras Llama 3.1 70B) for intelligent reasoning
- 📊 **Quantitative Optimization** (PyPortfolioOpt) based on Modern Portfolio Theory
- 🛡️ **Safety Guardrails** for PII detection and compliance
- 📈 **Real Historical Data** from CSV files (35,000+ price records)
- 🎨 **Interactive Streamlit Frontend** for impactful user experience

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   STREAMLIT FRONTEND                    │
│         (Interactive UI with Visualizations)            │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              LAYER 1: INPUT GUARDRAILS                  │
│         (PII Detection, Input Validation)               │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│           LAYER 2: AGENTIC REASONING                    │
│    (Cerebras Llama 3.1 70B - Parameter Extraction)      │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│        LAYER 3: QUANTITATIVE OPTIMIZATION               │
│     (PyPortfolioOpt + CSV Historical Data)              │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│         LAYER 4: EXPLANATION GENERATION                 │
│    (Cerebras AI - Personalized Natural Language)        │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│            LAYER 5: OUTPUT GUARDRAILS                   │
│        (Disclaimer Enforcement, Compliance)             │
└─────────────────────────────────────────────────────────┘
```

## ✨ Key Features

### 🤖 AI-Powered Intelligence
- **Cerebras Cloud SDK** with Llama 3.1 70B
- Natural language understanding of investment goals
- Conversational interface for portfolio recommendations
- Personalized explanations tailored to user queries

### 📊 Quantitative Excellence
- **PyPortfolioOpt** for Modern Portfolio Theory optimization
- Multiple optimization strategies (Min Volatility, Max Sharpe, Efficient Return)
- Sector constraints and diversification requirements
- Discrete allocation (exact share quantities)

### 🎨 Interactive Frontend
- **Streamlit** web application with 3 modes:
  - 🤖 **AI Chat**: Conversational portfolio recommendations
  - ⚡ **Quick Recommend**: Form-based interface
  - 📈 **Portfolio Analysis**: Data exploration and visualization
- Real-time Plotly charts and metrics
- Responsive, user-friendly design

### 🛡️ Safety & Compliance
- PII detection (SSN, credit cards, etc.)
- Mandatory regulatory disclaimers
- Input/output validation
- Transparent reasoning

### 📁 Real Data Integration
- CSV-based portfolio data (29 stocks)
- 35,000+ historical price records (2020-2025)
- Multiple sectors: IT, Finance, Healthcare, Agriculture, etc.
- Market indices: S&P 500, NASDAQ, Dow Jones

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Cerebras API key (provided in `.env`)

### Installation

1. **Clone or download the project**
   ```bash
   cd c:\Users\mohdm\Downloads\AP
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify .env file exists**
   The `.env` file should contain:
   ```
   CEREBRAS_API_KEY=csk-3pdf28w2dmhpx3vxjkjw5ydpwrf4kj5p6tkj9dcyp443m2wr
   CEREBRAS_MODEL=llama3.1-70b
   ```

4. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**
   Navigate to `http://localhost:8501`

## 📂 Project Structure

```
AP/
├── 🎨 FRONTEND
│   └── app.py                      # Streamlit web application
│
├── 🤖 AI AGENT
│   └── agent_cerebras.py           # Cerebras-powered agentic orchestration
│
├── 📊 OPTIMIZATION ENGINE
│   ├── portfolio_optimizer_csv.py  # CSV-based portfolio optimization
│   └── data_loader.py              # CSV data loading utilities
│
├── ⚙️ CONFIGURATION
│   ├── config_new.py               # Main configuration (CSV-based)
│   ├── .env                        # Environment variables
│   └── .env.example                # Template for environment setup
│
├── 🛡️ SAFETY
│   └── guardrails.py               # Input/output safety guardrails
│
├── 📈 DATA
│   └── datasets/
│       ├── Portfolio.csv           # Portfolio holdings (29 stocks)
│       ├── Portfolio_prices.csv    # Historical prices (35K+ records)
│       ├── SP500.csv
│       ├── NASDAQ .csv
│       └── Dow_Jones.csv
│
├── 📦 DEPENDENCIES
│   └── requirements.txt            # Python packages
│
└── 📚 DOCUMENTATION
    ├── README.md                   # This file
    └── ARCHITECTURE.md             # System architecture
```

## 🎮 Usage Modes

### 1. 🤖 AI Chat Mode
**Best for**: Natural conversation and personalized recommendations

```
Example Queries:
- "I'm 30 years old saving for retirement. I can handle some risk."
- "I need a conservative portfolio for my kids' college fund in 5 years."
- "I want aggressive growth with high risk tolerance for 10+ years."
```

**Features**:
- Full conversational AI
- Real-time portfolio optimization
- Interactive visualizations
- Chat history tracking

### 2. ⚡ Quick Recommend Mode
**Best for**: Fast recommendations with simple inputs

**Inputs**:
- Risk tolerance (low/medium/high slider)
- Investment horizon (1-30 years)
- Sector preferences (optional)
- Total investment amount

**Outputs**:
- Optimized portfolio allocation
- Performance metrics
- Sector distribution
- Discrete share allocation

### 3. 📈 Portfolio Analysis Mode
**Best for**: Data exploration and research

**Features**:
- Portfolio statistics
- Sector distribution pie chart
- Stock universe table
- Historical price charts (normalized)
- Return statistics

## 📊 Understanding Outputs

### Allocation
- **Format**: Ticker → Weight (%)
- **Example**: AAPL: 12.5%, JPM: 8.3%, etc.
- **Visualization**: Pie chart

### Performance Metrics

| Metric | Description | Good Values |
|--------|-------------|-------------|
| **Expected Return** | Annualized projected return | 8-15% |
| **Volatility** | Annual standard deviation (risk) | 15-25% (medium risk) |
| **Sharpe Ratio** | Risk-adjusted return | >1.0 is good, >2.0 is excellent |
| **Holdings** | Number of stocks | 6-15 for diversification |

### Sector Allocation
- Distribution across sectors (IT, Finance, Healthcare, etc.)
- Ensures diversification
- Respects risk profile constraints

### Discrete Allocation
- **Input**: Total investment amount (e.g., $10,000)
- **Output**: Exact shares to buy for each stock
- **Leftover**: Uninvested cash displayed

## 🔧 Configuration

### Risk Profiles (`config_new.py`)

| Risk | Target Volatility | Max Sector Weight | Min Holdings |
|------|------------------|-------------------|--------------|
| **Low** | 15% | 25% | 8 |
| **Medium** | 22% | 35% | 6 |
| **High** | 35% | 50% | 4 |

### Cerebras Models

- **llama3.1-70b** (default): Best balance of performance and speed
- **qwen-3-235b-a22b-instruct-2507**: More capable, slower

Edit `.env` to change model:
```
CEREBRAS_MODEL=qwen-3-235b-a22b-instruct-2507
```

## 🧪 Testing Components

### Test Data Loader
```bash
python data_loader.py
```
**Expected Output**:
- ✅ Data validation passed
- Portfolio statistics (29 stocks, sectors)
- Sample historical data

### Test Portfolio Optimizer
```bash
python portfolio_optimizer_csv.py
```
**Expected Output**:
- Optimizations for low/medium/high risk
- Top 10 holdings for each profile
- Performance metrics

### Test Cerebras Agent
```bash
python agent_cerebras.py
```
**Expected Output**:
- 3 test queries processed
- Full recommendations with explanations
- Allocation and metrics

## 🚨 Important Disclaimer

⚠️ **THIS APPLICATION IS FOR DEMONSTRATION AND EDUCATIONAL PURPOSES ONLY.**

This is **NOT financial advice**. The portfolio recommendations generated by this system are based on historical data and mathematical models, which cannot predict future market performance.

**Before making ANY investment decisions**:
1. Consult with a registered financial advisor
2. Conduct your own research
3. Understand the risks involved
4. Consider your personal financial situation

**Regulatory Notice**: This application:
- Does NOT provide investment advice
- Does NOT manage client funds
- Does NOT guarantee returns
- Is NOT regulated by SEC or FINRA

## 📚 Technical Details

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **AI Model** | Cerebras Llama 3.1 70B |
| **Frontend** | Streamlit 1.32+ |
| **Optimization** | PyPortfolioOpt 1.5+ |
| **Data Processing** | pandas 2.2+, numpy 1.26+ |
| **Visualization** | Plotly 5.18+, matplotlib 3.8+ |
| **Safety** | guardrails-ai 0.4+ |
| **API Client** | cerebras-cloud-sdk 1.0+ |

### Data Sources

**Portfolio.csv** (29 stocks):
- Tickers: AAPL, BA, CAT, JPM, MSFT, etc.
- Sectors: IT, Finance, Healthcare, Agriculture, etc.
- Quantities, prices, weights

**Portfolio_prices.csv** (35,399 records):
- Date range: 2020-01-03 to present
- OHLCV data (Open, High, Low, Close, Adjusted, Volume)
- Daily returns calculated

### Optimization Methods

1. **Low Risk**: Minimize volatility
2. **Medium Risk**: Maximize Sharpe ratio (risk-adjusted return)
3. **High Risk**: Maximize returns with volatility constraint

**Constraints**:
- Sector weight limits (based on risk profile)
- Minimum position size (1% per stock)
- Diversification requirements

## 🛠️ Troubleshooting

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

### Cerebras API Errors
- Check API key in `.env`
- Verify API credits at cerebras.ai
- Try alternative model (qwen-3-235b-a22b-instruct-2507)

### Data Validation Failed
```bash
python data_loader.py
```
Check for missing CSV files or corrupted data

### Streamlit Won't Start
```bash
streamlit cache clear
streamlit run app.py
```

## 🚀 Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to streamlit.io
3. Add Cerebras API key to secrets
4. Deploy

### Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### AWS/Azure/GCP
- Use container services (ECS, AKS, Cloud Run)
- Set environment variables
- Configure load balancer

## 🔮 Future Enhancements

### Potential Features
- [ ] Multi-objective optimization (ESG scores, dividends)
- [ ] Backtesting engine
- [ ] Monte Carlo simulations
- [ ] Portfolio rebalancing alerts
- [ ] Tax-loss harvesting suggestions
- [ ] Integration with brokerage APIs
- [ ] Multi-user support with authentication
- [ ] Real-time market data updates

### Advanced AI Features
- [ ] Fine-tuned models on financial data
- [ ] Multi-agent reasoning (debate/consensus)
- [ ] Retrieval-Augmented Generation (RAG) for financial news
- [ ] Sentiment analysis integration

## 📝 License

MIT License - See LICENSE file for details

---

**Built with** ❤️ **using Cerebras, Streamlit, and PyPortfolioOpt**

**Version**: 1.0.0  
**Last Updated**: 2025  
**Model**: Cerebras Llama 3.1 70B
