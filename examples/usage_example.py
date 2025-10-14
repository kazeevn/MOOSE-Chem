"""
Example usage of the new MOOSE-Chem architecture.

This script demonstrates how to use the new configuration management,
LLM abstraction layer, and data models.
"""

import sys
import os

# Add parent directory to path to import Method modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Method.settings import settings, LLMSettings, ExperimentSettings
from Method.llm_client import create_llm_client
from Method.models import (
    Hypothesis,
    Inspiration,
    ResearchBackground,
    HypothesisCollection,
    PromptTemplate
)


def example_configuration():
    """Example 1: Using configuration management."""
    print("=" * 60)
    print("Example 1: Configuration Management")
    print("=" * 60)
    
    # Access global settings
    print(f"LLM Provider: {settings.llm.provider}")
    print(f"LLM Model: {settings.llm.model}")
    print(f"Experiment Name: {settings.experiment.name}")
    print(f"Checkpoint Dir: {settings.experiment.experiment_checkpoint_dir}")
    
    # Create custom settings
    custom_llm_settings = LLMSettings(
        provider="openai",
        model="gpt-4-turbo",
        temperature=0.7
    )
    print(f"\nCustom LLM temperature: {custom_llm_settings.temperature}")
    
    # Settings can be overridden with environment variables
    print("\nTo override settings, set environment variables:")
    print("  export MOOSE_LLM__PROVIDER=azure")
    print("  export MOOSE_LLM__MODEL=gpt-4")
    print("  export MOOSE_EXPERIMENT__NAME=my_experiment")
    print()


def example_llm_client():
    """Example 2: Using the LLM abstraction layer."""
    print("=" * 60)
    print("Example 2: LLM Client Abstraction")
    print("=" * 60)
    
    # Create a client (in real usage, you'd provide a valid API key)
    print("Creating LLM client...")
    print(f"Provider: openai")
    print(f"Model: gpt-4")
    print("\nNote: To actually use the client, provide a valid API key:")
    print("  client = create_llm_client(")
    print("      provider='openai',")
    print("      api_key='your-api-key-here',")
    print("      model='gpt-4'")
    print("  )")
    print("\nThen generate text:")
    print("  response = client.generate(prompt='Your prompt', temperature=0.7)")
    
    # Example of switching providers
    print("\nSwitching providers is easy:")
    print("  # OpenAI")
    print("  client = create_llm_client(provider='openai', ...)")
    print("  # Azure OpenAI")
    print("  client = create_llm_client(provider='azure', base_url='...', ...)")
    print("  # Google Gemini")
    print("  client = create_llm_client(provider='google', ...)")
    print()


def example_data_models():
    """Example 3: Using Pydantic data models."""
    print("=" * 60)
    print("Example 3: Data Models with Validation")
    print("=" * 60)
    
    # Create a research background
    background = ResearchBackground(
        question="How can we improve molecular generation using transformers?",
        survey="Previous work has shown that transformer models can be effective..."
    )
    print(f"Research Question: {background.question}")
    
    # Create an inspiration
    inspiration = Inspiration(
        title="Attention Is All You Need",
        abstract="The dominant sequence transduction models are based on complex...",
        reason="Introduces transformer architecture relevant to our work"
    )
    print(f"\nInspiration: {inspiration.title}")
    
    # Create a hypothesis with automatic validation
    hypothesis = Hypothesis(
        text="We hypothesize that a transformer-based molecular generator can...",
        reasoning="Based on the success of transformers in NLP...",
        scores=[8.5, 9.0, 7.5, 8.0]
    )
    print(f"\nHypothesis: {hypothesis.text[:60]}...")
    print(f"Average Score: {hypothesis.average_score}")
    
    # Validation example
    print("\nValidation Example:")
    try:
        invalid_hypothesis = Hypothesis(
            text="Test hypothesis",
            scores=[15.0]  # Invalid: score must be between 0 and 10
        )
    except ValueError as e:
        print(f"Validation caught error: Score must be between 0 and 10")
    
    # Create a hypothesis collection
    collection = HypothesisCollection(
        background_question=background.question
    )
    collection.add_hypothesis(inspiration.title, "0", hypothesis)
    print(f"\nHypothesis Collection created with {len(collection.hypotheses_by_inspiration)} inspirations")
    print()


def example_prompt_template():
    """Example 4: Using prompt templates."""
    print("=" * 60)
    print("Example 4: Prompt Templates")
    print("=" * 60)
    
    # Create a prompt template
    template = PromptTemplate(
        name="hypothesis_generation",
        template=(
            "Research Question: {question}\n\n"
            "Inspiration: {inspiration}\n\n"
            "Generate a novel research hypothesis based on the above."
        ),
        required_fields=["question", "inspiration"]
    )
    
    # Format the template
    prompt = template.format(
        question="How can we improve molecular generation?",
        inspiration="Transformers have been successful in NLP tasks..."
    )
    print(f"Template Name: {template.name}")
    print(f"\nFormatted Prompt:\n{prompt}")
    
    # Validation example
    print("\nValidation Example:")
    try:
        # Missing required field
        prompt = template.format(question="Only question provided")
    except ValueError as e:
        print(f"Validation caught error: {e}")
    print()


def example_integration():
    """Example 5: Integration example."""
    print("=" * 60)
    print("Example 5: Integration Example")
    print("=" * 60)
    
    print("Complete workflow example:")
    print()
    
    # 1. Setup configuration
    print("1. Configure the application:")
    print("   - Set LLM provider and model")
    print("   - Configure data paths")
    print("   - Set experiment parameters")
    
    # 2. Create LLM client
    print("\n2. Create LLM client:")
    print("   client = create_llm_client(**settings.llm.dict())")
    
    # 3. Load data
    print("\n3. Load research data:")
    background = ResearchBackground(
        question="Research question here",
        survey="Background survey here"
    )
    print(f"   - Research question loaded")
    
    # 4. Generate hypotheses
    print("\n4. Generate hypotheses:")
    print("   prompt = create_hypothesis_prompt(background, inspiration)")
    print("   response = client.generate(prompt)")
    print("   hypothesis = Hypothesis.parse(response)")
    
    # 5. Evaluate and collect
    collection = HypothesisCollection(background_question=background.question)
    print("\n5. Evaluate and collect:")
    print("   - Evaluate hypothesis")
    print("   - Add to collection")
    print("   - Save results")
    
    print("\nThis demonstrates the complete flow using the new architecture!")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("MOOSE-Chem Architecture Usage Examples")
    print("=" * 60 + "\n")
    
    example_configuration()
    example_llm_client()
    example_data_models()
    example_prompt_template()
    example_integration()
    
    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nFor more information, see:")
    print("  - ARCHITECTURE.md: Detailed architecture documentation")
    print("  - REWRITE.md: Original refactoring suggestions")
    print("  - Method/test_*.py: Unit tests with more examples")
    print()


if __name__ == "__main__":
    main()
