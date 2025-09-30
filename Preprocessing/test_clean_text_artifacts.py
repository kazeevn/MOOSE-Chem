"""
Unit tests for clean_text_artifacts module.

Tests the sanitization of control codes and Unicode artifacts in text,
particularly for processing abstracts from academic papers.
"""

import unittest
from clean_text_artifacts import (
    sanitize_abstract_text,
    sanitize_title_abstract_pair,
    sanitize_corpus
)


class TestSanitizeAbstractText(unittest.TestCase):
    """Test cases for sanitize_abstract_text function."""
    
    def test_newline_removal(self):
        """Test that newlines are replaced with spaces."""
        self.assertEqual(sanitize_abstract_text("Hello\nWorld"), "Hello World")
        self.assertEqual(sanitize_abstract_text("Line1\nLine2\nLine3"), "Line1 Line2 Line3")
    
    def test_tab_removal(self):
        """Test that tabs are replaced with spaces."""
        self.assertEqual(sanitize_abstract_text("Hello\tWorld"), "Hello World")
    
    def test_carriage_return_removal(self):
        """Test that carriage returns are replaced with spaces."""
        self.assertEqual(sanitize_abstract_text("Hello\rWorld"), "Hello World")
    
    def test_unicode_dashes(self):
        """Test that Unicode dashes are converted to ASCII hyphens."""
        self.assertEqual(sanitize_abstract_text("En\u2013dash"), "En-dash")
        self.assertEqual(sanitize_abstract_text("Em\u2014dash"), "Em-dash")
        self.assertEqual(sanitize_abstract_text("\u2010hyphen"), "-hyphen")
    
    def test_unicode_quotes(self):
        """Test that Unicode quotes are converted to ASCII quotes."""
        self.assertEqual(sanitize_abstract_text("\u2018Left single\u2019"), "'Left single'")
        self.assertEqual(sanitize_abstract_text("\u201cLeft double\u201d"), '"Left double"')
    
    def test_special_spaces(self):
        """Test that special Unicode spaces are converted to regular spaces."""
        self.assertEqual(sanitize_abstract_text("Non\u00a0breaking"), "Non breaking")
        self.assertEqual(sanitize_abstract_text("Thin\u2009space"), "Thin space")
        self.assertEqual(sanitize_abstract_text("En\u2002space"), "En space")
    
    def test_copyright_symbol(self):
        """Test that copyright symbol is converted to (c)."""
        self.assertEqual(sanitize_abstract_text("Copyright \u00a9 2024"), "Copyright (c) 2024")
    
    def test_trademark_symbols(self):
        """Test that trademark symbols are converted."""
        self.assertEqual(sanitize_abstract_text("Registered\u00ae"), "Registered(R)")
        self.assertEqual(sanitize_abstract_text("Trademark\u2122"), "Trademark(TM)")
    
    def test_multiple_spaces_collapsed(self):
        """Test that multiple consecutive spaces are collapsed to one."""
        self.assertEqual(sanitize_abstract_text("Too    many    spaces"), "Too many spaces")
        self.assertEqual(sanitize_abstract_text("Mixed\n\n\nspaces"), "Mixed spaces")
    
    def test_whitespace_stripping(self):
        """Test that leading and trailing whitespace is removed."""
        self.assertEqual(sanitize_abstract_text("  Hello World  "), "Hello World")
        self.assertEqual(sanitize_abstract_text("\n\tHello\n\t"), "Hello")
    
    def test_empty_string(self):
        """Test that empty string returns empty string."""
        self.assertEqual(sanitize_abstract_text(""), "")
    
    def test_none_input(self):
        """Test that None input returns None."""
        self.assertIsNone(sanitize_abstract_text(None))
    
    def test_clean_text_unchanged(self):
        """Test that clean text remains unchanged."""
        clean_text = "This is clean text with no artifacts."
        self.assertEqual(sanitize_abstract_text(clean_text), clean_text)
    
    def test_combined_artifacts(self):
        """Test text with multiple types of artifacts."""
        input_text = "Hello\nWorld\u2013test\u2019s \"quoted\"\u2009text"
        expected = 'Hello World-test\'s "quoted" text'
        self.assertEqual(sanitize_abstract_text(input_text), expected)


class TestSanitizeTitleAbstractPair(unittest.TestCase):
    """Test cases for sanitize_title_abstract_pair function."""
    
    def test_both_title_and_abstract(self):
        """Test sanitizing both title and abstract."""
        title = "Test\nTitle"
        abstract = "Test\u2013Abstract"
        clean_title, clean_abstract = sanitize_title_abstract_pair(title, abstract)
        self.assertEqual(clean_title, "Test Title")
        self.assertEqual(clean_abstract, "Test-Abstract")
    
    def test_none_values(self):
        """Test that None values are handled correctly."""
        clean_title, clean_abstract = sanitize_title_abstract_pair(None, None)
        self.assertIsNone(clean_title)
        self.assertIsNone(clean_abstract)


class TestSanitizeCorpus(unittest.TestCase):
    """Test cases for sanitize_corpus function."""
    
    def test_sanitize_corpus(self):
        """Test sanitizing an entire corpus."""
        corpus = [
            ["Title\n1", "Abstract\u20131"],
            ["Title 2", "Abstract 2"],
            ["Title\u20193", "Abstract\u201c3\u201d"]
        ]
        sanitized = sanitize_corpus(corpus)
        
        self.assertEqual(len(sanitized), 3)
        self.assertEqual(sanitized[0], ["Title 1", "Abstract-1"])
        self.assertEqual(sanitized[1], ["Title 2", "Abstract 2"])
        self.assertEqual(sanitized[2], ["Title'3", 'Abstract"3"'])
    
    def test_empty_corpus(self):
        """Test sanitizing an empty corpus."""
        self.assertEqual(sanitize_corpus([]), [])
    
    def test_incomplete_entries(self):
        """Test that incomplete entries are kept as-is."""
        corpus = [
            ["Only title"],
            ["Title", "Abstract"]
        ]
        sanitized = sanitize_corpus(corpus)
        self.assertEqual(len(sanitized), 2)
        self.assertEqual(sanitized[0], ["Only title"])
        self.assertEqual(sanitized[1], ["Title", "Abstract"])


class TestRealWorldExamples(unittest.TestCase):
    """Test cases based on actual artifacts found in wyformer_v0.2.json."""
    
    def test_crystalline_materials_abstract(self):
        """Test with a real abstract containing newlines."""
        input_text = ("We introduce CrystalFormer, a transformer-based autoregressive model\n"
                     "specifically designed for space group-controlled generation of crystalline\n"
                     "materials.")
        expected = ("We introduce CrystalFormer, a transformer-based autoregressive model "
                   "specifically designed for space group-controlled generation of crystalline "
                   "materials.")
        self.assertEqual(sanitize_abstract_text(input_text), expected)
    
    def test_functional_materials_abstract(self):
        """Test with a real abstract containing en dash."""
        input_text = "energy storage, catalysis and carbon capture1\u20133"
        expected = "energy storage, catalysis and carbon capture1-3"
        self.assertEqual(sanitize_abstract_text(input_text), expected)
    
    def test_alphafold_abstract(self):
        """Test with abstract containing multiple Unicode artifacts."""
        # U+2009 is thin space, U+2026 is ellipsis, U+2013 is en dash
        input_text = "AlphaFold\u200921 has spurred a revolution\u2026protein\u2013ligand"
        expected = "AlphaFold 21 has spurred a revolution...protein-ligand"
        self.assertEqual(sanitize_abstract_text(input_text), expected)


if __name__ == '__main__':
    unittest.main()
