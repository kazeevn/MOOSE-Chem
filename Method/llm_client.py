"""
LLM Client Abstraction Layer for MOOSE-Chem.

This module provides a unified interface for interacting with different LLM providers
(OpenAI, Azure OpenAI, Google Gemini). This abstraction allows for easy swapping of
models and providers without changing the core logic.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from openai import OpenAI, AzureOpenAI
from google import genai


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The input prompt text
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text string
        """
        pass
    
    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_format: Any,
        temperature: float = 1.0,
        **kwargs
    ) -> Any:
        """
        Generate structured output from a prompt.
        
        Args:
            prompt: The input prompt text
            response_format: The expected response format/schema
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Structured response object
        """
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client implementation."""
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: str = "gpt-4"
    ):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            base_url: Optional custom base URL
            model: Model name to use
        """
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def generate(
        self,
        prompt: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text using OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content
    
    def generate_structured(
        self,
        prompt: str,
        response_format: Any,
        temperature: float = 1.0,
        **kwargs
    ) -> Any:
        """Generate structured output using OpenAI API."""
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.parsed


class AzureOpenAIClient(LLMClient):
    """Azure OpenAI API client implementation."""
    
    def __init__(
        self,
        api_key: str,
        azure_endpoint: str,
        model: str = "gpt-4",
        api_version: str = "2024-06-01"
    ):
        """
        Initialize Azure OpenAI client.
        
        Args:
            api_key: Azure OpenAI API key
            azure_endpoint: Azure endpoint URL
            model: Model deployment name
            api_version: API version to use
        """
        self.model = model
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )
    
    def generate(
        self,
        prompt: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text using Azure OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content
    
    def generate_structured(
        self,
        prompt: str,
        response_format: Any,
        temperature: float = 1.0,
        **kwargs
    ) -> Any:
        """Generate structured output using Azure OpenAI API."""
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.parsed


class GoogleClient(LLMClient):
    """Google Gemini API client implementation."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-pro"
    ):
        """
        Initialize Google Gemini client.
        
        Args:
            api_key: Google API key
            model: Model name to use
        """
        self.model = model
        self.client = genai.Client(api_key=api_key)
    
    def generate(
        self,
        prompt: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text using Google Gemini API."""
        config = {
            "temperature": temperature,
        }
        if max_tokens:
            config["max_output_tokens"] = max_tokens
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )
        return response.text
    
    def generate_structured(
        self,
        prompt: str,
        response_format: Any,
        temperature: float = 1.0,
        **kwargs
    ) -> Any:
        """Generate structured output using Google Gemini API."""
        config = {
            "temperature": temperature,
            "response_mime_type": "application/json",
            "response_schema": response_format
        }
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )
        return response.text


def create_llm_client(
    provider: str,
    api_key: str,
    model: str,
    base_url: Optional[str] = None,
    **kwargs
) -> LLMClient:
    """
    Factory function to create an LLM client based on provider type.
    
    Args:
        provider: Provider name ('openai', 'azure', or 'google')
        api_key: API key for the provider
        model: Model name to use
        base_url: Optional base URL (for OpenAI/Azure)
        **kwargs: Additional provider-specific arguments
        
    Returns:
        Configured LLMClient instance
        
    Raises:
        ValueError: If provider is not recognized
    """
    provider = provider.lower()
    
    if provider == "openai":
        return OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    elif provider == "azure":
        if not base_url:
            raise ValueError("base_url (azure_endpoint) is required for Azure OpenAI")
        return AzureOpenAIClient(
            api_key=api_key,
            azure_endpoint=base_url,
            model=model,
            **kwargs
        )
    elif provider == "google":
        return GoogleClient(api_key=api_key, model=model)
    else:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Supported providers: openai, azure, google"
        )
