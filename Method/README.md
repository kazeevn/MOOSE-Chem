# MOOSE-Chem Method Module

This directory contains the core implementation of the MOOSE-Chem hypothesis generation pipeline.

## Module Overview

### Core Modules

- **`config.py`**: Centralized configuration for LLM API calls, hypothesis generation, and prompts
  - `LLMConfig`: API retry logic, token limits, and temperature constraints
  - `HypothesisGenerationConfig`: Discipline-specific settings and generation parameters
  - `PromptConfig`: Configuration for prompt formatting and retries

- **`utils.py`**: Utility functions for LLM API interaction and data processing
  - `llm_generation()`: Main function for calling LLM APIs with retry logic
  - `llm_generation_structured()`: Generate structured outputs using Pydantic models
  - `instruction_prompts()`: Prompt templates for different pipeline stages
  - Various helper functions for data loading and processing

- **`hypothesis_generation.py`**: Main hypothesis generation logic
  - `HypothesisGenerationEA` class: Evolutionary algorithm for hypothesis generation
  - Handles mutation, refinement, and evaluation of hypotheses

- **`inspiration_screening.py`**: Literature screening for finding inspirations
  - `Screening` class: Multi-round screening process
  - Identifies relevant papers to inspire hypothesis generation

- **`evaluate.py`**: Hypothesis ranking and evaluation
  - `Evaluate` class: Evaluates and ranks generated hypotheses
  - Supports automatic evaluation and comparison with ground truth

- **`logging_utils.py`**: Logging configuration and utilities
  - `setup_logger()`: Configures file and console logging
  - Suppresses verbose logs from external libraries

## Key Improvements

### 1. Error Handling and Retry Logic
- Increased max retries from 1 to 3 with exponential backoff
- Added proper input validation for all API calls
- Better error messages with contextual information
- Empty response detection and handling

### 2. Configuration Management
- Centralized configuration in `config.py`
- Separate configs for LLM, hypothesis generation, and prompts
- Easy to modify settings without changing code
- Validation functions for common parameters

### 3. Logging Support
- Comprehensive logging throughout the pipeline
- Debug, warning, and error levels
- Tracks API calls, retries, and errors
- Configurable log output

### 4. Code Quality
- Comprehensive unit tests (23 tests covering core functionality)
- Better documentation and docstrings
- Input validation and type hints
- Backwards compatibility maintained

## Usage Examples

### Basic LLM Generation
```python
from utils import llm_generation
from openai import OpenAI

client = OpenAI(api_key="your-key")
response = llm_generation(
    prompt="Generate a hypothesis about...",
    model_name="gpt-4",
    client=client,
    temperature=1.0,
    api_type=0  # 0=OpenAI, 1=Azure, 2=Google
)
```

### Structured Output Generation
```python
from utils import llm_generation_structured, HypothesisResponse
from openai import OpenAI

client = OpenAI(api_key="your-key")
result = llm_generation_structured(
    prompt="Generate a hypothesis...",
    model_name="gpt-4",
    client=client,
    template=HypothesisResponse,
    temperature=1.0,
    api_type=0
)
```

### Configuration
```python
from config import llm_config, hypothesis_config

# Adjust retry settings
llm_config.MAX_RETRIES = 5
llm_config.MAX_RETRY_DELAY = 10.0

# Adjust hypothesis generation settings
hypothesis_config.DEFAULT_NUM_MUTATIONS = 5
```

## Testing

Run the unit tests:
```bash
cd Method
python -m unittest test_utils -v
```

All 23 tests should pass, covering:
- Configuration validation
- Input validation
- Retry logic and exponential backoff
- Response validation
- Pydantic model validation

## Configuration Parameters

### LLM Config
- `MAX_RETRIES`: Number of retry attempts (default: 3)
- `INITIAL_RETRY_DELAY`: Initial delay between retries (default: 0.5s)
- `MAX_RETRY_DELAY`: Maximum delay between retries (default: 5.0s)
- `BACKOFF_MULTIPLIER`: Exponential backoff multiplier (default: 2.0)
- `MAX_COMPLETION_TOKENS_DEFAULT`: Default token limit (default: 8192)
- `MAX_COMPLETION_TOKENS_CLAUDE_HAIKU`: Token limit for Claude Haiku (default: 4096)

### Hypothesis Generation Config
- `DISCIPLINE`: Research discipline (default: "AI for Materials Science")
- `DEFAULT_NUM_ITERS_SELF_REFINE`: Refinement iterations (default: 3)
- `DEFAULT_NUM_MUTATIONS`: Number of mutations (default: 3)
- `DEFAULT_NUM_SCREENING_WINDOW_SIZE`: Screening window size (default: 12)
- `DEFAULT_NUM_SCREENING_KEEP_SIZE`: Papers to keep per round (default: 3)

### Prompt Config
- `MAX_PROMPT_FORMAT_RETRIES`: Max retries for prompt formatting (default: 10)
- `INITIAL_PROMPT_RETRY_TEMPERATURE`: Starting temperature for retries (default: 1.0)
- `MAX_PROMPT_RETRY_TEMPERATURE`: Max temperature for retries (default: 2.0)

## API Types

The system supports three API types:
- `0`: OpenAI API
- `1`: Azure OpenAI API
- `2`: Google Gemini API

Note: Structured outputs are only supported for OpenAI and Azure (types 0 and 1).

## Error Handling

The improved error handling includes:
1. Input validation before API calls
2. Exponential backoff retry logic
3. Empty response detection
4. Detailed error messages with context
5. Proper exception propagation

## Backwards Compatibility

All improvements maintain backwards compatibility with existing code:
- Legacy constants are aliased to new config values
- Function signatures remain unchanged
- Existing code continues to work without modifications

## Future Improvements

Potential areas for future enhancement:
- Separate prompt templates into dedicated module
- Add more comprehensive integration tests
- Add rate limiting support
- Add token usage tracking
- Add caching for repeated API calls
