"""
Refactoring Guide: Before and After Examples

This file shows concrete examples of how to refactor existing MOOSE-Chem code
to use the new architecture.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ============================================================================
# Example 1: LLM Client Initialization
# ============================================================================

def example_1_before():
    """
    BEFORE: Direct API client initialization with conditional logic
    """
    # This is how it was done in the old code
    print("BEFORE - Direct API initialization:")
    print("""
    from openai import OpenAI, AzureOpenAI
    from google import genai
    
    # Complex conditional logic for different providers
    if args.api_type == 0:
        self.client = OpenAI(api_key=args.api_key, base_url=args.base_url)
    elif args.api_type == 1:
        self.client = AzureOpenAI(
            azure_endpoint=args.base_url,
            api_key=args.api_key,
            api_version="2024-06-01"
        )
    elif args.api_type == 2:
        self.client = genai.Client(api_key=args.api_key)
    else:
        raise NotImplementedError
    """)


def example_1_after():
    """
    AFTER: Using the LLM abstraction layer
    """
    print("AFTER - Using LLM abstraction:")
    print("""
    from Method.llm_client import create_llm_client
    
    # Simple, unified interface
    provider_map = {0: "openai", 1: "azure", 2: "google"}
    self.client = create_llm_client(
        provider=provider_map[args.api_type],
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model_name
    )
    """)


# ============================================================================
# Example 2: Making API Calls
# ============================================================================

def example_2_before():
    """
    BEFORE: Provider-specific API call handling
    """
    print("BEFORE - Provider-specific API calls:")
    print("""
    # Different code for different providers
    if api_type == 0:  # OpenAI
        response = self.client.chat.completions.create(
            model=self.args.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0
        )
        result = response.choices[0].message.content
    elif api_type == 2:  # Google
        response = self.client.models.generate_content(
            model=self.args.model_name,
            contents=prompt,
            config={"temperature": 1.0}
        )
        result = response.text
    """)


def example_2_after():
    """
    AFTER: Using the unified client interface
    """
    print("AFTER - Unified API calls:")
    print("""
    # Same code works for all providers
    result = self.client.generate(
        prompt=prompt,
        temperature=1.0
    )
    """)


# ============================================================================
# Example 3: Configuration Management
# ============================================================================

def example_3_before():
    """
    BEFORE: Scattered configuration in argparse
    """
    print("BEFORE - Argparse configuration:")
    print("""
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="gpt-4")
    parser.add_argument("--api_key", type=str, required=True)
    parser.add_argument("--base_url", type=str, default=None)
    parser.add_argument("--checkpoint_dir", type=str, default="./Checkpoints")
    parser.add_argument("--num_mutations", type=int, default=3)
    parser.add_argument("--temperature", type=float, default=1.0)
    # ... many more arguments
    args = parser.parse_args()
    
    # Access throughout code
    model = args.model_name
    checkpoint = args.checkpoint_dir
    """)


def example_3_after():
    """
    AFTER: Using centralized settings
    """
    print("AFTER - Centralized settings:")
    print("""
    from Method.settings import settings
    
    # Configuration loaded from environment or defaults
    model = settings.llm.model
    checkpoint = settings.experiment.checkpoint_dir
    
    # Can still use argparse for command-line overrides
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=settings.llm.model)
    args = parser.parse_args()
    
    # Or set via environment variables:
    # export MOOSE_LLM__MODEL=gpt-4
    # export MOOSE_EXPERIMENT__NAME=my_experiment
    """)


# ============================================================================
# Example 4: Data Structures
# ============================================================================

def example_4_before():
    """
    BEFORE: Untyped nested dictionaries
    """
    print("BEFORE - Nested dictionaries:")
    print("""
    # Hard to understand, no validation
    hypothesis_data = {
        "text": "We hypothesize...",
        "reasoning": "Based on...",
        "feedback": "Good hypothesis",
        "scores": [8.0, 9.0, 7.5, 8.5]
    }
    
    # Easy to make mistakes
    avg_score = sum(hypothesis_data["scores"]) / len(hypothesis_data["scores"])
    
    # What if scores is empty? What if it's not a list?
    # No validation, errors happen at runtime
    """)


def example_4_after():
    """
    AFTER: Using Pydantic models
    """
    print("AFTER - Pydantic models:")
    print("""
    from Method.models import Hypothesis
    
    # Type-safe, validated data structure
    hypothesis = Hypothesis(
        text="We hypothesize...",
        reasoning="Based on...",
        feedback="Good hypothesis",
        scores=[8.0, 9.0, 7.5, 8.5]
    )
    
    # Computed properties
    avg_score = hypothesis.average_score  # 8.25
    
    # Automatic validation
    try:
        bad_hyp = Hypothesis(text="Test", scores=[15.0])  # Score > 10!
    except ValueError as e:
        print(f"Caught validation error: {e}")
    """)


# ============================================================================
# Example 5: Complete Refactoring Example
# ============================================================================

def example_5_before():
    """
    BEFORE: Complete old-style class initialization
    """
    print("BEFORE - Complete class initialization:")
    print("""
    class HypothesisGenerationEA(object):
        def __init__(self, args, custom_rq=None, custom_bs=None):
            self.args = args
            
            # Manual client setup
            if args.api_type == 0:
                self.client = OpenAI(api_key=args.api_key, base_url=args.base_url)
            elif args.api_type == 1:
                self.client = AzureOpenAI(...)
            elif args.api_type == 2:
                self.client = genai.Client(api_key=args.api_key)
            
            # Load data
            if custom_rq is None:
                self.bkg_q_list, self.dict_bkg2insp, ... = load_chem_annotation(
                    args.chem_annotation_path, ...
                )
            else:
                self.bkg_q_list = [custom_rq]
                self.dict_bkg2survey = {custom_rq: custom_bs}
        
        def generate_hypothesis(self, prompt):
            # Provider-specific call
            if self.args.api_type == 0:
                response = self.client.chat.completions.create(...)
                return response.choices[0].message.content
            elif self.args.api_type == 2:
                response = self.client.models.generate_content(...)
                return response.text
    """)


def example_5_after():
    """
    AFTER: Refactored class using new architecture
    """
    print("AFTER - Refactored with new architecture:")
    print("""
    from Method.llm_client import create_llm_client
    from Method.settings import settings
    from Method.models import ResearchBackground, Hypothesis
    
    class HypothesisGenerationEA(object):
        def __init__(self, llm_client=None, research_background=None):
            # Dependency injection - easier to test
            self.client = llm_client or create_llm_client(
                provider=settings.llm.provider,
                api_key=settings.llm.api_key,
                base_url=settings.llm.base_url,
                model=settings.llm.model
            )
            
            # Use Pydantic models
            if research_background:
                self.background = research_background
            else:
                # Load default
                self.background = self._load_default_background()
        
        def generate_hypothesis(self, prompt: str) -> str:
            # Unified interface - works with any provider
            return self.client.generate(
                prompt=prompt,
                temperature=settings.llm.temperature
            )
        
        def create_hypothesis_model(self, text: str, scores: list) -> Hypothesis:
            # Return validated model
            return Hypothesis(text=text, scores=scores)
    """)


# ============================================================================
# Example 6: Testing Benefits
# ============================================================================

def example_6_after():
    """
    Testing with the new architecture
    """
    print("AFTER - Easy testing with mocks:")
    print("""
    import unittest
    from unittest.mock import Mock
    
    class TestHypothesisGeneration(unittest.TestCase):
        def test_generate_hypothesis(self):
            # Mock the LLM client
            mock_client = Mock()
            mock_client.generate.return_value = "Test hypothesis"
            
            # Inject mock into class
            generator = HypothesisGenerationEA(llm_client=mock_client)
            
            # Test without making real API calls
            result = generator.generate_hypothesis("Test prompt")
            
            self.assertEqual(result, "Test hypothesis")
            mock_client.generate.assert_called_once()
    """)


# ============================================================================
# Main
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("MOOSE-Chem Refactoring Guide: Before and After")
    print("=" * 70 + "\n")
    
    print("Example 1: LLM Client Initialization")
    print("-" * 70)
    example_1_before()
    print()
    example_1_after()
    print("\n")
    
    print("Example 2: Making API Calls")
    print("-" * 70)
    example_2_before()
    print()
    example_2_after()
    print("\n")
    
    print("Example 3: Configuration Management")
    print("-" * 70)
    example_3_before()
    print()
    example_3_after()
    print("\n")
    
    print("Example 4: Data Structures")
    print("-" * 70)
    example_4_before()
    print()
    example_4_after()
    print("\n")
    
    print("Example 5: Complete Class Refactoring")
    print("-" * 70)
    example_5_before()
    print()
    example_5_after()
    print("\n")
    
    print("Example 6: Testing Benefits")
    print("-" * 70)
    example_6_after()
    print("\n")
    
    print("=" * 70)
    print("Key Benefits of the Refactoring:")
    print("=" * 70)
    print("✅ Cleaner, more maintainable code")
    print("✅ Type safety and validation")
    print("✅ Easier testing with dependency injection")
    print("✅ Provider-agnostic API calls")
    print("✅ Centralized configuration")
    print("✅ Better documentation through types")
    print("\nSee ARCHITECTURE.md for more details!")
    print()


if __name__ == "__main__":
    main()
