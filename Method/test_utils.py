"""
Unit tests for the utils module, focusing on LLM API interaction improvements.

Tests cover:
- Configuration validation
- Error handling and retry logic
- Input validation
- Response validation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from config import (
    llm_config,
    get_max_completion_tokens,
    calculate_retry_delay,
)
from utils import (
    llm_generation,
    llm_generation_structured,
    HypothesisResponse,
    RefinedHypothesisResponse,
    EvaluationResponse,
)

# Alias for backwards compatibility with tests
LLMConfig = llm_config
_get_max_completion_tokens = get_max_completion_tokens
_calculate_retry_delay = calculate_retry_delay


class TestLLMConfig(unittest.TestCase):
    """Test LLM configuration constants."""
    
    def test_max_retries_positive(self):
        """Ensure MAX_RETRIES is positive."""
        self.assertGreater(LLMConfig.MAX_RETRIES, 0)
    
    def test_retry_delays_valid(self):
        """Ensure retry delay values are sensible."""
        self.assertGreater(LLMConfig.INITIAL_RETRY_DELAY, 0)
        self.assertGreater(LLMConfig.MAX_RETRY_DELAY, LLMConfig.INITIAL_RETRY_DELAY)
        self.assertGreater(LLMConfig.BACKOFF_MULTIPLIER, 1.0)
    
    def test_max_completion_tokens_positive(self):
        """Ensure token limits are positive."""
        self.assertGreater(LLMConfig.MAX_COMPLETION_TOKENS_CLAUDE_HAIKU, 0)
        self.assertGreater(LLMConfig.MAX_COMPLETION_TOKENS_DEFAULT, 0)


class TestGetMaxCompletionTokens(unittest.TestCase):
    """Test token limit determination based on model name."""
    
    def test_claude_haiku_model(self):
        """Claude Haiku models should use smaller token limit."""
        result = _get_max_completion_tokens("claude-3-haiku-20240307")
        self.assertEqual(result, LLMConfig.MAX_COMPLETION_TOKENS_CLAUDE_HAIKU)
    
    def test_other_models(self):
        """Other models should use default token limit."""
        models = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "gemini-pro"]
        for model in models:
            result = _get_max_completion_tokens(model)
            self.assertEqual(result, LLMConfig.MAX_COMPLETION_TOKENS_DEFAULT)


class TestCalculateRetryDelay(unittest.TestCase):
    """Test exponential backoff calculation."""
    
    def test_first_retry(self):
        """First retry should use initial delay."""
        delay = _calculate_retry_delay(0)
        self.assertEqual(delay, LLMConfig.INITIAL_RETRY_DELAY)
    
    def test_exponential_growth(self):
        """Delays should grow exponentially."""
        delay1 = _calculate_retry_delay(1)
        delay2 = _calculate_retry_delay(2)
        expected_ratio = LLMConfig.BACKOFF_MULTIPLIER
        self.assertAlmostEqual(delay2 / delay1, expected_ratio, places=2)
    
    def test_max_delay_cap(self):
        """Delays should not exceed MAX_RETRY_DELAY."""
        for trial in range(10):
            delay = _calculate_retry_delay(trial)
            self.assertLessEqual(delay, LLMConfig.MAX_RETRY_DELAY)


class TestLLMGenerationValidation(unittest.TestCase):
    """Test input validation for llm_generation."""
    
    def test_empty_prompt(self):
        """Empty prompt should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            llm_generation("", "gpt-4", Mock(), temperature=1.0)
        self.assertIn("Invalid prompt", str(context.exception))
    
    def test_none_prompt(self):
        """None prompt should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            llm_generation(None, "gpt-4", Mock(), temperature=1.0)
        self.assertIn("Invalid prompt", str(context.exception))
    
    def test_invalid_prompt_type(self):
        """Non-string prompt should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            llm_generation(123, "gpt-4", Mock(), temperature=1.0)
        self.assertIn("Invalid prompt", str(context.exception))
    
    def test_empty_model_name(self):
        """Empty model name should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            llm_generation("test prompt", "", Mock(), temperature=1.0)
        self.assertIn("model_name cannot be empty", str(context.exception))
    
    def test_temperature_too_low(self):
        """Temperature below 0 should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            llm_generation("test prompt", "gpt-4", Mock(), temperature=-0.1)
        self.assertIn("temperature must be between", str(context.exception))
    
    def test_temperature_too_high(self):
        """Temperature above 2 should raise ValueError."""
        with self.assertRaises(ValueError) as context:
            llm_generation("test prompt", "gpt-4", Mock(), temperature=2.1)
        self.assertIn("temperature must be between", str(context.exception))


