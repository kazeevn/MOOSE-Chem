"""
Text Artifact Cleaning Module

This module provides functions to clean control codes and special Unicode characters
from text, particularly for processing abstracts from academic papers.

Based on analysis of inspiration_corpus/wyformer_v0.2.json which revealed:
- Newlines (U+000A): 106 occurrences
- En dash (U+2013): 6 occurrences  
- Unicode quotes (U+2018, U+2019, U+201C, U+201D): 19 occurrences
- Thin space (U+2009): 4 occurrences
- Em dash (U+2014): 2 occurrences
- Copyright symbol (U+00A9): 1 occurrence
- Various other control characters and special Unicode

See ABSTRACT_ARTIFACTS_LIST.md for full documentation.
"""

import re


def sanitize_abstract_text(text):
    """
    Sanitize text by removing control codes and normalizing Unicode characters.
    
    This function handles common artifacts found in academic abstracts:
    - Control characters (newlines, tabs, carriage returns)
    - Unicode punctuation (em/en dashes, curly quotes)
    - Special spaces (non-breaking, thin spaces)
    - Copyright and other special symbols
    
    Args:
        text (str): The input text to sanitize
    
    Returns:
        str: Cleaned text with artifacts removed/normalized
    
    Examples:
        >>> sanitize_abstract_text("Hello\\nWorld")
        'Hello World'
        >>> sanitize_abstract_text("It's—a test")
        "It's-a test"
        >>> sanitize_abstract_text('"Quoted text"')
        '"Quoted text"'
    """
    if not text:
        return text
    
    # Step 1: Remove NULL bytes and other dangerous control characters
    text = text.replace('\x00', '')
    
    # Step 2: Normalize newlines, carriage returns, and tabs to spaces
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\t', ' ')
    
    # Step 3: Replace Unicode dashes with ASCII equivalents
    text = text.replace('\u2010', '-')  # hyphen
    text = text.replace('\u2011', '-')  # non-breaking hyphen
    text = text.replace('\u2012', '-')  # figure dash
    text = text.replace('\u2013', '-')  # en dash
    text = text.replace('\u2014', '-')  # em dash
    text = text.replace('\u2015', '-')  # horizontal bar
    
    # Step 3b: Replace ellipsis and other punctuation
    text = text.replace('\u2026', '...')  # horizontal ellipsis
    
    # Step 4: Replace Unicode quotes with ASCII quotes
    text = text.replace('\u2018', "'")  # left single quotation mark
    text = text.replace('\u2019', "'")  # right single quotation mark
    text = text.replace('\u201a', "'")  # single low-9 quotation mark
    text = text.replace('\u201b', "'")  # single high-reversed-9 quotation mark
    text = text.replace('\u201c', '"')  # left double quotation mark
    text = text.replace('\u201d', '"')  # right double quotation mark
    text = text.replace('\u201e', '"')  # double low-9 quotation mark
    text = text.replace('\u201f', '"')  # double high-reversed-9 quotation mark
    
    # Step 5: Replace various space characters with regular space
    text = text.replace('\u00a0', ' ')  # non-breaking space
    text = text.replace('\u2002', ' ')  # en space
    text = text.replace('\u2003', ' ')  # em space
    text = text.replace('\u2004', ' ')  # three-per-em space
    text = text.replace('\u2005', ' ')  # four-per-em space
    text = text.replace('\u2006', ' ')  # six-per-em space
    text = text.replace('\u2007', ' ')  # figure space
    text = text.replace('\u2008', ' ')  # punctuation space
    text = text.replace('\u2009', ' ')  # thin space
    text = text.replace('\u200a', ' ')  # hair space
    text = text.replace('\u202f', ' ')  # narrow no-break space
    text = text.replace('\u205f', ' ')  # medium mathematical space
    
    # Step 6: Remove other problematic characters
    text = text.replace('\u00a9', '(c)')  # copyright symbol
    text = text.replace('\u00ae', '(R)')  # registered trademark
    text = text.replace('\u2122', '(TM)')  # trademark
    
    # Step 7: Remove other control characters (U+0000 to U+001F and U+007F to U+009F)
    # except those already handled (tab, newline, carriage return)
    text = ''.join(char for char in text if ord(char) >= 32 or char in ' ')
    
    # Step 8: Collapse multiple spaces into single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Step 9: Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def sanitize_title_abstract_pair(title, abstract):
    """
    Sanitize both title and abstract in a pair.
    
    Args:
        title (str): Paper title
        abstract (str): Paper abstract
    
    Returns:
        tuple: (cleaned_title, cleaned_abstract)
    """
    clean_title = sanitize_abstract_text(title) if title else title
    clean_abstract = sanitize_abstract_text(abstract) if abstract else abstract
    return clean_title, clean_abstract


def sanitize_corpus(corpus_data):
    """
    Sanitize an entire corpus of title-abstract pairs.
    
    Args:
        corpus_data (list): List of [title, abstract] pairs
    
    Returns:
        list: List of [cleaned_title, cleaned_abstract] pairs
    """
    sanitized_corpus = []
    for entry in corpus_data:
        if len(entry) >= 2:
            clean_title, clean_abstract = sanitize_title_abstract_pair(entry[0], entry[1])
            sanitized_corpus.append([clean_title, clean_abstract])
        else:
            # Keep incomplete entries as-is
            sanitized_corpus.append(entry)
    return sanitized_corpus


if __name__ == "__main__":
    # Test the sanitization function
    test_cases = [
        "Hello\nWorld",
        "It's—a test",
        '"Quoted text"',
        "En–dash and em—dash",
        "Thin\u2009space",
        "Copyright © 2024",
        "Multiple\n\n\nnewlines",
        "Tab\there",
        "Non-breaking\u00a0space",
    ]
    
    print("Testing sanitize_abstract_text():")
    print("-" * 60)
    for test in test_cases:
        cleaned = sanitize_abstract_text(test)
        print(f"Input:  {repr(test)}")
        print(f"Output: {repr(cleaned)}")
        print()
