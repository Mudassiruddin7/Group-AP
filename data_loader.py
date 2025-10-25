"""
CSV Data Loader for F2 Portfolio Recommender
Loads portfolio and historical price data from CSV files
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PortfolioDataLoader:
    """Handles loading and processing of portfolio data from CSV files"""
    
    def __init__(self, portfolio_csv: Path, prices_csv: Path):
        """
        Initialize data loader
        
        Args:
            portfolio_csv: Path to Portfolio.csv
            prices_csv: Path to Portfolio_prices.csv
        """
        self.portfolio_csv = portfolio_csv
        self.prices_csv = prices_csv
        self._portfolio_df = None
        self._prices_df = None
        
    def load_portfolio(self) -> pd.DataFrame:
        """Load portfolio composition data"""
        if self._portfolio_df is None:
            logger.info(f"Loading portfolio from {self.portfolio_csv}")
            self._portfolio_df = pd.read_csv(self.portfolio_csv)
            logger.info(f"Loaded {len(self._portfolio_df)} stocks from portfolio")
        return self._portfolio_df
    
    def load_prices(self) -> pd.DataFrame:
        """Load historical price data"""
        if self._prices_df is None:
            logger.info(f"Loading prices from {self.prices_csv}")
            self._prices_df = pd.read_csv(self.prices_csv, parse_dates=['Date'])
            logger.info(f"Loaded {len(self._prices_df)} price records")
        return self._prices_df
    
    def get_stock_universe(self) -> List[str]:
        """Get list of all available stock tickers"""
        portfolio_df = self.load_portfolio()
        return portfolio_df['Ticker'].tolist()
    
    def get_sector_mapping(self) -> Dict[str, str]:
        """Get mapping of ticker to sector"""
        portfolio_df = self.load_portfolio()
        return dict(zip(portfolio_df['Ticker'], portfolio_df['Sector']))
    
    def get_historical_prices(
        self,
        tickers: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        lookback_days: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get historical adjusted close prices for specified tickers and date range
        
        Args:
            tickers: List of ticker symbols (None = all tickers)
            start_date: Start date for data
            end_date: End date for data (None = latest available)
            lookback_days: Alternative to start_date - look back N days from end
            
        Returns:
            DataFrame with Date index and ticker columns containing adjusted close prices
        """
        prices_df = self.load_prices()
        
        # Filter by tickers
        if tickers is not None:
            prices_df = prices_df[prices_df['Ticker'].isin(tickers)]
        
        # Set date range
        if end_date is None:
            end_date = prices_df['Date'].max()
        
        if lookback_days is not None and start_date is None:
            start_date = end_date - timedelta(days=lookback_days)
        
        if start_date is not None:
            prices_df = prices_df[prices_df['Date'] >= start_date]
        
        prices_df = prices_df[prices_df['Date'] <= end_date]
        
        # Pivot to wide format (Date x Ticker)
        price_matrix = prices_df.pivot(
            index='Date',
            columns='Ticker',
            values='Adjusted'
        )
        
        logger.info(
            f"Fetched prices for {price_matrix.shape[1]} tickers, "
            f"{price_matrix.shape[0]} days ({price_matrix.index.min()} to {price_matrix.index.max()})"
        )
        
        return price_matrix
    
    def get_returns(
        self,
        tickers: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        lookback_days: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Calculate returns from historical prices
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date
            end_date: End date
            lookback_days: Lookback period in days
            
        Returns:
            DataFrame of daily returns
        """
        prices = self.get_historical_prices(tickers, start_date, end_date, lookback_days)
        returns = prices.pct_change().dropna()
        
        logger.info(f"Calculated returns: {returns.shape[0]} days, {returns.shape[1]} tickers")
        return returns
    
    def get_portfolio_stats(self) -> Dict:
        """Get summary statistics of the current portfolio"""
        portfolio_df = self.load_portfolio()
        
        stats = {
            "total_stocks": len(portfolio_df),
            "total_value": portfolio_df['Price'].sum() if 'Price' in portfolio_df.columns else None,
            "sectors": portfolio_df['Sector'].unique().tolist(),
            "sector_distribution": portfolio_df.groupby('Sector')['Ticker'].count().to_dict(),
            "top_holdings": portfolio_df.nlargest(5, 'Weight')[['Ticker', 'Weight']].to_dict('records') if 'Weight' in portfolio_df.columns else []
        }
        
        return stats
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        """
        Validate that CSV data is properly formatted and complete
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        try:
            # Check portfolio CSV
            portfolio_df = self.load_portfolio()
            required_portfolio_cols = ['Ticker', 'Sector']
            missing_cols = set(required_portfolio_cols) - set(portfolio_df.columns)
            if missing_cols:
                issues.append(f"Portfolio.csv missing columns: {missing_cols}")
            
            # Check prices CSV
            prices_df = self.load_prices()
            required_price_cols = ['Date', 'Ticker', 'Adjusted']
            missing_cols = set(required_price_cols) - set(prices_df.columns)
            if missing_cols:
                issues.append(f"Portfolio_prices.csv missing columns: {missing_cols}")
            
            # Check data alignment
            portfolio_tickers = set(portfolio_df['Ticker'])
            price_tickers = set(prices_df['Ticker'])
            
            missing_prices = portfolio_tickers - price_tickers
            if missing_prices:
                issues.append(f"Tickers in portfolio without price data: {missing_prices}")
            
            # Check for sufficient historical data
            min_date = prices_df['Date'].min()
            max_date = prices_df['Date'].max()
            days_available = (max_date - min_date).days
            
            if days_available < 252:  # Less than 1 year
                issues.append(f"Only {days_available} days of data available (recommend 252+ for annual stats)")
            
            logger.info(f"Data validation: {len(issues)} issues found")
            
        except Exception as e:
            issues.append(f"Data validation error: {str(e)}")
            logger.error(f"Validation failed: {e}")
        
        return len(issues) == 0, issues


# Convenience function for quick data access
def get_data_loader(
    portfolio_csv: str = "datasets/Portfolio.csv",
    prices_csv: str = "datasets/Portfolio_prices.csv"
) -> PortfolioDataLoader:
    """
    Get a configured data loader instance
    
    Args:
        portfolio_csv: Path to portfolio CSV
        prices_csv: Path to prices CSV
        
    Returns:
        Configured PortfolioDataLoader
    """
    from pathlib import Path
    
    project_root = Path(__file__).parent
    portfolio_path = project_root / portfolio_csv
    prices_path = project_root / prices_csv
    
    return PortfolioDataLoader(portfolio_path, prices_path)


if __name__ == "__main__":
    # Test data loader
    logging.basicConfig(level=logging.INFO)
    
    loader = get_data_loader()
    
    print("=" * 60)
    print("PORTFOLIO DATA VALIDATION")
    print("=" * 60)
    
    is_valid, issues = loader.validate_data()
    
    if is_valid:
        print("✅ Data validation passed!")
    else:
        print("❌ Data validation failed:")
        for issue in issues:
            print(f"  - {issue}")
    
    print("\n" + "=" * 60)
    print("PORTFOLIO STATISTICS")
    print("=" * 60)
    
    stats = loader.get_portfolio_stats()
    print(f"Total Stocks: {stats['total_stocks']}")
    print(f"Sectors: {', '.join(stats['sectors'])}")
    print("\nSector Distribution:")
    for sector, count in stats['sector_distribution'].items():
        print(f"  {sector}: {count} stocks")
    
    print("\n" + "=" * 60)
    print("SAMPLE HISTORICAL DATA")
    print("=" * 60)
    
    # Get last 30 days of data for 5 stocks
    sample_tickers = loader.get_stock_universe()[:5]
    prices = loader.get_historical_prices(
        tickers=sample_tickers,
        lookback_days=30
    )
    
    print(f"\nLast 5 days of prices for {sample_tickers}:")
    print(prices.tail())
    
    # Calculate returns
    returns = loader.get_returns(tickers=sample_tickers, lookback_days=30)
    print(f"\nReturns summary:")
    print(returns.describe())
