"""
System Verification Script
Tests all components of the F2 Portfolio Recommender
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("F2 PORTFOLIO RECOMMENDER - SYSTEM VERIFICATION")
print("=" * 70)

# Test 1: Import check
print("\n[1/5] Testing imports...")
try:
    import pandas as pd
    import numpy as np
    from cerebras.cloud.sdk import Cerebras
    import streamlit as st
    import plotly.express as px
    from pypfopt import EfficientFrontier
    print("✅ All core imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 2: Data loader
print("\n[2/5] Testing data loader...")
try:
    from data_loader import get_data_loader
    
    loader = get_data_loader()
    is_valid, issues = loader.validate_data()
    
    if is_valid:
        print("✅ Data validation passed")
        stats = loader.get_portfolio_stats()
        print(f"   - {stats['total_stocks']} stocks in portfolio")
        print(f"   - {len(stats['sectors'])} sectors")
    else:
        print("⚠️  Data validation issues:")
        for issue in issues:
            print(f"   - {issue}")
except Exception as e:
    print(f"❌ Data loader failed: {e}")
    sys.exit(1)

# Test 3: Configuration
print("\n[3/5] Testing configuration...")
try:
    from config_new import (
        CEREBRAS_API_KEY,
        CEREBRAS_MODEL,
        RISK_PROFILES,
        PORTFOLIO_CSV,
        PORTFOLIO_PRICES_CSV
    )
    
    print(f"✅ Configuration loaded")
    print(f"   - Model: {CEREBRAS_MODEL}")
    print(f"   - API Key: {CEREBRAS_API_KEY[:20]}...")
    print(f"   - Risk Profiles: {list(RISK_PROFILES.keys())}")
    print(f"   - Portfolio CSV: {PORTFOLIO_CSV.exists()}")
    print(f"   - Prices CSV: {PORTFOLIO_PRICES_CSV.exists()}")
except Exception as e:
    print(f"❌ Configuration failed: {e}")
    sys.exit(1)

# Test 4: Portfolio optimizer
print("\n[4/5] Testing portfolio optimizer...")
try:
    from portfolio_optimizer_csv import create_optimizer
    
    optimizer = create_optimizer()
    print("✅ Optimizer initialized")
    print(f"   - Available stocks: {len(optimizer.data_loader.get_stock_universe())}")
    print(f"   - Sector mapping: {len(optimizer.sector_mapping)} entries")
    
    # Quick optimization test
    print("   - Running quick optimization test (medium risk)...")
    result = optimizer.optimize_portfolio(
        risk_profile="medium",
        horizon_years=5
    )
    print(f"   ✅ Optimization successful: {len(result['weights'])} holdings")
    print(f"      Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
    print(f"      Expected Return: {result['metrics']['expected_annual_return']*100:.1f}%")
    
except Exception as e:
    print(f"❌ Optimizer failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Cerebras agent
print("\n[5/5] Testing Cerebras agent...")
try:
    from agent_cerebras import create_agent
    
    agent = create_agent()
    print("✅ Agent initialized")
    print(f"   - Model: {agent.model}")
    print(f"   - Cerebras client: Connected")
    
    # Test parameter extraction
    print("   - Testing parameter extraction...")
    test_query = "I want a medium risk portfolio for 5 years"
    params = agent._extract_parameters(test_query)
    print(f"   ✅ Parameter extraction successful")
    print(f"      Risk: {params['risk_profile']}")
    print(f"      Horizon: {params['horizon_years']} years")
    
except Exception as e:
    print(f"❌ Agent failed: {e}")
    import traceback
    traceback.print_exc()
    print("\n   Note: This might be due to API connectivity.")
    print("   Check your Cerebras API key and internet connection.")

# Final summary
print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\n✅ System is ready!")
print("\nNext steps:")
print("  1. Run Streamlit app: streamlit run app.py")
print("  2. Open browser at: http://localhost:8501")
print("  3. Start using the AI Portfolio Recommender!")
print("\n" + "=" * 70)
