"""
Unit tests for llm_client module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from llm_client import (
    LLMClient,
    OpenAIClient,
    AzureOpenAIClient,
    GoogleClient,
    create_llm_client
)


class TestLLMClientInterface(unittest.TestCase):
    """Test cases for LLMClient abstract base class."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that LLMClient cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            LLMClient()


class TestOpenAIClient(unittest.TestCase):
    """Test cases for OpenAIClient."""
    
    @patch('llm_client.OpenAI')
    def test_initialization(self, mock_openai):
        """Test that OpenAIClient initializes correctly."""
        client = OpenAIClient(
            api_key="test-key",
            base_url="https://api.openai.com",
            model="gpt-4"
        )
        
        mock_openai.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.openai.com"
        )
        self.assertEqual(client.model, "gpt-4")
    
    @patch('llm_client.OpenAI')
    def test_generate(self, mock_openai):
        """Test text generation."""
        # Setup mock
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create client and generate
        client = OpenAIClient(api_key="test-key", model="gpt-4")
        result = client.generate("Test prompt", temperature=0.7)
        
        self.assertEqual(result, "Generated text")
        mock_client.chat.completions.create.assert_called_once()


class TestAzureOpenAIClient(unittest.TestCase):
    """Test cases for AzureOpenAIClient."""
    
    @patch('llm_client.AzureOpenAI')
    def test_initialization(self, mock_azure):
        """Test that AzureOpenAIClient initializes correctly."""
        client = AzureOpenAIClient(
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com",
            model="gpt-4"
        )
        
        mock_azure.assert_called_once_with(
            azure_endpoint="https://test.openai.azure.com",
            api_key="test-key",
            api_version="2024-06-01"
        )
        self.assertEqual(client.model, "gpt-4")


class TestGoogleClient(unittest.TestCase):
    """Test cases for GoogleClient."""
    
    @patch('llm_client.genai.Client')
    def test_initialization(self, mock_genai):
        """Test that GoogleClient initializes correctly."""
        client = GoogleClient(
            api_key="test-key",
            model="gemini-1.5-pro"
        )
        
        mock_genai.assert_called_once_with(api_key="test-key")
        self.assertEqual(client.model, "gemini-1.5-pro")


class TestCreateLLMClient(unittest.TestCase):
    """Test cases for create_llm_client factory function."""
    
    @patch('llm_client.OpenAI')
    def test_create_openai_client(self, mock_openai):
        """Test creating OpenAI client."""
        client = create_llm_client(
            provider="openai",
            api_key="test-key",
            model="gpt-4"
        )
        
        self.assertIsInstance(client, OpenAIClient)
    
    @patch('llm_client.AzureOpenAI')
    def test_create_azure_client(self, mock_azure):
        """Test creating Azure client."""
        client = create_llm_client(
            provider="azure",
            api_key="test-key",
            model="gpt-4",
            base_url="https://test.openai.azure.com"
        )
        
        self.assertIsInstance(client, AzureOpenAIClient)
    
    @patch('llm_client.genai.Client')
    def test_create_google_client(self, mock_genai):
        """Test creating Google client."""
        client = create_llm_client(
            provider="google",
            api_key="test-key",
            model="gemini-1.5-pro"
        )
        
        self.assertIsInstance(client, GoogleClient)
    
    def test_create_unknown_provider(self):
        """Test that unknown provider raises ValueError."""
        with self.assertRaises(ValueError) as context:
            create_llm_client(
                provider="unknown",
                api_key="test-key",
                model="test"
            )
        
        self.assertIn("Unknown provider", str(context.exception))
    
    @patch('llm_client.AzureOpenAI')
    def test_azure_requires_base_url(self, mock_azure):
        """Test that Azure provider requires base_url."""
        with self.assertRaises(ValueError) as context:
            create_llm_client(
                provider="azure",
                api_key="test-key",
                model="gpt-4"
            )
        
        self.assertIn("base_url", str(context.exception).lower())
    
    @patch('llm_client.OpenAI')
    def test_case_insensitive_provider(self, mock_openai):
        """Test that provider name is case-insensitive."""
        client1 = create_llm_client(provider="OpenAI", api_key="key", model="gpt-4")
        client2 = create_llm_client(provider="OPENAI", api_key="key", model="gpt-4")
        
        self.assertIsInstance(client1, OpenAIClient)
        self.assertIsInstance(client2, OpenAIClient)


if __name__ == '__main__':
    unittest.main()
