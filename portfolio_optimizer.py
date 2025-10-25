"""
Portfolio Optimization Tool
Uses PyPortfolioOpt for quantitative portfolio optimization based on Modern Portfolio Theory
Supports risk-adjusted allocation for Indian and global equities
"""
import warnings
warnings.filterwarnings('ignore')

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from pypfopt import EfficientFrontier, risk_models, expected_returns, objective_functions
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

from config import STOCK_UNIVERSE, RISK_PROFILES, HORIZON_ADJUSTMENTS


class PortfolioOptimizer:
    """
    Quantitative portfolio optimization engine
    Implements mean-variance optimization with risk profile adjustments
    """
    
    def __init__(self, lookback_period_years: int = 3):
        """
        Initialize optimizer with historical data lookback period
        
        Args:
            lookback_period_years: Years of historical data for calculation (default: 3)
        """
        self.lookback_period_years = lookback_period_years
        self.cache = {}  # Cache for historical data
    
    def _fetch_historical_data(self, tickers: List[str]) -> pd.DataFrame:
        """
        Fetch historical price data from Yahoo Finance
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            DataFrame with adjusted closing prices
        """
        cache_key = tuple(sorted(tickers))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_period_years * 365)
        
        try:
            data = yf.download(
                tickers,
                start=start_date,
                end=end_date,
                progress=False,
                auto_adjust=True
            )['Close']
            
            # Handle single ticker case
            if isinstance(data, pd.Series):
                data = data.to_frame(name=tickers[0])
            
            # Drop tickers with insufficient data
            data = data.dropna(axis=1, thresh=len(data) * 0.7)
            
            self.cache[cache_key] = data
            return data
            
        except Exception as e:
            raise ValueError(f"Failed to fetch historical data: {str(e)}")
    
    def _adjust_risk_for_horizon(
        self,
        risk_profile: str,
        horizon_years: int
    ) -> Tuple[str, float]:
        """
        Adjust risk profile based on investment horizon
        Longer horizons can tolerate slightly more risk
        
        Args:
            risk_profile: Original risk profile ('low', 'medium', 'high')
            horizon_years: Investment time horizon in years
            
        Returns:
            Tuple of (adjusted_risk_profile, risk_adjustment_factor)
        """
        risk_adjustment = 1.0
        
        # Long-term investors can take slightly more risk
        if horizon_years >= 10:
            risk_adjustment = 1.15
        elif horizon_years >= 7:
            risk_adjustment = 1.08
        elif horizon_years <= 3:
            # Short-term: be more conservative
            risk_adjustment = 0.85
        
        return risk_profile, risk_adjustment
    
    def optimize_portfolio(
        self,
        risk_profile: str,
        horizon_years: int,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Main optimization function - generates optimal portfolio allocation
        
        Args:
            risk_profile: User risk tolerance ('low', 'medium', 'high')
            horizon_years: Investment time horizon in years
            constraints: Optional constraints (e.g., {'max_weight': 0.3})
            
        Returns:
            Dictionary with portfolio weights, metrics, and metadata
        """
        # Validate inputs
        if risk_profile not in ['low', 'medium', 'high']:
            raise ValueError(f"Invalid risk_profile: {risk_profile}. Must be 'low', 'medium', or 'high'")
        
        if horizon_years < 1 or horizon_years > 30:
            raise ValueError(f"Invalid horizon_years: {horizon_years}. Must be between 1 and 30")
        
        # Get risk-appropriate stock universe
        profile_config = RISK_PROFILES[risk_profile]
        stock_set = profile_config['stock_set']
        tickers = STOCK_UNIVERSE[stock_set]
        
        # Fetch historical data
        historical_data = self._fetch_historical_data(tickers)
        
        if historical_data.empty or len(historical_data.columns) < 3:
            raise ValueError("Insufficient historical data for optimization")
        
        # Calculate expected returns and risk
        mu = expected_returns.mean_historical_return(historical_data)
        S = risk_models.sample_cov(historical_data)
        
        # Initialize Efficient Frontier optimizer
        ef = EfficientFrontier(mu, S, weight_bounds=(0.05, 0.4))  # Min 5%, Max 40% per stock
        
        # Apply horizon adjustment
        adjusted_profile, risk_adj = self._adjust_risk_for_horizon(risk_profile, horizon_years)
        target_return = profile_config['target_return'] * risk_adj
        
        # Optimize for risk-adjusted return
        try:
            # Maximize Sharpe ratio with target return constraint
            ef.add_objective(objective_functions.L2_reg, gamma=0.1)  # Diversification penalty
            ef.efficient_return(target_return=min(target_return, mu.max() * 0.9))
        except:
            # Fallback to max Sharpe if target return is infeasible
            ef.max_sharpe()
        
        # Get cleaned weights (removes tiny allocations)
        weights = ef.clean_weights()
        
        # Calculate portfolio performance metrics
        performance = ef.portfolio_performance(verbose=False)
        expected_annual_return = performance[0]
        annual_volatility = performance[1]
        sharpe_ratio = performance[2]
        
        # Prepare output
        result = {
            "portfolio_weights": {k: round(v, 4) for k, v in weights.items() if v > 0.01},
            "metrics": {
                "expected_annual_return": round(expected_annual_return, 4),
                "annual_volatility": round(annual_volatility, 4),
                "sharpe_ratio": round(sharpe_ratio, 4),
                "risk_profile": risk_profile,
                "horizon_years": horizon_years,
                "risk_adjustment_factor": round(risk_adj, 4)
            },
            "metadata": {
                "optimization_date": datetime.now().isoformat(),
                "lookback_period_years": self.lookback_period_years,
                "num_assets": len([w for w in weights.values() if w > 0.01]),
                "stock_universe": stock_set
            }
        }
        
        return result
    
    def explain_allocation(self, portfolio_result: Dict) -> str:
        """
        Generate human-readable explanation of portfolio allocation
        
        Args:
            portfolio_result: Output from optimize_portfolio()
            
        Returns:
            Plain English explanation string
        """
        weights = portfolio_result['portfolio_weights']
        metrics = portfolio_result['metrics']
        
        # Sort by weight
        sorted_holdings = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        
        explanation = f"""
**Portfolio Allocation Summary**

**Risk Profile:** {metrics['risk_profile'].upper()}
**Investment Horizon:** {metrics['horizon_years']} years

**Top Holdings:**
"""
        for ticker, weight in sorted_holdings[:5]:
            company_name = ticker.replace('.NS', ' (NSE)')
            explanation += f"  • {company_name}: {weight*100:.2f}%\n"
        
        explanation += f"""
**Expected Performance:**
  • Annual Return: {metrics['expected_annual_return']*100:.2f}%
  • Risk (Volatility): {metrics['annual_volatility']*100:.2f}%
  • Sharpe Ratio: {metrics['sharpe_ratio']:.2f}

**Rationale:**
"""
        
        # Add context-specific rationale
        if metrics['risk_profile'] == 'low':
            explanation += "  • Conservative allocation focused on stable, large-cap stocks\n"
            explanation += "  • Lower volatility suitable for capital preservation\n"
        elif metrics['risk_profile'] == 'medium':
            explanation += "  • Balanced allocation mixing growth and stability\n"
            explanation += "  • Moderate risk-reward profile for steady wealth building\n"
        else:
            explanation += "  • Aggressive allocation targeting high-growth opportunities\n"
            explanation += "  • Higher volatility accepted for long-term wealth creation\n"
        
        if metrics['horizon_years'] >= 10:
            explanation += "  • Long horizon allows riding out market cycles\n"
        elif metrics['horizon_years'] <= 3:
            explanation += "  • Short horizon requires more conservative positioning\n"
        
        explanation += f"\n**Diversification:** Portfolio spread across {portfolio_result['metadata']['num_assets']} assets\n"
        
        return explanation


# Tool function wrapper for agent integration
def portfolio_optimizer_tool(
    risk_profile: str,
    horizon_years: int,
    constraints: Optional[Dict] = None
) -> Dict:
    """
    Agent-callable tool function for portfolio optimization
    
    Args:
        risk_profile: 'low', 'medium', or 'high'
        horizon_years: Investment time horizon (1-30 years)
        constraints: Optional optimization constraints
        
    Returns:
        Complete portfolio recommendation with weights and explanation
    """
    optimizer = PortfolioOptimizer()
    
    try:
        # Generate optimized portfolio
        portfolio_result = optimizer.optimize_portfolio(
            risk_profile=risk_profile,
            horizon_years=horizon_years,
            constraints=constraints
        )
        
        # Add human-readable explanation
        explanation = optimizer.explain_allocation(portfolio_result)
        portfolio_result['explanation'] = explanation
        
        return portfolio_result
        
    except Exception as e:
        return {
            "error": str(e),
            "portfolio_weights": {},
            "metrics": {},
            "explanation": f"Failed to optimize portfolio: {str(e)}"
        }


if __name__ == "__main__":
    # Test the optimizer
    print("Testing Portfolio Optimizer...\n")
    
    test_cases = [
        ("low", 10),
        ("medium", 5),
        ("high", 3)
    ]
    
    for risk, horizon in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: Risk={risk}, Horizon={horizon} years")
        print('='*60)
        
        result = portfolio_optimizer_tool(risk, horizon)
        
        if 'error' not in result or not result['error']:
            print("\n📊 Portfolio Weights:")
            for ticker, weight in result['portfolio_weights'].items():
                print(f"  {ticker}: {weight*100:.2f}%")
            
            print(f"\n📈 Expected Return: {result['metrics']['expected_annual_return']*100:.2f}%")
            print(f"📉 Volatility: {result['metrics']['annual_volatility']*100:.2f}%")
            print(f"⚡ Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
            print(f"\n{result['explanation']}")
        else:
            print(f"❌ Error: {result['error']}")
