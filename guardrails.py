"""
Guardrails System for F2 Portfolio Recommender Agent
Implements safety controls: PII detection, disclaimer enforcement, output validation
Ensures regulatory compliance and responsible AI practices
"""
import re
import json
from typing import Dict, List, Tuple, Any, Optional

# Try to import from new config, fall back to old config
try:
    from config_new import PII_PATTERNS, MANDATORY_DISCLAIMER
except ImportError:
    from config import PII_PATTERNS, MANDATORY_DISCLAIMER


class GuardrailSystem:
    """
    Comprehensive guardrails for agentic financial AI
    Protects user privacy, ensures compliance, validates outputs
    """
    
    def __init__(self):
        self.pii_patterns = [re.compile(pattern) for pattern in PII_PATTERNS]
        self.disclaimer = MANDATORY_DISCLAIMER
        self.violation_log = []
    
    def detect_pii(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect Personal Identifiable Information in user input
        
        Args:
            text: User input text to scan
            
        Returns:
            Tuple of (has_pii: bool, detected_patterns: List[str])
        """
        detected = []
        
        for pattern in self.pii_patterns:
            matches = pattern.findall(text)
            if matches:
                detected.extend([f"PII Pattern: {m[:4]}***" for m in matches])
        
        # Additional keyword-based detection
        pii_keywords = ['ssn', 'social security', 'credit card', 'pan card', 'aadhaar', 'passport']
        text_lower = text.lower()
        
        for keyword in pii_keywords:
            if keyword in text_lower:
                detected.append(f"PII Keyword: {keyword}")
        
        has_pii = len(detected) > 0
        
        if has_pii:
            self.violation_log.append({
                "type": "PII_DETECTED",
                "detected": detected,
                "input_preview": text[:50] + "..."
            })
        
        return has_pii, detected
    
    def validate_input(self, user_input: str) -> Dict[str, Any]:
        """
        Validate user input against all safety rules
        
        Args:
            user_input: Raw user query
            
        Returns:
            Validation result with status and details
        """
        result = {
            "is_valid": True,
            "violations": [],
            "sanitized_input": user_input
        }
        
        # PII check
        has_pii, pii_detected = self.detect_pii(user_input)
        if has_pii:
            result["is_valid"] = False
            result["violations"].append({
                "type": "PII_DETECTED",
                "details": pii_detected,
                "message": "Your input contains sensitive personal information. Please remove it and try again."
            })
        
        # Length check
        if len(user_input) > 1000:
            result["violations"].append({
                "type": "INPUT_TOO_LONG",
                "message": "Input exceeds maximum length. Please keep queries under 1000 characters."
            })
        
        # Check for malicious patterns
        malicious_keywords = ['hack', 'exploit', 'bypass', 'manipulate system']
        if any(keyword in user_input.lower() for keyword in malicious_keywords):
            result["is_valid"] = False
            result["violations"].append({
                "type": "SUSPICIOUS_INTENT",
                "message": "Input contains potentially malicious keywords."
            })
        
        return result
    
    def validate_portfolio_output(self, portfolio_data: Dict) -> Dict[str, Any]:
        """
        Validate portfolio optimization output for correctness and safety
        
        Args:
            portfolio_data: Portfolio result dictionary
            
        Returns:
            Validation result
        """
        result = {
            "is_valid": True,
            "violations": []
        }
        
        # Check for required fields
        required_fields = ['portfolio_weights', 'metrics']
        for field in required_fields:
            if field not in portfolio_data:
                result["is_valid"] = False
                result["violations"].append({
                    "type": "MISSING_FIELD",
                    "field": field
                })
        
        if not result["is_valid"]:
            return result
        
        # Validate weights sum to ~1.0
        weights = portfolio_data.get('portfolio_weights', {})
        if weights:
            total_weight = sum(weights.values())
            if not (0.95 <= total_weight <= 1.05):
                result["violations"].append({
                    "type": "INVALID_WEIGHTS",
                    "message": f"Weights sum to {total_weight:.4f}, expected ~1.0"
                })
        
        # Validate metrics are within reasonable bounds
        metrics = portfolio_data.get('metrics', {})
        if 'expected_annual_return' in metrics:
            ret = metrics['expected_annual_return']
            if ret < -0.5 or ret > 1.5:  # -50% to 150%
                result["violations"].append({
                    "type": "UNREALISTIC_RETURN",
                    "value": ret,
                    "message": "Expected return outside reasonable bounds"
                })
        
        if 'annual_volatility' in metrics:
            vol = metrics['annual_volatility']
            if vol < 0 or vol > 2.0:  # 0% to 200%
                result["violations"].append({
                    "type": "UNREALISTIC_VOLATILITY",
                    "value": vol,
                    "message": "Volatility outside reasonable bounds"
                })
        
        return result
    
    def enforce_disclaimer(self, output_text: str) -> str:
        """
        Ensure mandatory disclaimer is included in user-facing output
        
        Args:
            output_text: Response text to user
            
        Returns:
            Output with disclaimer appended if missing
        """
        # Check if disclaimer already present
        if "DISCLAIMER" in output_text.upper() or "not financial advice" in output_text.lower():
            return output_text
        
        # Append disclaimer
        return f"{output_text}\n\n{self.disclaimer}"
    
    def validate_and_format_response(
        self,
        portfolio_data: Dict,
        explanation: str
    ) -> Dict[str, Any]:
        """
        Complete output validation and formatting pipeline
        
        Args:
            portfolio_data: Raw portfolio optimization result
            explanation: Human-readable explanation
            
        Returns:
            Validated and formatted response with guardrails applied
        """
        # Validate portfolio output
        portfolio_validation = self.validate_portfolio_output(portfolio_data)
        
        if not portfolio_validation["is_valid"]:
            return {
                "success": False,
                "error": "Portfolio validation failed",
                "violations": portfolio_validation["violations"],
                "output": None
            }
        
        # Enforce disclaimer in explanation
        safe_explanation = self.enforce_disclaimer(explanation)
        
        # Format complete response
        response = {
            "success": True,
            "portfolio": portfolio_data.get('portfolio_weights', {}),
            "metrics": portfolio_data.get('metrics', {}),
            "explanation": safe_explanation,
            "metadata": portfolio_data.get('metadata', {}),
            "guardrails_applied": {
                "disclaimer_enforced": True,
                "output_validated": True,
                "validation_warnings": portfolio_validation.get("violations", [])
            }
        }
        
        return response
    
    def get_violation_summary(self) -> Dict:
        """
        Get summary of all guardrail violations detected during session
        
        Returns:
            Violation statistics
        """
        return {
            "total_violations": len(self.violation_log),
            "violations": self.violation_log
        }


# Utility functions for agent integration
def check_input_safety(user_input: str) -> Tuple[bool, Optional[str]]:
    """
    Quick safety check for agent input validation
    
    Args:
        user_input: User query string
        
    Returns:
        Tuple of (is_safe: bool, error_message: Optional[str])
    """
    guardrail = GuardrailSystem()
    validation = guardrail.validate_input(user_input)
    
    if not validation["is_valid"]:
        error_msg = "\n".join([v["message"] for v in validation["violations"]])
        return False, error_msg
    
    return True, None


def apply_output_guardrails(portfolio_result: Dict) -> Dict:
    """
    Apply all output guardrails to portfolio recommendation
    
    Args:
        portfolio_result: Raw optimization result
        
    Returns:
        Guardrailed response ready for user consumption
    """
    guardrail = GuardrailSystem()
    
    explanation = portfolio_result.get('explanation', 'No explanation provided.')
    
    final_response = guardrail.validate_and_format_response(
        portfolio_data=portfolio_result,
        explanation=explanation
    )
    
    return final_response


if __name__ == "__main__":
    # Test guardrails
    print("Testing Guardrail System...\n")
    
    # Test 1: PII Detection
    print("="*60)
    print("Test 1: PII Detection")
    print("="*60)
    
    test_inputs = [
        "I want a portfolio with medium risk for 5 years",
        "My PAN is ABCDE1234F, what should I invest in?",
        "SSN: 123-45-6789, please recommend stocks",
        "My Aadhaar is 123456789012"
    ]
    
    guardrail = GuardrailSystem()
    
    for inp in test_inputs:
        is_safe, error = check_input_safety(inp)
        status = "✅ SAFE" if is_safe else "❌ BLOCKED"
        print(f"\n{status}: '{inp[:50]}...'")
        if error:
            print(f"  Reason: {error}")
    
    # Test 2: Output Validation
    print("\n" + "="*60)
    print("Test 2: Output Validation & Disclaimer")
    print("="*60)
    
    sample_portfolio = {
        "portfolio_weights": {"RELIANCE.NS": 0.4, "TCS.NS": 0.6},
        "metrics": {
            "expected_annual_return": 0.15,
            "annual_volatility": 0.20,
            "sharpe_ratio": 0.75
        },
        "explanation": "This is a balanced portfolio for moderate risk investors."
    }
    
    validated_output = apply_output_guardrails(sample_portfolio)
    
    if validated_output["success"]:
        print("\n✅ Output Validation: PASSED")
        print(f"\nDisclaimer Enforced: {validated_output['guardrails_applied']['disclaimer_enforced']}")
        print(f"\nExplanation with Disclaimer:\n{validated_output['explanation'][:200]}...")
    else:
        print(f"\n❌ Output Validation: FAILED")
        print(f"Violations: {validated_output['violations']}")
    
    # Test 3: Violation Log
    print("\n" + "="*60)
    print("Test 3: Violation Summary")
    print("="*60)
    print(f"\nTotal Violations Detected: {len(guardrail.violation_log)}")


# New simplified classes for agent_cerebras.py compatibility
class InputGuardrail:
    """Simplified input guardrail for new agent"""
    
    def __init__(self):
        self.guardrail_system = GuardrailSystem()
    
    def check(self, user_input: str) -> Dict[str, Any]:
        """
        Check user input for safety
        
        Args:
            user_input: User's query
            
        Returns:
            Dictionary with 'passed' (bool) and 'issues' (list)
        """
        validation = self.guardrail_system.validate_input(user_input)
        
        return {
            "passed": validation["is_valid"],
            "issues": [v["message"] for v in validation["violations"]]
        }


class OutputGuardrail:
    """Simplified output guardrail for new agent"""
    
    def __init__(self):
        self.guardrail_system = GuardrailSystem()
    
    def check(self, output_text: str) -> Dict[str, Any]:
        """
        Check output for disclaimer compliance
        
        Args:
            output_text: Output text to validate
            
        Returns:
            Dictionary with 'passed' (bool) and 'has_disclaimer' (bool)
        """
        has_disclaimer = (
            "DISCLAIMER" in output_text.upper() or 
            "not financial advice" in output_text.lower()
        )
        
        return {
            "passed": has_disclaimer,
            "has_disclaimer": has_disclaimer
        }
