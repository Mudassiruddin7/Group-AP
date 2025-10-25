"""
Portfolio Optimizer (CSV-Based) for F2 Portfolio Recommender
Uses PyPortfolioOpt with real historical data from CSV files
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt import objective_functions
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

from data_loader import PortfolioDataLoader
from config_new import RISK_PROFILES, RISK_FREE_RATE, LOOKBACK_PERIOD_DAYS

logger = logging.getLogger(__name__)


class CSVPortfolioOptimizer:
    """
    Portfolio optimization engine using CSV data
    Integrates PyPortfolioOpt with real historical price data
    """
    
    def __init__(self, data_loader: PortfolioDataLoader):
        """
        Initialize optimizer with data loader
        
        Args:
            data_loader: Configured PortfolioDataLoader instance
        """
        self.data_loader = data_loader
        self.sector_mapping = data_loader.get_sector_mapping()
        
    def optimize_portfolio(
        self,
        risk_profile: str,
        horizon_years: int,
        sector_preferences: Optional[List[str]] = None,
        exclude_tickers: Optional[List[str]] = None,
        lookback_days: int = LOOKBACK_PERIOD_DAYS
    ) -> Dict:
        """
        Optimize portfolio allocation based on risk profile and preferences
        
        Args:
            risk_profile: 'low', 'medium', or 'high'
            horizon_years: Investment horizon in years
            sector_preferences: Preferred sectors (optional)
            exclude_tickers: Tickers to exclude (optional)
            lookback_days: Historical data lookback period
            
        Returns:
            Optimization results dictionary with weights, metrics, and explanations
        """
        logger.info(f"Starting optimization: risk={risk_profile}, horizon={horizon_years}y")
        
        # Validate risk profile
        if risk_profile not in RISK_PROFILES:
            raise ValueError(f"Invalid risk profile: {risk_profile}. Choose from {list(RISK_PROFILES.keys())}")
        
        profile_config = RISK_PROFILES[risk_profile]
        
        # Get stock universe
        all_tickers = self.data_loader.get_stock_universe()
        
        # Apply exclusions
        if exclude_tickers:
            all_tickers = [t for t in all_tickers if t not in exclude_tickers]
        
        # Filter by sector preferences if specified
        if sector_preferences:
            all_tickers = [
                t for t in all_tickers 
                if self.sector_mapping.get(t) in sector_preferences
            ]
        
        logger.info(f"Optimizing for {len(all_tickers)} tickers")
        
        # Load historical data
        prices = self.data_loader.get_historical_prices(
            tickers=all_tickers,
            lookback_days=lookback_days
        )
        
        # Drop tickers with insufficient data
        prices = prices.dropna(axis=1, thresh=int(0.8 * len(prices)))
        available_tickers = prices.columns.tolist()
        
        logger.info(f"Using {len(available_tickers)} tickers with sufficient data")
        
        if len(available_tickers) < profile_config['min_diversification']:
            raise ValueError(
                f"Insufficient stocks ({len(available_tickers)}) for {risk_profile} risk profile "
                f"(minimum {profile_config['min_diversification']} required)"
            )
        
        # Calculate expected returns and risk
        mu = expected_returns.mean_historical_return(prices, frequency=252)
        S = risk_models.sample_cov(prices, frequency=252)
        
        # Create efficient frontier
        ef = EfficientFrontier(mu, S)
        
        # Apply sector constraints
        sector_mapper = {ticker: self.sector_mapping.get(ticker, 'Unknown') 
                        for ticker in available_tickers}
        sector_lower = {}
        sector_upper = {sector: profile_config['max_sector_weight'] 
                       for sector in set(sector_mapper.values())}
        
        ef.add_sector_constraints(sector_mapper, sector_lower, sector_upper)
        
        # Apply weight constraints (min 1% per stock to avoid too many positions)
        ef.add_constraint(lambda w: w >= 0.01)
        
        # Optimize based on risk profile
        if risk_profile == "low":
            # Minimize volatility for low risk
            ef.min_volatility()
        elif risk_profile == "medium":
            # Maximize Sharpe ratio for balanced approach
            ef.max_sharpe(risk_free_rate=RISK_FREE_RATE)
        else:  # high
            # Maximize returns with volatility constraint
            ef.efficient_return(target_return=mu.max() * 0.9)
        
        # Get cleaned weights
        weights = ef.clean_weights()
        
        # Calculate performance metrics
        performance = ef.portfolio_performance(
            verbose=False,
            risk_free_rate=RISK_FREE_RATE
        )
        
        expected_annual_return, annual_volatility, sharpe_ratio = performance
        
        # Get sector allocation
        sector_allocation = self._calculate_sector_allocation(weights, sector_mapper)
        
        # Generate explanation
        explanation = self._generate_explanation(
            weights=weights,
            risk_profile=risk_profile,
            horizon_years=horizon_years,
            expected_return=expected_annual_return,
            volatility=annual_volatility,
            sharpe_ratio=sharpe_ratio,
            sector_allocation=sector_allocation,
            sector_preferences=sector_preferences
        )
        
        result = {
            "weights": {k: round(v, 4) for k, v in weights.items() if v > 0.001},
            "metrics": {
                "expected_annual_return": round(expected_annual_return, 4),
                "annual_volatility": round(annual_volatility, 4),
                "sharpe_ratio": round(sharpe_ratio, 4),
                "diversification": len([w for w in weights.values() if w > 0.01])
            },
            "sector_allocation": sector_allocation,
            "explanation": explanation,
            "risk_profile": risk_profile,
            "horizon_years": horizon_years,
            "optimization_date": datetime.now().isoformat()
        }
        
        logger.info(f"Optimization complete: {len(result['weights'])} holdings, Sharpe={sharpe_ratio:.2f}")
        
        return result
    
    def _calculate_sector_allocation(
        self,
        weights: Dict[str, float],
        sector_mapper: Dict[str, str]
    ) -> Dict[str, float]:
        """Calculate percentage allocation by sector"""
        sector_weights = {}
        
        for ticker, weight in weights.items():
            if weight > 0.001:  # Only include meaningful weights
                sector = sector_mapper.get(ticker, 'Unknown')
                sector_weights[sector] = sector_weights.get(sector, 0.0) + weight
        
        return {k: round(v, 4) for k, v in sector_weights.items()}
    
    def _generate_explanation(
        self,
        weights: Dict[str, float],
        risk_profile: str,
        horizon_years: int,
        expected_return: float,
        volatility: float,
        sharpe_ratio: float,
        sector_allocation: Dict[str, float],
        sector_preferences: Optional[List[str]]
    ) -> str:
        """Generate plain English explanation of the recommendation"""
        
        # Filter to significant holdings
        significant_holdings = {k: v for k, v in weights.items() if v > 0.05}
        top_3_holdings = sorted(significant_holdings.items(), key=lambda x: x[1], reverse=True)[:3]
        
        explanation_parts = []
        
        # Opening
        explanation_parts.append(
            f"Based on your **{risk_profile} risk** profile and **{horizon_years}-year** "
            f"investment horizon, here's your optimized portfolio:\n"
        )
        
        # Performance expectations
        explanation_parts.append(
            f"**Expected Performance:**\n"
            f"- Annual Return: {expected_return*100:.1f}%\n"
            f"- Annual Volatility: {volatility*100:.1f}%\n"
            f"- Sharpe Ratio: {sharpe_ratio:.2f} (risk-adjusted return)\n"
        )
        
        # Top holdings
        explanation_parts.append("**Top Holdings:**\n")
        for ticker, weight in top_3_holdings:
            sector = self.sector_mapping.get(ticker, 'Unknown')
            explanation_parts.append(f"- **{ticker}** ({sector}): {weight*100:.1f}%\n")
        
        # Sector diversification
        explanation_parts.append("\n**Sector Diversification:**\n")
        sorted_sectors = sorted(sector_allocation.items(), key=lambda x: x[1], reverse=True)
        for sector, weight in sorted_sectors:
            explanation_parts.append(f"- {sector}: {weight*100:.1f}%\n")
        
        # Risk rationale
        risk_rationales = {
            "low": "This conservative allocation prioritizes capital preservation with lower volatility stocks and broad diversification.",
            "medium": "This balanced allocation seeks a middle ground between growth potential and risk management.",
            "high": "This growth-oriented allocation targets higher returns with concentrated positions in high-potential stocks."
        }
        explanation_parts.append(f"\n**Why This Allocation?**\n{risk_rationales[risk_profile]}\n")
        
        # Sector preference acknowledgment
        if sector_preferences:
            explanation_parts.append(
                f"\nYour preference for {', '.join(sector_preferences)} sectors has been incorporated "
                f"where it aligns with your risk profile.\n"
            )
        
        # Time horizon note
        if horizon_years >= 7:
            explanation_parts.append(
                "\nWith your long investment horizon, this portfolio can weather short-term volatility "
                "and capitalize on long-term growth opportunities.\n"
            )
        elif horizon_years <= 3:
            explanation_parts.append(
                "\nGiven your shorter time horizon, this portfolio emphasizes stability and "
                "liquidity to preserve capital.\n"
            )
        
        return "".join(explanation_parts)
    
    def discrete_allocation(
        self,
        weights: Dict[str, float],
        total_portfolio_value: float
    ) -> Tuple[Dict[str, int], float]:
        """
        Convert percentage weights to discrete share quantities
        
        Args:
            weights: Optimized portfolio weights
            total_portfolio_value: Total amount to invest ($)
            
        Returns:
            (allocation_dict, leftover_cash)
        """
        logger.info(f"Calculating discrete allocation for ${total_portfolio_value:,.2f}")
        
        tickers = list(weights.keys())
        latest_prices = self.data_loader.get_historical_prices(tickers=tickers)
        latest_prices = get_latest_prices(latest_prices)
        
        da = DiscreteAllocation(
            weights,
            latest_prices,
            total_portfolio_value=total_portfolio_value
        )
        
        allocation, leftover = da.greedy_portfolio()
        
        logger.info(f"Discrete allocation: {len(allocation)} positions, ${leftover:.2f} leftover")
        
        return allocation, leftover


def create_optimizer() -> CSVPortfolioOptimizer:
    """Convenience function to create optimizer with default data loader"""
    from data_loader import get_data_loader
    
    data_loader = get_data_loader()
    return CSVPortfolioOptimizer(data_loader)


if __name__ == "__main__":
    # Test optimizer
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("PORTFOLIO OPTIMIZER TEST")
    print("=" * 60)
    
    optimizer = create_optimizer()
    
    # Test optimization for different risk profiles
    for risk_profile in ['low', 'medium', 'high']:
        print(f"\n{'='*60}")
        print(f"OPTIMIZING FOR {risk_profile.upper()} RISK")
        print(f"{'='*60}\n")
        
        try:
            result = optimizer.optimize_portfolio(
                risk_profile=risk_profile,
                horizon_years=5
            )
            
            print("ALLOCATION:")
            for ticker, weight in sorted(result['weights'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {ticker}: {weight*100:.2f}%")
            
            print(f"\nMETRICS:")
            print(f"  Expected Return: {result['metrics']['expected_annual_return']*100:.2f}%")
            print(f"  Volatility: {result['metrics']['annual_volatility']*100:.2f}%")
            print(f"  Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
            print(f"  Holdings: {result['metrics']['diversification']}")
            
            print(f"\nSECTOR ALLOCATION:")
            for sector, weight in sorted(result['sector_allocation'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {sector}: {weight*100:.2f}%")
            
        except Exception as e:
            print(f"❌ Error: {e}")
