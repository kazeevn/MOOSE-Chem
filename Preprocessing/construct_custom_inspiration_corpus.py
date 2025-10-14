"""
Custom Inspiration Corpus Construction Script

This script builds a custom inspiration corpus for the MOOSE-Chem framework from two possible sources:

1. Excel Method (--method excel):
   Extract title-abstract pairs from Excel/XLS files containing research papers.
   Usage: python construct_custom_inspiration_corpus.py --method excel --raw_data_dir /path/to/excel/files

2. Semantic Scholar Method (--method semanticscholar):
   Retrieve references from a specific paper using the Semantic Scholar API.
   Usage: python construct_custom_inspiration_corpus.py --method semanticscholar --paper_id 'arXiv:1706.03762' --max_references 100

Supported paper ID formats for Semantic Scholar:
- DOI: 10.1038/nature14539
- ArXiv: arXiv:1706.03762 or 1706.03762  
- Semantic Scholar ID: 649def34f8be52c8b66281af98ae884c09aef38b
- Pubmed ID: PMID:19872477

Output: A JSON file containing [[title, abstract], [title, abstract], ...] format.
"""

import os
import json
import argparse
import re
import pandas as pd
from semanticscholar import SemanticScholar
import arxiv
from clean_text_artifacts import sanitize_abstract_text

# Compiled regex pattern to match arXiv DOIs like 10.48550/arXiv.XXXX.XXXXX
ARXIV_DOI_PATTERN = re.compile(r'10\.48550/arXiv\.(.+)', re.IGNORECASE)


def retrieve_from_arxiv(arxiv_id=None, doi=None):
    """
    Retrieve title and abstract from arXiv using either an arXiv ID or a DOI.
    
    Args:
        arxiv_id (str, optional): The arXiv ID (e.g., "1706.03762" or "arXiv:1706.03762")
        doi (str, optional): The DOI to search for
    
    Returns:
        tuple: (title, abstract) or (None, None) if not found
    
    Note:
        Exactly one of arxiv_id or doi must be provided.
    """
    if not arxiv_id and not doi:
        print("  Error: Either arxiv_id or doi must be provided")
        return None, None

    if arxiv_id and doi:
        print("  Error: Only one of arxiv_id or doi should be provided")
        return None, None

    try:
        client = arxiv.Client()
       
        if arxiv_id:
            # Clean the arXiv ID (remove "arXiv:" prefix if present)
            clean_id = arxiv_id.replace("arXiv:", "").strip()
            search = arxiv.Search(id_list=[clean_id])
            search_type = f"arXiv ID: {clean_id}"
        else:  # doi is provided
            search = arxiv.Search(query=f'doi:{doi}', max_results=1)
            search_type = f"DOI: {doi}"

        paper = next(client.results(search), None)

        if paper:
            title = paper.title.strip() if paper.title else None
            abstract = paper.summary.strip() if paper.summary else None
            
            # Sanitize title and abstract to remove control codes and artifacts
            if title:
                title = sanitize_abstract_text(title)
            if abstract:
                abstract = sanitize_abstract_text(abstract)
            
            print(f"  Retrieved from arXiv ({search_type}): {title}")
            return title, abstract

        print(f"  Paper not found on arXiv with {search_type}")
        return None, None
    except Exception as e:
        print(f"  Error retrieving from arXiv ({search_type}): {str(e)}")
        return None, None


def extract_arxiv_id_from_doi(doi):
    """
    Extract arXiv ID from DOI if it's an arXiv DOI.
    
    Args:
        doi (str): The DOI string (e.g., "10.48550/arXiv.2308.14920")
    
    Returns:
        str or None: The extracted arXiv ID (e.g., "2308.14920") or None if not an arXiv DOI
    """
    match = ARXIV_DOI_PATTERN.search(doi)
    if match:
        return match.group(1)
    return None


