"""
Unit tests for settings module.
"""

import unittest
import os
from settings import (
    LLMSettings,
    DataSettings,
    ExperimentSettings,
    HypothesisGenerationSettings,
    AppSettings
)


class TestLLMSettings(unittest.TestCase):
    """Test cases for LLMSettings."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = LLMSettings()
        self.assertEqual(settings.provider, "openai")
        self.assertEqual(settings.model, "gpt-4.1-2025-04-14")
        self.assertEqual(settings.temperature, 1.0)
    
    def test_custom_values(self):
        """Test that custom values can be set."""
        settings = LLMSettings(
            provider="azure",
            model="gpt-4",
            api_key="test-key",
            temperature=0.5
        )
        self.assertEqual(settings.provider, "azure")
        self.assertEqual(settings.model, "gpt-4")
        self.assertEqual(settings.api_key, "test-key")
        self.assertEqual(settings.temperature, 0.5)
    
    def test_temperature_validation(self):
        """Test that temperature is validated."""
        # Valid temperatures
        LLMSettings(temperature=0.0)
        LLMSettings(temperature=1.0)
        LLMSettings(temperature=2.0)
        
        # Invalid temperatures should raise validation error
        with self.assertRaises(Exception):
            LLMSettings(temperature=-0.1)
        with self.assertRaises(Exception):
            LLMSettings(temperature=2.1)


class TestDataSettings(unittest.TestCase):
    """Test cases for DataSettings."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = DataSettings()
        self.assertEqual(settings.inspiration_corpus, "inspiration_corpus/default.json")
        self.assertEqual(settings.corpus_size, 150)
    
    def test_custom_values(self):
        """Test that custom values can be set."""
        settings = DataSettings(
            inspiration_corpus="custom/path.json",
            corpus_size=200
        )
        self.assertEqual(settings.inspiration_corpus, "custom/path.json")
        self.assertEqual(settings.corpus_size, 200)


class TestExperimentSettings(unittest.TestCase):
    """Test cases for ExperimentSettings."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = ExperimentSettings()
        self.assertEqual(settings.name, "default_experiment")
        self.assertEqual(settings.checkpoint_dir, "./Checkpoints")
    
    def test_experiment_checkpoint_dir(self):
        """Test that experiment checkpoint directory is constructed correctly."""
        settings = ExperimentSettings(
            name="test_exp",
            checkpoint_dir="/tmp/checkpoints"
        )
        self.assertEqual(
            settings.experiment_checkpoint_dir,
            "/tmp/checkpoints/test_exp"
        )


class TestHypothesisGenerationSettings(unittest.TestCase):
    """Test cases for HypothesisGenerationSettings."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = HypothesisGenerationSettings()
        self.assertEqual(settings.num_mutations, 3)
        self.assertEqual(settings.num_itr_self_refine, 3)
        self.assertEqual(settings.max_inspiration_search_steps, 3)
    
    def test_validation(self):
        """Test that values are validated (must be >= 1)."""
        # Valid values
        HypothesisGenerationSettings(num_mutations=1)
        HypothesisGenerationSettings(num_mutations=10)
        
        # Invalid values should raise validation error
        with self.assertRaises(Exception):
            HypothesisGenerationSettings(num_mutations=0)


class TestAppSettings(unittest.TestCase):
    """Test cases for AppSettings."""
    
    def test_nested_settings(self):
        """Test that nested settings work correctly."""
        settings = AppSettings()
        self.assertIsInstance(settings.llm, LLMSettings)
        self.assertIsInstance(settings.data, DataSettings)
        self.assertIsInstance(settings.experiment, ExperimentSettings)
        self.assertIsInstance(settings.hypothesis, HypothesisGenerationSettings)
    
    def test_access_nested_values(self):
        """Test accessing nested values."""
        settings = AppSettings()
        self.assertEqual(settings.llm.provider, "openai")
        self.assertEqual(settings.data.corpus_size, 150)
        self.assertEqual(settings.experiment.name, "default_experiment")


if __name__ == '__main__':
    unittest.main()
