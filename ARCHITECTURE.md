# MOOSE-Chem Architecture

This document describes the architectural improvements made to MOOSE-Chem to improve code quality, maintainability, and extensibility.

## Overview

The codebase has been refactored to follow modern software engineering best practices, with a focus on:

- **Modularity**: Separation of concerns into distinct layers
- **Type Safety**: Using Pydantic for data validation and type checking
- **Abstraction**: Abstract interfaces for swappable implementations
- **Configuration Management**: Centralized, type-safe configuration
- **Testability**: Unit tests for all new components

## Architecture Layers

### 1. Configuration Layer (`Method/settings.py`)

Centralized configuration management using Pydantic Settings. Configuration can be loaded from:
- Environment variables (prefixed with `MOOSE_`)
- `.env` files
- Programmatic defaults

**Key Features:**
- Type-safe configuration with validation
- Nested configuration structure
- Environment variable support with nested delimiter (`__`)

**Example:**
```python
from Method.settings import settings

# Access configuration
print(f"LLM Provider: {settings.llm.provider}")
print(f"Model: {settings.llm.model}")
print(f"Experiment: {settings.experiment.name}")
```

**Configuration via environment variables:**
```bash
export MOOSE_LLM__PROVIDER=openai
export MOOSE_LLM__MODEL=gpt-4
export MOOSE_EXPERIMENT__NAME=my_experiment
```

### 2. LLM Abstraction Layer (`Method/llm_client.py`)

Unified interface for interacting with different LLM providers (OpenAI, Azure OpenAI, Google Gemini).

**Key Features:**
- Abstract base class `LLMClient` defines the interface
- Concrete implementations for each provider
- Factory function `create_llm_client()` for easy instantiation
- Consistent API across different providers

**Example:**
```python
from Method.llm_client import create_llm_client

# Create a client (provider determined by configuration)
client = create_llm_client(
    provider="openai",
    api_key="your-api-key",
    model="gpt-4"
)

# Generate text
response = client.generate(
    prompt="What is the meaning of life?",
    temperature=0.7
)

# Generate structured output
structured_response = client.generate_structured(
    prompt="Evaluate this hypothesis",
    response_format=EvaluationResponse,
    temperature=0.5
)
```

**Switching providers is easy:**
```python
# Switch to Azure
client = create_llm_client(
    provider="azure",
    api_key="azure-key",
    model="gpt-4",
    base_url="https://your-resource.openai.azure.com"
)

# Switch to Google
client = create_llm_client(
    provider="google",
    api_key="google-key",
    model="gemini-1.5-pro"
)
```

### 3. Data Models Layer (`Method/models.py`)

Strongly-typed data structures using Pydantic for validation and documentation.

**Key Models:**
- `Hypothesis`: A scientific hypothesis with reasoning, feedback, and scores
- `Inspiration`: A research paper or inspiration source
- `ResearchBackground`: Research question and survey
- `HypothesisMutation`: A mutation line with refinement history
- `EvaluationResult`: Results from hypothesis evaluation
- `HypothesisCollection`: Organized collection of hypotheses
- `PromptTemplate`: Reusable prompt templates
- `APIResponse`: Standardized API response wrapper

**Example:**
```python
from Method.models import Hypothesis, Inspiration

# Create a hypothesis with automatic validation
hypothesis = Hypothesis(
    text="We hypothesize that X causes Y through mechanism Z",
    reasoning="Based on observations A, B, and C",
    scores=[8.5, 9.0, 7.5, 8.0]
)

# Access computed properties
print(f"Average score: {hypothesis.average_score}")  # 8.25

# Validation happens automatically
try:
    invalid_hyp = Hypothesis(
        text="Test",
        scores=[15.0]  # Invalid: score > 10
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

## Benefits of the New Architecture

### 1. Type Safety
- Pydantic models catch errors at runtime with clear error messages
- IDE autocomplete and type checking support
- Better documentation through type annotations

### 2. Testability
- Abstract interfaces allow for easy mocking in tests
- Unit tests validate each component independently
- See `Method/test_*.py` files for examples

### 3. Maintainability
- Clear separation of concerns
- Easy to understand and modify individual components
- Consistent patterns throughout the codebase

### 4. Flexibility
- Easy to swap LLM providers without changing core logic
- Configuration can be changed without modifying code
- New features can be added without breaking existing code

### 5. Extensibility
- New LLM providers can be added by implementing `LLMClient`
- New data models can be added as needed
- Configuration can be extended with new sections

## Migration Guide

### For Existing Code Using Direct API Calls

**Before:**
```python
from openai import OpenAI

client = OpenAI(api_key=args.api_key, base_url=args.base_url)
response = client.chat.completions.create(
    model=args.model,
    messages=[{"role": "user", "content": prompt}],
    temperature=1.0
)
text = response.choices[0].message.content
```

**After:**
```python
from Method.llm_client import create_llm_client

client = create_llm_client(
    provider=args.api_type,  # "openai", "azure", or "google"
    api_key=args.api_key,
    base_url=args.base_url,
    model=args.model
)
text = client.generate(prompt, temperature=1.0)
```

### For Configuration Management

**Before:**
```python
parser.add_argument("--model_name", type=str, default="gpt-4")
parser.add_argument("--api_key", type=str, required=True)
parser.add_argument("--checkpoint_dir", type=str, default="./Checkpoints")
```

**After:**
```python
from Method.settings import settings

# Settings are automatically loaded from environment or defaults
model_name = settings.llm.model
api_key = settings.llm.api_key
checkpoint_dir = settings.experiment.checkpoint_dir
```

### For Data Structures

**Before:**
```python
# Untyped nested dictionaries
hypothesis_data = {
    "text": "...",
    "scores": [8.0, 9.0],
    # No validation, easy to make mistakes
}
```

**After:**
```python
from Method.models import Hypothesis

# Typed, validated model
hypothesis = Hypothesis(
    text="...",
    scores=[8.0, 9.0]
)
# Automatic validation ensures data integrity
```

## Testing

All new components include comprehensive unit tests:

```bash
# Run all tests
cd Method
python -m unittest test_settings test_llm_client test_models -v

# Run specific test module
python -m unittest test_settings -v

# Run with coverage (if coverage is installed)
python -m coverage run -m unittest discover
python -m coverage report
```

## Future Improvements

Potential areas for further improvement:

1. **Workflow Orchestration**: Consider using Prefect or Dagster to replace `main.sh`
2. **Async Support**: Add async methods for parallel LLM calls
3. **Caching**: Implement response caching to reduce API costs
4. **Monitoring**: Add logging and metrics collection
5. **Database Layer**: Abstract data persistence beyond JSON files
6. **API Server**: Expose functionality through REST or GraphQL API

## Documentation

- See `REWRITE.md` for the original suggestions that guided this refactoring
- See individual module docstrings for detailed API documentation
- See test files for usage examples

## Questions or Issues?

If you have questions about the new architecture or encounter any issues, please open a GitHub issue.