def build_inspiration_corpus_from_semanticscholar(
    paper_id, custom_inspiration_corpus_path, max_references=None):
    """
    Build an inspiration corpus using Semantic Scholar API to retrieve references of a given paper.
    
    Args:
        paper_id (str): The paper ID. Supported formats:
                       - DOI: "10.1038/nature14539"
                       - ArXiv: "arXiv:1706.03762" or "1706.03762"
                       - Semantic Scholar ID: "649def34f8be52c8b66281af98ae884c09aef38b"
                       - Pubmed ID: "PMID:19872477"
        custom_inspiration_corpus_path (str): Path to save the inspiration corpus JSON file
        max_references (int, optional): Maximum number of references to retrieve
    
    Returns:
        list: List of [title, abstract] pairs from the referenced papers
    """
    # Initialize Semantic Scholar client
    sch = SemanticScholar()
    
    try:
        # Get the paper details
        print(f"Retrieving paper details for: {paper_id}")
        paper = sch.get_paper(paper_id, fields=['title', 'abstract', 'references', 'references.title', 'references.abstract', 'references.externalIds'])
        
        if not paper:
            print(f"Paper with ID {paper_id} not found.")
            print("Supported ID formats:")
            print("  - DOI: 10.1038/nature14539")
            print("  - ArXiv: arXiv:1706.03762 or 1706.03762")
            print("  - Semantic Scholar ID: 649def34f8be52c8b66281af98ae884c09aef38b")
            print("  - Pubmed ID: PMID:19872477")
            return []
            
        print(f"Found paper: {paper.title}")
        print(f"Number of references: {len(paper.references) if paper.references else 0}")

        # Extract title-abstract pairs from references
        all_ttl_abs = []
        
        if paper.references:
            references_to_process = paper.references
            if max_references:
                references_to_process = paper.references[:max_references]
                print(f"Processing {len(references_to_process)} out of {len(paper.references)} references")
            
            for ref in references_to_process:
                title = ref.title.strip() if ref.title else None
                abstract = ref.abstract.strip() if ref.abstract else None
                
                # Sanitize title and abstract to remove control codes and artifacts
                if title:
                    title = sanitize_abstract_text(title)
                if abstract:
                    abstract = sanitize_abstract_text(abstract)
                
                # If title or abstract is missing, try to retrieve from arXiv
                if (not title or not abstract) and hasattr(ref, 'externalIds') and ref.externalIds:
                    if 'ArXiv' in ref.externalIds:
                        arxiv_id = ref.externalIds['ArXiv']
                        print(f"Missing title or abstract for reference, attempting arXiv fallback with ID: {arxiv_id}")
                        arxiv_title, arxiv_abstract = retrieve_from_arxiv(arxiv_id=arxiv_id)
                        
                        # Use arXiv data if available and missing in Semantic Scholar
                        if not title and arxiv_title:
                            title = arxiv_title
                        if not abstract and arxiv_abstract:
                            abstract = arxiv_abstract
                    
                    # If ArXiv ID is not available, try DOI fallback
                    elif 'DOI' in ref.externalIds and (not title or not abstract):
                        doi = ref.externalIds['DOI']
                        print(f"Missing title or abstract for reference, attempting DOI fallback with DOI: {doi}")
                        
                        # Check if DOI points to arXiv
                        arxiv_id_from_doi = extract_arxiv_id_from_doi(doi)
                        if arxiv_id_from_doi:
                            print(f"  DOI points to arXiv, extracted ID: {arxiv_id_from_doi}")
                            arxiv_title, arxiv_abstract = retrieve_from_arxiv(arxiv_id=arxiv_id_from_doi)
                        else:
                            # Use DOI in arXiv search query
                            print(f"  Searching arXiv by DOI: {doi}")
                            arxiv_title, arxiv_abstract = retrieve_from_arxiv(doi=doi)
                        
                        # Use arXiv data if available and missing in Semantic Scholar
                        if not title and arxiv_title:
                            title = arxiv_title
                        if not abstract and arxiv_abstract:
                            abstract = arxiv_abstract
                
                # Only add if both title and abstract are available
                if title and abstract:
                    all_ttl_abs.append([title, abstract])
                else:
                    print(f"Missing title or abstract: ID:{ref.paperId}; title: {ref.title}")
                    print(ref.externalIds)
            
            print(f"Successfully extracted {len(all_ttl_abs)} title-abstract pairs from references")
        else:
            print("No references found for this paper.")
            
        # Remove duplicates
        all_ttl_abs = list(dict.fromkeys(tuple(item) for item in all_ttl_abs))
        all_ttl_abs = [list(item) for item in all_ttl_abs]
        print(f"After removing duplicates: {len(all_ttl_abs)} unique title-abstract pairs")
        
        if all_ttl_abs:
            print(f"Example entry: {all_ttl_abs[0][0]}")
        
        # Save to JSON file
        with open(custom_inspiration_corpus_path, 'w', encoding='utf-8') as f:
            json.dump(all_ttl_abs, f, indent=4)
        
        print(f"Inspiration corpus saved to: {custom_inspiration_corpus_path}")
        return all_ttl_abs
        
    except Exception as e:
        print(f"Error retrieving paper or references: {str(e)}")
        print("Please check your internet connection and verify the paper ID format.")
        print("If the error persists, the paper might not be available in Semantic Scholar's database.")
        return []