class TestLLMGenerationRetry(unittest.TestCase):
    """Test retry logic for llm_generation."""
    
    @patch('utils.time.sleep')
    def test_retry_on_failure(self, mock_sleep):
        """Should retry on API failures."""
        mock_client = Mock()
        # First two calls fail, third succeeds
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            Mock(choices=[Mock(message=Mock(content="Success"))])
        ]
        
        result = llm_generation("test prompt", "gpt-4", mock_client, api_type=0)
        
        self.assertEqual(result, "Success")
        self.assertEqual(mock_client.chat.completions.create.call_count, 3)
        # Should have slept twice (before retry 2 and 3)
        self.assertEqual(mock_sleep.call_count, 2)
    
    @patch('utils.time.sleep')
    def test_all_retries_fail(self, mock_sleep):
        """Should raise exception if all retries fail."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Persistent Error")
        
        with self.assertRaises(Exception) as context:
            llm_generation("test prompt", "gpt-4", mock_client, api_type=0)
        
        self.assertIn("Failed to get generation after", str(context.exception))
        self.assertIn("Persistent Error", str(context.exception))
        self.assertEqual(mock_client.chat.completions.create.call_count, LLMConfig.MAX_RETRIES)
    
    def test_empty_response_treated_as_error(self):
        """Empty response from LLM should be treated as error."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="   "))]  # Only whitespace
        )
        
        with self.assertRaises(Exception) as context:
            llm_generation("test prompt", "gpt-4", mock_client, api_type=0)
        # Should fail after retries with message about empty response
        self.assertIn("Empty response", str(context.exception))


class TestLLMGenerationStructuredValidation(unittest.TestCase):
    """Test input validation for llm_generation_structured."""
    
    def test_empty_prompt(self):
        """Empty prompt should raise ValueError."""
        with self.assertRaises(ValueError):
            llm_generation_structured("", "gpt-4", Mock(), HypothesisResponse)
    
    def test_invalid_temperature(self):
        """Invalid temperature should raise ValueError."""
        with self.assertRaises(ValueError):
            llm_generation_structured("test", "gpt-4", Mock(), HypothesisResponse, temperature=3.0)
    
    def test_unsupported_api_type(self):
        """Unsupported API type should raise RuntimeError after retries."""
        with self.assertRaises(RuntimeError) as context:
            llm_generation_structured("test", "gpt-4", Mock(), HypothesisResponse, api_type=2)
        # Should mention that the API type is not supported
        self.assertIn("not implemented", str(context.exception))


class TestPydanticModels(unittest.TestCase):
    """Test Pydantic model definitions."""
    
    def test_hypothesis_response_fields(self):
        """HypothesisResponse should have required fields."""
        response = HypothesisResponse(
            reasoning_process="Test reasoning",
            hypothesis="Test hypothesis"
        )
        self.assertEqual(response.reasoning_process, "Test reasoning")
        self.assertEqual(response.hypothesis, "Test hypothesis")
    
    def test_refined_hypothesis_response_fields(self):
        """RefinedHypothesisResponse should have required fields."""
        response = RefinedHypothesisResponse(
            reasoning_process="Test reasoning",
            refined_hypothesis="Test refined hypothesis"
        )
        self.assertEqual(response.reasoning_process, "Test reasoning")
        self.assertEqual(response.refined_hypothesis, "Test refined hypothesis")
    
    def test_evaluation_response_validation(self):
        """EvaluationResponse should validate score range."""
        # Valid scores (0-5)
        for score in range(6):
            response = EvaluationResponse(
                matched_score=score,
                reason="Test reason"
            )
            self.assertEqual(response.matched_score, score)
        
        # Invalid scores should fail
        with self.assertRaises(Exception):  # Pydantic validation error
            EvaluationResponse(matched_score=6, reason="Test")
        
        with self.assertRaises(Exception):
            EvaluationResponse(matched_score=-1, reason="Test")


if __name__ == '__main__':
    unittest.main()
