"""
Configuration module for MOOSE-Chem.

This module centralizes all configuration constants and provides
validation for configuration values.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    """Configuration for LLM API calls."""
    
    # Maximum completion tokens based on model type
    MAX_COMPLETION_TOKENS_CLAUDE_HAIKU: int = 4096
    MAX_COMPLETION_TOKENS_DEFAULT: int = 8192
    
    # Retry configuration
    MAX_RETRIES: int = 3
    INITIAL_RETRY_DELAY: float = 0.5  # seconds
    MAX_RETRY_DELAY: float = 5.0  # seconds
    BACKOFF_MULTIPLIER: float = 2.0
    
    # API types
    API_TYPE_OPENAI: int = 0
    API_TYPE_AZURE: int = 1
    API_TYPE_GOOGLE: int = 2
    
    # Temperature constraints
    MIN_TEMPERATURE: float = 0.0
    MAX_TEMPERATURE: float = 2.0
    
    # System prompts
    DEFAULT_SYSTEM_PROMPT: str = "You are a helpful assistant."
    SCIENTIST_SYSTEM_PROMPT: str = (
        "You are a helpful and knowledgeable scientist. "
        "Provide your response in the exact format requested."
    )


@dataclass
class HypothesisGenerationConfig:
    """Configuration for hypothesis generation."""
    
    # Discipline for hypothesis generation
    DISCIPLINE: str = "AI for Materials Science"
    
    # Mutation guidance
    MUTATION_CUSTOM_GUIDE: str = (
        "You should be careful on adopting ML methods as the novel content of the "
        "mutation, since currently we are using ML examples to illustrate the derivation "
        "of hypothesis from research background and inspirations, and now it seems that "
        "the ML concepts can therefore easily be abused."
    )
    
    # Hypothesis generation guidance
    HYPOTHESIS_GENERATION_CUSTOM_GUIDE: str = """
Please formulate a detailed, valid, feasible, novel, and constructive hypothesis, primarily 
emphasizing the methodology and mechanistic design. Each step in your hypothesis should be 
clear, precise, and free from ambiguity. The expected performance or potential impact of the 
hypothesis is not the main focus and should be mentioned minimally.

The generated hypothesis must not exceed 600 words, but it can be shorter if conciseness 
doesn't sacrifice essential details (normally 600 words should be more than enough to describe 
the essential idea and essential details of a hypothesis). The hypothesis must remain concise 
yet comprehensive, clearly describing all essential aspects of data representation, model 
architecture and training, while avoiding unnecessary verbosity or redundant explanations of 
common scientific knowledge. If your initial hypothesis exceeds 600 words, try to compress it 
until it meets this constraint without omitting any critical information.
"""
    
    # Refinement iterations
    DEFAULT_NUM_ITERS_SELF_REFINE: int = 3
    DEFAULT_NUM_MUTATIONS: int = 3
    
    # Screening parameters
    DEFAULT_NUM_SCREENING_WINDOW_SIZE: int = 12
    DEFAULT_NUM_SCREENING_KEEP_SIZE: int = 3


@dataclass
class PromptConfig:
    """Configuration for prompt templates."""
    
    # Max number of retries for prompt formatting
    MAX_PROMPT_FORMAT_RETRIES: int = 10
    
    # Initial temperature for prompt retries
    INITIAL_PROMPT_RETRY_TEMPERATURE: float = 1.0
    MAX_PROMPT_RETRY_TEMPERATURE: float = 2.0
    PROMPT_RETRY_TEMPERATURE_INCREMENT: float = 0.25


# Global configuration instances
llm_config = LLMConfig()
hypothesis_config = HypothesisGenerationConfig()
prompt_config = PromptConfig()


def validate_temperature(temperature: float) -> None:
    """
    Validate temperature value.
    
    Args:
        temperature: Temperature value to validate
        
    Raises:
        ValueError: If temperature is out of valid range
    """
    if not (llm_config.MIN_TEMPERATURE <= temperature <= llm_config.MAX_TEMPERATURE):
        raise ValueError(
            f"temperature must be between {llm_config.MIN_TEMPERATURE} and "
            f"{llm_config.MAX_TEMPERATURE}, got {temperature}"
        )


def validate_api_type(api_type: int) -> None:
    """
    Validate API type.
    
    Args:
        api_type: API type to validate
        
    Raises:
        ValueError: If API type is not recognized
    """
    valid_types = [
        llm_config.API_TYPE_OPENAI,
        llm_config.API_TYPE_AZURE,
        llm_config.API_TYPE_GOOGLE
    ]
    if api_type not in valid_types:
        raise ValueError(
            f"api_type must be one of {valid_types}, got {api_type}"
        )


def get_max_completion_tokens(model_name: str) -> int:
    """
    Determine max completion tokens based on model name.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Maximum completion tokens for the model
    """
    if "claude-3-haiku" in model_name.lower():
        return llm_config.MAX_COMPLETION_TOKENS_CLAUDE_HAIKU
    return llm_config.MAX_COMPLETION_TOKENS_DEFAULT


def calculate_retry_delay(trial: int) -> float:
    """
    Calculate exponential backoff delay for retries.
    
    Args:
        trial: Current trial number (0-indexed)
        
    Returns:
        Delay in seconds
    """
    delay = llm_config.INITIAL_RETRY_DELAY * (llm_config.BACKOFF_MULTIPLIER ** trial)
    return min(delay, llm_config.MAX_RETRY_DELAY)
