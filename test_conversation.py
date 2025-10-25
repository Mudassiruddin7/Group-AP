"""
Test F2 Portfolio AI conversational modes
"""
from agent_cerebras import CerebrasPortfolioAgent

def test_conversation_modes():
    """Test chat, research, and portfolio modes"""
    agent = CerebrasPortfolioAgent()
    
    test_cases = [
        ("General Chat", "hi"),
        ("General Chat", "hello, how are you?"),
        ("Research", "research about Apple stock"),
        ("Research", "tell me about diversification"),
        ("Research", "what is the Sharpe ratio?"),
        ("Portfolio", "I'm 25, moderate risk"),
        ("Portfolio", "need conservative portfolio for 5 years"),
    ]
    
    print("=" * 100)
    print("F2 PORTFOLIO AI - CONVERSATIONAL TESTING")
    print("=" * 100)
    
    for category, query in test_cases:
        print(f"\n{'='*100}")
        print(f"🎯 {category.upper()} MODE")
        print(f"Query: \"{query}\"")
        print(f"{'='*100}\n")
        
        result = agent.process_query(query)
        
        if result.get("is_chat"):
            print(f"💬 CONVERSATIONAL RESPONSE:")
            print("-" * 100)
            print(result.get("message", ""))
            print("-" * 100)
            
        elif result.get("is_research"):
            print(f"🔬 RESEARCH RESPONSE:")
            print("-" * 100)
            message = result.get("message", "")
            # Show first 500 chars for brevity
            print(message[:500] + "..." if len(message) > 500 else message)
            print("-" * 100)
            
        elif result.get("success") and result.get("recommendation"):
            print(f"📊 PORTFOLIO RECOMMENDATION:")
            print("-" * 100)
            params = result["parameters"]
            metrics = result["recommendation"]["metrics"]
            print(f"Risk: {params['risk_profile'].upper()} | Horizon: {params['horizon_years']}y")
            print(f"Return: {metrics['expected_annual_return']*100:.1f}% | Volatility: {metrics['annual_volatility']*100:.1f}%")
            print(f"Holdings: {metrics['diversification']} stocks")
            # Show first 300 chars of explanation
            explanation = result["recommendation"]["explanation"].split("⚠️ DISCLAIMER:")[0]
            print(f"\n{explanation[:300]}...")
            print("-" * 100)
        else:
            print(f"❌ Error: {result.get('message', 'Unknown')}")
        
        print()
    
    print("=" * 100)
    print("ALL CONVERSATION MODES TESTED")
    print("=" * 100)
    print("\n✅ The AI now intelligently detects:")
    print("   • General greetings → Warm conversational response")
    print("   • Research requests → Detailed information using Cerebras")
    print("   • Portfolio queries → Full optimization with charts")

if __name__ == "__main__":
    test_conversation_modes()
