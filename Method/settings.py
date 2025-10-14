"""
Configuration management for MOOSE-Chem application using Pydantic Settings.

This module provides a centralized configuration system using Pydantic Settings,
allowing configuration to be loaded from environment variables or .env files.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class LLMSettings(BaseSettings):
    """Settings for LLM provider and model configuration."""
    
    provider: str = Field(
        default="openai",
        description="LLM provider: 'openai', 'azure', or 'google'"
    )
    model: str = Field(
        default="gpt-4.1-2025-04-14",
        description="Model name to use for generation"
    )
    api_key: str = Field(
        default="",
        description="API key for the LLM provider"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Base URL for API endpoint (optional)"
    )
    temperature: float = Field(
        default=1.0,
        description="Temperature for generation",
        ge=0.0,
        le=2.0
    )


class DataSettings(BaseSettings):
    """Settings for data paths and corpus configuration."""
    
    inspiration_corpus: str = Field(
        default="inspiration_corpus/default.json",
        description="Path to inspiration corpus file"
    )
    research_background: str = Field(
        default="research_background/default.json",
        description="Path to research background file"
    )
    chem_annotation_path: str = Field(
        default="./Data/chem_research_2024.xlsx",
        description="Path to chemistry annotation data"
    )
    corpus_size: int = Field(
        default=150,
        description="Size of the inspiration corpus",
        ge=1
    )


class ExperimentSettings(BaseSettings):
    """Settings for experiment configuration."""
    
    name: str = Field(
        default="default_experiment",
        description="Name of the experiment"
    )
    checkpoint_dir: str = Field(
        default="./Checkpoints",
        description="Root directory for checkpoints"
    )
    
    @property
    def experiment_checkpoint_dir(self) -> str:
        """Get the full checkpoint directory path for this experiment."""
        return f"{self.checkpoint_dir}/{self.name}"


class HypothesisGenerationSettings(BaseSettings):
    """Settings specific to hypothesis generation."""
    
    num_mutations: int = Field(
        default=3,
        description="Number of mutations to generate",
        ge=1
    )
    num_itr_self_refine: int = Field(
        default=3,
        description="Number of self-refinement iterations",
        ge=1
    )
    num_self_explore_steps_each_line: int = Field(
        default=3,
        description="Number of self-exploration steps per mutation line",
        ge=1
    )
    num_screening_window_size: int = Field(
        default=12,
        description="Window size for screening",
        ge=1
    )
    num_screening_keep_size: int = Field(
        default=3,
        description="Number of hypotheses to keep after screening",
        ge=1
    )
    max_inspiration_search_steps: int = Field(
        default=3,
        description="Maximum number of inspiration search steps",
        ge=1
    )


class AppSettings(BaseSettings):
    """Main application settings that aggregate all configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter='__',
        env_prefix="MOOSE_"
    )
    
    llm: LLMSettings = Field(default_factory=LLMSettings)
    data: DataSettings = Field(default_factory=DataSettings)
    experiment: ExperimentSettings = Field(default_factory=ExperimentSettings)
    hypothesis: HypothesisGenerationSettings = Field(
        default_factory=HypothesisGenerationSettings
    )


# Global settings instance
settings = AppSettings()
