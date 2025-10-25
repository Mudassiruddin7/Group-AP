"""
Test F2 Portfolio AI with different age groups
"""
from agent_cerebras import CerebrasPortfolioAgent

def test_age_groups():
    """Test F2 Portfolio AI context-aware responses"""
    agent = CerebrasPortfolioAgent()
    
    test_cases = [
        ("Young Investor", "I'm 22 years old, moderate risk tolerance"),
        ("Middle-Aged", "I'm 40, looking for balanced growth"),
        ("Pre-Retirement", "I'm 58, conservative approach needed"),
    ]
    
    print("=" * 100)
    print("F2 PORTFOLIO AI - CONTEXT-AWARE TESTING")
    print("=" * 100)
    
    for category, query in test_cases:
        print(f"\n{'='*100}")
        print(f"🎯 {category.upper()} TEST")
        print(f"Query: \"{query}\"")
        print(f"{'='*100}\n")
        
        result = agent.process_query(query)
        
        if result["success"]:
            params = result["parameters"]
            metrics = result["recommendation"]["metrics"]
            
            print(f"📊 EXTRACTED PARAMETERS:")
            print(f"   Risk Profile: {params['risk_profile'].upper()}")
            print(f"   Horizon: {params['horizon_years']} years")
            print(f"   Reasoning: {params['reasoning']}")
            
            print(f"\n📈 PORTFOLIO METRICS:")
            print(f"   Expected Return: {metrics['expected_annual_return']*100:.1f}%")
            print(f"   Volatility: {metrics['annual_volatility']*100:.1f}%")
            print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"   Holdings: {metrics['diversification']} stocks")
            
            print(f"\n💬 F2 PORTFOLIO AI EXPLANATION:")
            print("-" * 100)
            # Print full explanation
            explanation = result["recommendation"]["explanation"]
            # Remove the disclaimer for cleaner output
            main_explanation = explanation.split("⚠️ DISCLAIMER:")[0].strip()
            print(main_explanation)
            print("-" * 100)
        else:
            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")
        
        print("\n")
    
    print("=" * 100)
    print("ALL TESTS COMPLETED")
    print("=" * 100)

if __name__ == "__main__":
    test_age_groups()
