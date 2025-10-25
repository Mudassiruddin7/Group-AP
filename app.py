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
    /* ChatGPT-like styling */
    .stChatMessage {
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stChatMessage[data-testid="user-message"] {
        background-color: #f7f7f8;
    }
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #ffffff;
    }
    /* Better chat input */
    .stChatInput {
        border-radius: 1.5rem;
        border: 1px solid #d9d9e3;
    }
    /* Smooth transitions */
    .stChatMessage, .stButton, .stMetric {
        transition: all 0.2s ease;
    }
    .stButton:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
    
    # Top menu bar with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI Chat", "⚡ Quick Recommend", "📈 Portfolio Analysis", "⚙️ Settings"])
    
    with tab1:
        show_ai_chat()
    
    with tab2:
        show_quick_recommend()
    
    with tab3:
        show_portfolio_analysis()
    
    with tab4:
        show_settings()


def show_ai_chat():
    """AI Chat interface - ChatGPT style"""
    st.header("💬 Chat with F2 Portfolio AI")
    
    # Header controls
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption("Ask about investments, research companies, or get personalized portfolio recommendations")
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.recommendation = None
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
            
            # Show portfolio visualization if it exists in the message
            if message["role"] == "assistant" and message.get("has_portfolio"):
                if st.session_state.recommendation:
                    st.divider()
                    
                    # Compact metrics display
                    metrics = st.session_state.recommendation["recommendation"]["metrics"]
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📈 Return", f"{metrics['expected_annual_return']*100:.1f}%")
                    with col2:
                        st.metric("📊 Volatility", f"{metrics['annual_volatility']*100:.1f}%")
                    with col3:
                        st.metric("⚡ Sharpe", f"{metrics['sharpe_ratio']:.2f}")
                    with col4:
                        st.metric("🎯 Holdings", metrics['diversification'])
                    
                    # Charts in expander to save space
                    with st.expander("📊 View Portfolio Charts", expanded=False):
                        chart_col1, chart_col2 = st.columns(2)
                        
                        with chart_col1:
                            show_allocation_chart(st.session_state.recommendation["recommendation"]["allocation"])
                        
                        with chart_col2:
                            show_sector_chart(st.session_state.recommendation["recommendation"]["sector_allocation"])
    
    # Chat input at the bottom
    user_input = st.chat_input("Ask me anything... e.g., 'hi', 'research Apple stock', or 'I'm 25, moderate risk'")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Display user message immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Get AI response with streaming simulation
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            
            # Show thinking indicator
            message_placeholder.markdown("🤔 *Thinking...*")
            
            # Process query (only send last 10 messages for context efficiency)
            recent_history = st.session_state.chat_history[-10:] if len(st.session_state.chat_history) > 10 else st.session_state.chat_history
            
            result = st.session_state.agent.process_query(
                user_input,
                recent_history
            )
            
            # Determine response type and content
            has_portfolio = False
            
            if result.get("is_chat") or result.get("is_research"):
                # General chat or research response
                response_text = result.get("message", "")
                
            elif result["success"] and result.get("recommendation"):
                # Portfolio recommendation
                response_text = result["recommendation"]["explanation"]
                has_portfolio = True
                st.session_state.recommendation = result
                
            else:
                # Error
                response_text = "❌ " + result.get("message", "I encountered an error. Please try again.")
            
            # Display response with simulated streaming effect
            message_placeholder.markdown(response_text)
            
            # If portfolio recommendation, show metrics
            if has_portfolio:
                st.divider()
                
                metrics = result["recommendation"]["metrics"]
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📈 Return", f"{metrics['expected_annual_return']*100:.1f}%")
                with col2:
                    st.metric("📊 Volatility", f"{metrics['annual_volatility']*100:.1f}%")
                with col3:
                    st.metric("⚡ Sharpe", f"{metrics['sharpe_ratio']:.2f}")
                with col4:
                    st.metric("🎯 Holdings", metrics['diversification'])
                
                with st.expander("📊 View Portfolio Charts", expanded=False):
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        show_allocation_chart(result["recommendation"]["allocation"])
                    
                    with chart_col2:
                        show_sector_chart(result["recommendation"]["sector_allocation"])
        
        # Add assistant response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_text,
            "has_portfolio": has_portfolio
        })
        
        # Rerun to update the chat display
        st.rerun()


