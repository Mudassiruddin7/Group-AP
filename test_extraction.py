"""
Quick test to verify AI parameter extraction is working
"""
from agent_cerebras import CerebrasPortfolioAgent

def test_queries():
    """Test various query formats"""
    agent = CerebrasPortfolioAgent()
    
    test_cases = [
        "hi im 30 with medium risk tolerance",
        "im 20, moderate risk",
        "conservative portfolio for 5 years",
        "aggressive growth, age 25",
        "I'm 45 years old and want a balanced portfolio"
    ]
    
    print("=" * 80)
    print("TESTING AI PARAMETER EXTRACTION")
    print("=" * 80)
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{query}'")
        print("-" * 80)
        
        result = agent.process_query(query)
        
        if result["success"]:
            params = result["parameters"]
            print(f"✅ SUCCESS")
            print(f"   Risk: {params['risk_profile']}")
            print(f"   Horizon: {params['horizon_years']} years")
            print(f"   Confidence: {params['confidence']:.2f}")
            print(f"   Reasoning: {params['reasoning']}")
            print(f"   Holdings: {result['recommendation']['metrics']['diversification']} stocks")
            print(f"   Expected Return: {result['recommendation']['metrics']['expected_annual_return']*100:.1f}%")
        else:
            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_queries()