# raw_data_dir: the directory where the xls/xlsx files are stored
def load_title_abstract(raw_data_dir, custom_inspiration_corpus_path):
    files = os.listdir(raw_data_dir)

    all_ttl_abs = []
    for cur_file in files:
        if not (cur_file.endswith('.xlsx') or cur_file.endswith('.xls')) or cur_file.startswith('.~'):
            continue 
        cur_file_full_path = os.path.join(raw_data_dir, cur_file)
        cur_ttl_abs = []
        print("cur_file_full_path:", cur_file_full_path)
        if cur_file.endswith('.xlsx'):
            df = pd.read_excel(cur_file_full_path)
        elif cur_file.endswith('.xls'):
            df = pd.read_excel(cur_file_full_path, engine='xlrd')
        else:
            print(f"Unsupported file format: {cur_file}")
            continue
        # Load xls file
        df = pd.read_excel(cur_file_full_path, engine='xlrd')
        nan_values = df.isna()
        cur_titles = df['Article Title'].tolist()
        cur_abstracts = df['Abstract'].tolist()
        assert len(cur_titles) == len(cur_abstracts), "Title and Abstract lengths do not match"
        for cur_id_ttl in range(len(cur_titles)):
            if nan_values['Article Title'][cur_id_ttl] or nan_values['Abstract'][cur_id_ttl]:
                continue
            # Sanitize title and abstract to remove control codes and artifacts
            title = sanitize_abstract_text(cur_titles[cur_id_ttl].strip())
            abstract = sanitize_abstract_text(cur_abstracts[cur_id_ttl].strip())
            cur_ttl_abs.append([title, abstract])
        print("len(cur_ttl_abs):", len(cur_ttl_abs))
        all_ttl_abs.extend(cur_ttl_abs)
    print("len(all_ttl_abs):", len(all_ttl_abs))
    # get rid of repeated title-abstract pairs
    # all_ttl_abs: list of [title, abstract]
    all_ttl_abs = list(dict.fromkeys(tuple(item) for item in all_ttl_abs))
    all_ttl_abs = [list(item) for item in all_ttl_abs]
    print("len(all_ttl_abs) (no superficial repetition):", len(all_ttl_abs))
    print("all_ttl_abs[0]:", all_ttl_abs[0])

    # save to json file
    with open(custom_inspiration_corpus_path, 'w', encoding='utf-8') as f:
        json.dump(all_ttl_abs, f, indent=4)
    return all_ttl_abs


def main():
    parser = argparse.ArgumentParser(description="Build a custom inspiration corpus from various sources")
    parser.add_argument("--method", type=str, choices=["excel", "semanticscholar"], default="excel", 
                       help="Method to build the inspiration corpus: 'excel' for Excel files, 'semanticscholar' for Semantic Scholar API")
    parser.add_argument("--raw_data_dir", type=str, default="", help="the path to the raw data directory (for excel method)")
    parser.add_argument("--paper_id", type=str, default="", 
                       help="Paper ID for Semantic Scholar API. Formats: DOI (10.1038/nature14539), ArXiv (arXiv:1706.03762), Semantic Scholar ID, or Pubmed ID (PMID:19872477) (for semanticscholar method)")
    parser.add_argument("--max_references", type=int, default=None, help="Maximum number of references to retrieve from Semantic Scholar (optional)")
    parser.add_argument("--custom_inspiration_corpus_path", type=str, default="./custom_inspiration_corpus.json", 
                       help="path to the custom inspiration corpus file (which is a json file, and will be used as input to the MOOSE-Chem framework)")
    args = parser.parse_args()

    if args.method == "excel":
        if not args.raw_data_dir:
            print("Error: --raw_data_dir is required for excel method")
            return
        load_title_abstract(args.raw_data_dir, args.custom_inspiration_corpus_path)
    elif args.method == "semanticscholar":
        if not args.paper_id:
            print("Error: --paper_id is required for semanticscholar method")
            print("Example usage:")
            print("  python construct_custom_inspiration_corpus.py --method semanticscholar --paper_id 'arXiv:1706.03762' --max_references 100")
            return
        build_inspiration_corpus_from_semanticscholar(args.paper_id, args.custom_inspiration_corpus_path, args.max_references)
    else:
        print(f"Error: Unknown method '{args.method}'")
        return

if __name__ == "__main__":
    main()
