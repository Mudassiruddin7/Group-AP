"""
Command-Line Interface for F2 Portfolio Recommender Agent
Quick testing and demonstration without Jupyter
"""
import argparse
import sys
from pprint import pprint

from portfolio_optimizer import portfolio_optimizer_tool
from guardrails import check_input_safety, apply_output_guardrails

def main():
    parser = argparse.ArgumentParser(
        description='F2 Portfolio Recommender Agent - CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Conservative portfolio for 10 years
  python cli.py --risk low --horizon 10
  
  # Moderate portfolio for 5 years
  python cli.py --risk medium --horizon 5
  
  # Aggressive portfolio for 3 years
  python cli.py --risk high --horizon 3
  
  # Test PII detection
  python cli.py --test-pii "My PAN is ABCDE1234F"
        """
    )
    
    parser.add_argument(
        '--risk',
        type=str,
        choices=['low', 'medium', 'high'],
        help='Risk profile (low, medium, high)'
    )
    
    parser.add_argument(
        '--horizon',
        type=int,
        help='Investment horizon in years (1-30)'
    )
    
    parser.add_argument(
        '--test-pii',
        type=str,
        help='Test PII detection with custom input'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    
    args = parser.parse_args()
    
    # Test PII Detection
    if args.test_pii:
        print("="*70)
        print("Testing PII Detection")
        print("="*70)
        print(f"\nInput: '{args.test_pii}'")
        
        is_safe, error = check_input_safety(args.test_pii)
        
        if is_safe:
            print("\n✅ SAFE: No PII detected")
        else:
            print("\n❌ BLOCKED: PII detected!")
            print(f"Reason: {error}")
        
        return
    
    # Portfolio Optimization
    if args.risk and args.horizon:
        print("="*70)
        print(f"Portfolio Recommendation: {args.risk.upper()} Risk, {args.horizon} Years")
        print("="*70)
        
        # Generate portfolio
        result = portfolio_optimizer_tool(
            risk_profile=args.risk,
            horizon_years=args.horizon
        )
        
        if 'error' in result and result['error']:
            print(f"\n❌ Error: {result['error']}")
            return
        
        # Apply guardrails
        final_result = apply_output_guardrails(result)
        
        if not final_result['success']:
            print(f"\n❌ Validation Failed: {final_result.get('error')}")
            return
        
        # Display results
        print("\n📊 PORTFOLIO ALLOCATION:")
        print("-" * 70)
        for ticker, weight in sorted(final_result['portfolio'].items(), 
                                       key=lambda x: x[1], reverse=True):
            bar = "█" * int(weight * 50)
            print(f"  {ticker:15s} {weight*100:5.2f}% {bar}")
        
        print("\n📈 EXPECTED PERFORMANCE:")
        print("-" * 70)
        metrics = final_result['metrics']
        print(f"  Annual Return:  {metrics['expected_annual_return']*100:6.2f}%")
        print(f"  Volatility:     {metrics['annual_volatility']*100:6.2f}%")
        print(f"  Sharpe Ratio:   {metrics['sharpe_ratio']:6.2f}")
        print(f"  Risk Profile:   {metrics['risk_profile'].upper()}")
        print(f"  Horizon:        {metrics['horizon_years']} years")
        
        if args.verbose:
            print("\n💡 DETAILED EXPLANATION:")
            print("-" * 70)
            print(final_result['explanation'])
            
            print("\n🔧 METADATA:")
            print("-" * 70)
            pprint(final_result['metadata'])
            
            print("\n🛡️ GUARDRAILS:")
            print("-" * 70)
            pprint(final_result['guardrails_applied'])
        else:
            print("\n💡 SUMMARY:")
            print("-" * 70)
            explanation_lines = final_result['explanation'].split('\n')
            for line in explanation_lines[:10]:  # First 10 lines
                if line.strip():
                    print(f"  {line}")
            print("\n  (Use --verbose for full explanation)")
        
        # Growth projection
        print("\n💰 GROWTH PROJECTION (₹100,000 Initial Investment):")
        print("-" * 70)
        ret = metrics['expected_annual_return']
        for year in [1, 3, 5, args.horizon]:
            if year <= args.horizon:
                value = 100000 * (1 + ret) ** year
                print(f"  Year {year:2d}: ₹{value:,.0f}")
        
        print("\n" + "="*70)
        
    else:
        parser.print_help()
        print("\n⚠️  Please provide --risk and --horizon arguments")


if __name__ == "__main__":
    main()
