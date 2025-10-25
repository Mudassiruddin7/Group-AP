"""
Test script for ChatGPT-style interface
Tests efficient token usage and conversation flow
"""
import logging
from agent_cerebras import CerebrasPortfolioAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_chat_interface():
    """Test the chat interface with various query types"""
    
    print("="*70)
    print("CHATGPT-STYLE INTERFACE TEST")
    print("="*70)
    
    agent = CerebrasPortfolioAgent()
    chat_history = []
    
    # Test queries simulating a conversation
    test_queries = [
        ("Greeting", "hi"),
        ("Age mention", "im 20 what about u?"),
        ("Research", "research about Tesla stock"),
        ("Portfolio", "I want a medium risk portfolio for 10 years"),
        ("Follow-up", "what's the sharpe ratio?")
    ]
    
    for i, (query_type, query) in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {query_type}")
        print(f"User: {query}")
        print(f"{'='*70}")
        
        # Process query with chat history
        result = agent.process_query(query, chat_history)
        
        # Add to history (simulating what the app does)
        chat_history.append({"role": "user", "content": query})
        
        if result.get("is_chat"):
            print(f"\n🤖 Chat Response:")
            print(result["message"])
            chat_history.append({"role": "assistant", "content": result["message"]})
            
        elif result.get("is_research"):
            print(f"\n🔬 Research Response:")
            print(result["message"][:300] + "..." if len(result["message"]) > 300 else result["message"])
            chat_history.append({"role": "assistant", "content": result["message"]})
            
        elif result["success"] and result.get("recommendation"):
            print(f"\n📊 Portfolio Response:")
            print(result["recommendation"]["explanation"][:300] + "...")
            print(f"\n📈 Metrics:")
            metrics = result["recommendation"]["metrics"]
            print(f"  Return: {metrics['expected_annual_return']*100:.1f}%")
            print(f"  Volatility: {metrics['annual_volatility']*100:.1f}%")
            print(f"  Sharpe: {metrics['sharpe_ratio']:.2f}")
            print(f"  Holdings: {metrics['diversification']}")
            
            chat_history.append({
                "role": "assistant",
                "content": result["recommendation"]["explanation"],
                "has_portfolio": True
            })
        else:
            print(f"\n❌ Error: {result.get('message')}")
        
        print(f"\n💬 Chat history length: {len(chat_history)} messages")
    
    print(f"\n{'='*70}")
    print("✅ CHAT INTERFACE TEST COMPLETE")
    print(f"Total messages: {len(chat_history)}")
    print("="*70)


if __name__ == "__main__":
    test_chat_interface()