def show_quick_recommend():
    """Wall Street-Level Quantitative Portfolio Optimization Engine"""
    
    # Professional header
    st.markdown('<div style="text-align: center; padding: 1rem 0;">', unsafe_allow_html=True)
    st.markdown('## 📊 F2 Portfolio Recommender')
    st.markdown('*Autonomous AI-Powered Portfolio Optimization with Cerebras*')
    st.caption('Institutional-Grade Quantitative Analysis | Real-Time Model Inference | Mean-Variance Optimization')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Professional parameter input grid
    st.markdown("### ⚙️ Portfolio Configuration Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_profile = st.select_slider(
            "🎯 Risk Tolerance",
            options=["low", "medium", "high"],
            value="medium",
            help="Defines volatility constraints and expected return targets"
        )
        
        profile_details = RISK_PROFILES[risk_profile]
        st.metric("Target Volatility", f"{profile_details['target_volatility']*100:.0f}%")
    
    with col2:
        horizon_years = st.slider(
            "⏱️ Investment Horizon",
            min_value=1,
            max_value=30,
            value=5,
            help="Time horizon for portfolio optimization and rebalancing strategy"
        )
        
        if horizon_years <= 3:
            st.caption("⚠️ Short-term: Conservative allocation recommended")
        elif horizon_years >= 10:
            st.caption("✅ Long-term: Growth-oriented strategies enabled")
        else:
            st.caption("📊 Medium-term: Balanced growth approach")
    
    with col3:
        portfolio_value = st.number_input(
            "💰 Total Investment ($)",
            min_value=1000,
            max_value=10000000,
            value=10000,
            step=1000,
            help="Total capital allocation for discrete share optimization"
        )
        
        min_holdings = st.number_input(
            "🔢 Min Holdings",
            min_value=3,
            max_value=15,
            value=profile_details['min_diversification'],
            help="Minimum number of positions for diversification"
        )
    
    # Advanced parameters
    with st.expander("🔬 Advanced Quantitative Parameters", expanded=False):
        adv_col1, adv_col2 = st.columns(2)
        
        with adv_col1:
            target_volatility = st.slider(
                "Target Annual Volatility (%)",
                min_value=5,
                max_value=40,
                value=int(profile_details['target_volatility'] * 100),
                help="Maximum acceptable portfolio volatility (standard deviation)"
            )
            
            rebalance_frequency = st.selectbox(
                "Rebalancing Frequency",
                ["Monthly", "Quarterly", "Semi-Annual", "Annual"],
                index=2,
                help="How often to rebalance the portfolio"
            )
        
        with adv_col2:
            all_sectors = st.session_state.data_loader.get_sector_mapping()
            unique_sectors = sorted(set(all_sectors.values()))
            
            sector_preferences = st.multiselect(
                "Sector Preferences (Optional)",
                options=unique_sectors,
                help="Constrain optimization to specific sectors"
            )
            
            include_etfs = st.checkbox("Include ETFs", value=False, help="Add ETF exposure (if available)")
    
    st.divider()
    
    # Generate button with professional styling
    generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
    
    with generate_col2:
        generate_clicked = st.button(
            "🚀 GENERATE OPTIMAL PORTFOLIO",
            type="primary",
            use_container_width=True,
            help="Execute mean-variance optimization with Cerebras AI inference"
        )
    
    if generate_clicked:
        # Professional loading message
        with st.spinner("⚙️ Executing quantitative optimization pipeline..."):
            st.info("🔄 **Status**: Fetching Cerebras model outputs | Calculating covariance matrices | Running Monte Carlo simulations...")
            
            # Build professional query
            query = f"Generate an optimal portfolio with {risk_profile} risk tolerance for a {horizon_years}-year horizon."
            if sector_preferences:
                query += f" Focus on {', '.join(sector_preferences)} sectors."
            
            # Process with agent
            result = st.session_state.agent.process_query(query)
            
            if result["success"]:
                st.session_state.recommendation = result
                
                # Professional success message
                st.success("✅ **Portfolio Optimization Complete** | Model: Cerebras Llama 3.3-70B | Optimization: Mean-Variance (Sharpe Maximization)")
                
                st.divider()
                
                # PORTFOLIO RECOMMENDATION HEADER
                st.markdown("## ✅ Portfolio Recommendation")
                
                metrics = result["recommendation"]["metrics"]
                allocation = result["recommendation"]["allocation"]
                sector_allocation = result["recommendation"]["sector_allocation"]
                
                # Professional metrics display
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
                        <h3 style="margin: 0; font-size: 0.9rem;">📈 Expected Return</h3>
                        <h1 style="margin: 0.5rem 0; font-size: 2rem;">{metrics['expected_annual_return']*100:.2f}%</h1>
                        <p style="margin: 0; font-size: 0.8rem; opacity: 0.9;">Annualized</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with metric_col2:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
                        <h3 style="margin: 0; font-size: 0.9rem;">📊 Volatility</h3>
                        <h1 style="margin: 0.5rem 0; font-size: 2rem;">{metrics['annual_volatility']*100:.2f}%</h1>
                        <p style="margin: 0; font-size: 0.8rem; opacity: 0.9;">Annual Std Dev</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with metric_col3:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                                padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
                        <h3 style="margin: 0; font-size: 0.9rem;">⚡ Sharpe Ratio</h3>
                        <h1 style="margin: 0.5rem 0; font-size: 2rem;">{metrics['sharpe_ratio']:.2f}</h1>
                        <p style="margin: 0; font-size: 0.8rem; opacity: 0.9;">Risk-Adjusted</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with metric_col4:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                                padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
                        <h3 style="margin: 0; font-size: 0.9rem;">🎯 Holdings</h3>
                        <h1 style="margin: 0.5rem 0; font-size: 2rem;">{metrics['diversification']}</h1>
                        <p style="margin: 0; font-size: 0.8rem; opacity: 0.9;">Positions</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                # Allocations and discrete shares
                alloc_col1, alloc_col2 = st.columns([1.5, 1])
                
                with alloc_col1:
                    st.markdown("### � Portfolio Allocations")
                    
                    # Calculate discrete allocation
                    discrete_alloc, leftover = st.session_state.agent.optimizer.discrete_allocation(
                        allocation,
                        portfolio_value
                    )
                    
                    # Build professional allocation table
                    alloc_data = []
                    for ticker in sorted(allocation.keys(), key=lambda x: allocation[x], reverse=True):
                        shares = discrete_alloc.get(ticker, 0)
                        sector = st.session_state.data_loader.get_sector_mapping().get(ticker, "Unknown")
                        
                        alloc_data.append({
                            "Ticker": ticker,
                            "Allocation": f"{allocation[ticker]*100:.1f}%",
                            "Shares": shares,
                            "Sector": sector,
                            "Weight": allocation[ticker]
                        })
                    
                    df_alloc = pd.DataFrame(alloc_data)
                    
                    # Styled dataframe
                    st.dataframe(
                        df_alloc[["Ticker", "Sector", "Allocation", "Shares"]],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    st.info(f"💵 **Leftover Cash**: ${leftover:,.2f}")
                
                with alloc_col2:
                    st.markdown("### 🌐 Sector Breakdown")
                    
                    sector_data = []
                    for sector, weight in sorted(sector_allocation.items(), key=lambda x: x[1], reverse=True):
                        sector_data.append({
                            "Sector": sector,
                            "Weight": f"{weight*100:.1f}%"
                        })
                    
                    st.dataframe(
                        pd.DataFrame(sector_data),
                        use_container_width=True,
                        hide_index=True
                    )
                
                st.divider()
                
                # Visualizations
                viz_col1, viz_col2 = st.columns(2)
                
                with viz_col1:
                    show_allocation_chart(allocation)
                
                with viz_col2:
                    show_sector_chart(sector_allocation)
                
                st.divider()
                
                # AI Commentary
                st.markdown("### 🧩 AI-Generated Portfolio Commentary")
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea;">
                {result["recommendation"]["explanation"]}
                </div>
                """, unsafe_allow_html=True)
                
                st.divider()
                
                # Professional disclaimer
                st.warning("""
                ⚠️ **DISCLAIMER**: This portfolio is AI-generated using Cerebras Llama 3.3-70B for **educational and demonstration purposes only**.
                
                - This output does **NOT** constitute financial advice, investment recommendations, or trading signals.
                - Past performance does not guarantee future results.
                - All investments carry risk, including potential loss of principal.
                - Consult a licensed financial advisor (CFA, CFP) before making investment decisions.
                - Periodic rebalancing and risk monitoring are recommended.
                
                **Optimization Method**: Mean-Variance Optimization | Sharpe Ratio Maximization  
                **Data Source**: Historical price data (2020-2025) | Cerebras fine-tuned inference  
                **Model**: Cerebras Llama 3.3-70B | Temperature: 0.7 | Real-time generation
                """)
                
            else:
                st.error(f"❌ **Optimization Failed**: {result.get('message', 'Unknown error occurred. Please try again.')}")


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


def show_settings():
    """Settings and configuration page"""
    st.header("⚙️ Settings & Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Data Status")
        is_valid, issues = st.session_state.data_loader.validate_data()
        
        if is_valid:
            st.success("✅ All data validated")
        else:
            st.warning("⚠️ Data issues detected")
            for issue in issues:
                st.text(f"- {issue}")
        
        stats = st.session_state.data_loader.get_portfolio_stats()
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Stocks", stats['total_stocks'])
        with col_b:
            st.metric("Sectors", len(stats['sectors']))
        with col_c:
            if stats['total_value']:
                st.metric("Total Value", f"${stats['total_value']:,.2f}")
        
        st.divider()
        
        st.subheader("📈 Data Sources")
        st.write("- **Portfolio Data**: Portfolio.csv")
        st.write("- **Historical Prices**: Portfolio_prices.csv (35K+ records)")
        st.write(f"- **Sectors**: {', '.join(stats['sectors'][:5])}...")
    
    with col2:
        st.subheader("🤖 AI Model")
        st.metric("Model", st.session_state.agent.model)
        st.metric("Provider", "Cerebras Cloud")
        st.metric("Status", "🟢 Active")
        
        st.divider()
        
        st.subheader("🏗️ Architecture")
        st.write("""
        The system follows a 5-layer agentic architecture:
        
        1. **Input Guardrails** - Validates user input
        2. **Agentic Reasoning** - Cerebras AI extracts parameters
        3. **Quantitative Optimization** - PyPortfolioOpt generates allocations
        4. **Explanation Generation** - AI creates explanations
        5. **Output Guardrails** - Ensures compliance
        """)
    
    st.divider()
    
    # Important Info
    st.subheader("⚠️ Important Disclaimer")
    st.warning("""
    This application is for **demonstration and educational purposes only**. 
    It is **NOT financial advice**. Always consult with a registered financial 
    advisor before making investment decisions.
    """)
    
    st.divider()
    
    # Tech Stack
    st.subheader("🛠️ Technology Stack")
    tech_df = pd.DataFrame([
        {"Component": "AI Model", "Technology": "Cerebras Llama 3.1 70B"},
        {"Component": "Frontend", "Technology": "Streamlit 1.32+"},
        {"Component": "Optimization", "Technology": "PyPortfolioOpt 1.5+"},
        {"Component": "Data Processing", "Technology": "pandas, numpy"},
        {"Component": "Visualization", "Technology": "Plotly 5.18+"},
    ])
    st.dataframe(tech_df, use_container_width=True, hide_index=True)


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
