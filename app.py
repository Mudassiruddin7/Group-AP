"""
Streamlit Frontend for F2 Portfolio Recommender Agent
Interactive UI for portfolio recommendations powered by Cerebras AI
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import logging

from agent_cerebras import CerebrasPortfolioAgent
from data_loader import get_data_loader
from config_new import STREAMLIT_CONFIG, COLOR_SCHEME, RISK_PROFILES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(**STREAMLIT_CONFIG)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = CerebrasPortfolioAgent()
    
if 'data_loader' not in st.session_state:
    st.session_state.data_loader = get_data_loader()
    
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
if 'recommendation' not in st.session_state:
    st.session_state.recommendation = None


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">📊 F2 Portfolio Recommender</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Autonomous AI-Powered Portfolio Optimization with Cerebras</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Mode selection
        app_mode = st.radio(
            "Select Mode",
            ["🤖 AI Chat", "⚡ Quick Recommend", "📈 Portfolio Analysis", "ℹ️ About"],
            index=0
        )
        
        st.divider()
        
        # Data validation
        with st.expander("📊 Data Status"):
            is_valid, issues = st.session_state.data_loader.validate_data()
            
            if is_valid:
                st.success("✅ All data validated")
            else:
                st.warning("⚠️ Data issues detected")
                for issue in issues:
                    st.text(f"- {issue}")
            
            stats = st.session_state.data_loader.get_portfolio_stats()
            st.metric("Total Stocks", stats['total_stocks'])
            st.metric("Sectors", len(stats['sectors']))
        
        st.divider()
        
        # Model info
        with st.expander("🤖 AI Model"):
            st.write(f"**Model:** {st.session_state.agent.model}")
            st.write("**Provider:** Cerebras Cloud")
            st.write("**Status:** Active")
    
    # Main content based on mode
    if app_mode == "🤖 AI Chat":
        show_ai_chat()
    elif app_mode == "⚡ Quick Recommend":
        show_quick_recommend()
    elif app_mode == "📈 Portfolio Analysis":
        show_portfolio_analysis()
    else:
        show_about()


def show_ai_chat():
    """AI Chat interface"""
    st.header("💬 Chat with Portfolio AI")
    st.write("Ask me anything about portfolio recommendations, risk management, or investment strategies!")
    
    # Chat history display
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # User input
    user_input = st.chat_input("Type your investment question here...")
    
    if user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                result = st.session_state.agent.process_query(
                    user_input,
                    st.session_state.chat_history
                )
                
                if result["success"]:
                    response_text = result["recommendation"]["explanation"]
                    st.write(response_text)
                    
                    # Store recommendation for visualization
                    st.session_state.recommendation = result
                    
                    # Show visualizations
                    st.divider()
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        show_allocation_chart(result["recommendation"]["allocation"])
                    
                    with col2:
                        show_sector_chart(result["recommendation"]["sector_allocation"])
                    
                    # Show metrics
                    show_metrics_cards(result["recommendation"]["metrics"])
                    
                else:
                    response_text = result.get("message", "Error processing request")
                    st.error(response_text)
        
        # Add assistant message
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})


def show_quick_recommend():
    """Quick recommendation form"""
    st.header("⚡ Quick Portfolio Recommendation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        risk_profile = st.select_slider(
            "Risk Tolerance",
            options=["low", "medium", "high"],
            value="medium",
            help="How much risk are you willing to take?"
        )
        
        # Show risk profile details
        profile_details = RISK_PROFILES[risk_profile]
        st.info(f"**Target Volatility:** {profile_details['target_volatility']*100:.0f}%  \n"
                f"**Min Holdings:** {profile_details['min_diversification']}")
    
    with col2:
        horizon_years = st.slider(
            "Investment Horizon (Years)",
            min_value=1,
            max_value=30,
            value=5,
            help="How long do you plan to invest?"
        )
        
        if horizon_years <= 3:
            st.warning("⚠️ Short horizon - conservative recommended")
        elif horizon_years >= 10:
            st.success("✅ Long horizon - can handle volatility")
    
    # Sector preferences
    all_sectors = st.session_state.data_loader.get_sector_mapping()
    unique_sectors = sorted(set(all_sectors.values()))
    
    sector_preferences = st.multiselect(
        "Sector Preferences (Optional)",
        options=unique_sectors,
        help="Select specific sectors you're interested in"
    )
    
    # Portfolio value for discrete allocation
    portfolio_value = st.number_input(
        "Total Investment Amount ($)",
        min_value=1000,
        max_value=10000000,
        value=10000,
        step=1000,
        help="Amount you want to invest"
    )
    
    # Generate button
    if st.button("🎯 Generate Recommendation", type="primary", use_container_width=True):
        with st.spinner("🤖 Optimizing your portfolio..."):
            # Create query
            query = f"I have a {risk_profile} risk tolerance and want to invest for {horizon_years} years."
            if sector_preferences:
                query += f" I'm interested in {', '.join(sector_preferences)} sectors."
            
            result = st.session_state.agent.process_query(query)
            
            if result["success"]:
                st.session_state.recommendation = result
                
                st.success("✅ Portfolio optimized successfully!")
                
                # Display results
                st.divider()
                
                # Explanation
                st.markdown("### 📝 Recommendation")
                st.write(result["recommendation"]["explanation"])
                
                # Visualizations
                st.divider()
                col1, col2 = st.columns(2)
                
                with col1:
                    show_allocation_chart(result["recommendation"]["allocation"])
                
                with col2:
                    show_sector_chart(result["recommendation"]["sector_allocation"])
                
                # Metrics
                show_metrics_cards(result["recommendation"]["metrics"])
                
                # Discrete allocation
                st.divider()
                st.markdown("### 💰 Share Allocation")
                
                allocation, leftover = st.session_state.agent.optimizer.discrete_allocation(
                    result["recommendation"]["allocation"],
                    portfolio_value
                )
                
                df_allocation = pd.DataFrame([
                    {
                        "Ticker": ticker,
                        "Shares": shares,
                        "Sector": st.session_state.data_loader.get_sector_mapping()[ticker]
                    }
                    for ticker, shares in allocation.items()
                ])
                
                st.dataframe(df_allocation, use_container_width=True)
                st.info(f"💵 Leftover cash: ${leftover:,.2f}")
                
            else:
                st.error(f"❌ {result.get('message', 'Optimization failed')}")


def show_portfolio_analysis():
    """Portfolio analysis and data exploration"""
    st.header("📈 Portfolio Analysis")
    
    # Portfolio overview
    stats = st.session_state.data_loader.get_portfolio_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Stocks", stats['total_stocks'])
    
    with col2:
        st.metric("Sectors", len(stats['sectors']))
    
    with col3:
        if stats['total_value']:
            st.metric("Total Value", f"${stats['total_value']:,.2f}")
    
    # Sector distribution
    st.divider()
    st.subheader("📊 Sector Distribution")
    
    sector_df = pd.DataFrame([
        {"Sector": sector, "Count": count}
        for sector, count in stats['sector_distribution'].items()
    ])
    
    fig = px.pie(
        sector_df,
        values='Count',
        names='Sector',
        title='Stocks by Sector',
        color='Sector',
        color_discrete_map=COLOR_SCHEME['sectors']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Stock list
    st.divider()
    st.subheader("📋 Stock Universe")
    
    portfolio_df = st.session_state.data_loader.load_portfolio()
    st.dataframe(portfolio_df, use_container_width=True)
    
    # Historical price analysis
    st.divider()
    st.subheader("📈 Historical Price Analysis")
    
    selected_tickers = st.multiselect(
        "Select stocks to analyze",
        options=st.session_state.data_loader.get_stock_universe(),
        default=st.session_state.data_loader.get_stock_universe()[:5]
    )
    
    if selected_tickers:
        lookback = st.slider("Lookback period (days)", 30, 365, 252)
        
        prices = st.session_state.data_loader.get_historical_prices(
            tickers=selected_tickers,
            lookback_days=lookback
        )
        
        # Normalize prices
        normalized = prices / prices.iloc[0] * 100
        
        fig = go.Figure()
        
        for ticker in selected_tickers:
            fig.add_trace(go.Scatter(
                x=normalized.index,
                y=normalized[ticker],
                mode='lines',
                name=ticker
            ))
        
        fig.update_layout(
            title='Normalized Price Performance (Base 100)',
            xaxis_title='Date',
            yaxis_title='Normalized Price',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Returns statistics
        returns = st.session_state.data_loader.get_returns(
            tickers=selected_tickers,
            lookback_days=lookback
        )
        
        st.subheader("📊 Return Statistics")
        stats_df = returns.describe().T
        stats_df['annualized_return'] = returns.mean() * 252
        stats_df['annualized_volatility'] = returns.std() * (252 ** 0.5)
        
        st.dataframe(stats_df, use_container_width=True)


def show_about():
    """About page"""
    st.header("ℹ️ About F2 Portfolio Recommender")
    
    st.markdown("""
    ### 🎯 What is This?
    
    The **F2 Portfolio Recommender** is an autonomous AI agent that provides personalized 
    investment portfolio recommendations using cutting-edge technology:
    
    - 🤖 **Cerebras AI**: Powered by Llama 3.1 70B for intelligent reasoning
    - 📊 **PyPortfolioOpt**: Quantitative optimization based on Modern Portfolio Theory
    - 🛡️ **Safety Guardrails**: PII detection and mandatory disclaimers
    - 📈 **Real Data**: Uses actual historical price data from your portfolio
    
    ### 🏗️ Architecture
    
    The system follows a 5-layer agentic architecture:
    
    1. **Input Guardrails**: Validates user input for safety
    2. **Agentic Reasoning**: Cerebras AI extracts investment parameters
    3. **Quantitative Optimization**: PyPortfolioOpt generates optimal allocations
    4. **Explanation Generation**: AI creates personalized explanations
    5. **Output Guardrails**: Ensures compliance and disclaimers
    
    ### 🔒 Safety Features
    
    - PII detection (SSN, credit cards, etc.)
    - Mandatory regulatory disclaimers
    - Input validation and sanitization
    - No storage of personal information
    
    ### 📊 Data Sources
    
    - **Portfolio Data**: Real holdings from Portfolio.csv
    - **Historical Prices**: 35,000+ daily records from Portfolio_prices.csv
    - **Sectors**: IT, Finance, Healthcare, Agriculture, and more
    
    ### ⚠️ Important Disclaimer
    
    This application is for **demonstration and educational purposes only**. 
    It is **NOT financial advice**. Always consult with a registered financial 
    advisor before making investment decisions.
    
    ### 🛠️ Technology Stack
    
    - **Frontend**: Streamlit
    - **AI Model**: Cerebras Cloud SDK (Llama 3.1 70B)
    - **Optimization**: PyPortfolioOpt, pandas, numpy
    - **Visualization**: Plotly
    - **Data**: CSV-based historical data
    
    ### 📝 Version
    
    **Version**: 1.0.0 (Restructured)  
    **Last Updated**: {datetime.now().strftime("%Y-%m-%d")}  
    **Model**: llama3.1-70b via Cerebras
    
    ---
    
    💡 **Tip**: Try the AI Chat mode for the most interactive experience!
    """)


# Visualization helpers
def show_allocation_chart(allocation: dict):
    """Display allocation pie chart"""
    df = pd.DataFrame([
        {"Ticker": ticker, "Weight": weight * 100}
        for ticker, weight in allocation.items()
    ]).sort_values("Weight", ascending=False)
    
    fig = px.pie(
        df,
        values='Weight',
        names='Ticker',
        title='Portfolio Allocation (%)',
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig, use_container_width=True)


def show_sector_chart(sector_allocation: dict):
    """Display sector allocation bar chart"""
    df = pd.DataFrame([
        {"Sector": sector, "Weight": weight * 100}
        for sector, weight in sector_allocation.items()
    ]).sort_values("Weight", ascending=True)
    
    fig = px.bar(
        df,
        y='Sector',
        x='Weight',
        orientation='h',
        title='Sector Allocation (%)',
        color='Sector',
        color_discrete_map=COLOR_SCHEME['sectors']
    )
    
    fig.update_layout(showlegend=False)
    
    st.plotly_chart(fig, use_container_width=True)


def show_metrics_cards(metrics: dict):
    """Display performance metrics"""
    st.markdown("### 📊 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Expected Return",
            f"{metrics['expected_annual_return']*100:.2f}%",
            help="Annualized expected return"
        )
    
    with col2:
        st.metric(
            "Volatility",
            f"{metrics['annual_volatility']*100:.2f}%",
            help="Annualized standard deviation (risk)"
        )
    
    with col3:
        st.metric(
            "Sharpe Ratio",
            f"{metrics['sharpe_ratio']:.2f}",
            help="Risk-adjusted return metric"
        )
    
    with col4:
        st.metric(
            "Holdings",
            metrics['diversification'],
            help="Number of stocks in portfolio"
        )


if __name__ == "__main__":
    main()
