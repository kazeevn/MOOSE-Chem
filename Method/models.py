"""
Pydantic models for MOOSE-Chem data structures.

This module defines strongly-typed data models using Pydantic for better
type safety, validation, and documentation of data structures used throughout
the application.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any


class Hypothesis(BaseModel):
    """A scientific research hypothesis with associated metadata."""
    
    text: str = Field(
        description="The hypothesis text"
    )
    reasoning: str = Field(
        default="",
        description="The reasoning process behind the hypothesis"
    )
    feedback: str = Field(
        default="",
        description="Feedback on the hypothesis from evaluation"
    )
    scores: List[float] = Field(
        default_factory=list,
        description="Evaluation scores for different aspects"
    )
    
    @validator('scores')
    def validate_scores(cls, v):
        """Ensure all scores are between 0 and 10."""
        for score in v:
            if not (0 <= score <= 10):
                raise ValueError(f"Score {score} must be between 0 and 10")
        return v
    
    @property
    def average_score(self) -> Optional[float]:
        """Calculate the average score."""
        if not self.scores:
            return None
        return sum(self.scores) / len(self.scores)


class Inspiration(BaseModel):
    """An inspiration source (typically a research paper)."""
    
    title: str = Field(
        description="Title of the inspiration source"
    )
    abstract: str = Field(
        description="Abstract or summary of the inspiration source"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Reason why this is considered an inspiration"
    )
    
    @validator('title', 'abstract')
    def validate_not_empty(cls, v):
        """Ensure title and abstract are not empty."""
        if not v or not v.strip():
            raise ValueError("Title and abstract cannot be empty")
        return v.strip()


class ResearchBackground(BaseModel):
    """Research background information including question and survey."""
    
    question: str = Field(
        description="The research question being addressed"
    )
    survey: Optional[str] = Field(
        default=None,
        description="Background survey or literature review"
    )
    note: Optional[str] = Field(
        default=None,
        description="Additional notes about the research background"
    )
    
    @validator('question')
    def validate_question(cls, v):
        """Ensure question is not empty."""
        if not v or not v.strip():
            raise ValueError("Research question cannot be empty")
        return v.strip()


class HypothesisMutation(BaseModel):
    """A mutation or variation of a hypothesis with its refinement history."""
    
    mutation_id: str = Field(
        description="Identifier for this mutation (e.g., '0', '1', 'recom')"
    )
    hypotheses: List[Hypothesis] = Field(
        default_factory=list,
        description="List of hypothesis refinements in this mutation line"
    )
    
    def get_latest_hypothesis(self) -> Optional[Hypothesis]:
        """Get the most recent hypothesis in this mutation line."""
        if not self.hypotheses:
            return None
        return self.hypotheses[-1]


class EvaluationResult(BaseModel):
    """Result of evaluating a hypothesis."""
    
    hypothesis: str = Field(
        description="The evaluated hypothesis"
    )
    average_score: float = Field(
        description="Average evaluation score"
    )
    scores: List[float] = Field(
        description="Individual aspect scores"
    )
    core_inspiration_title: str = Field(
        description="Title of the core inspiration used"
    )
    round_id: int = Field(
        description="Round number in the generation process"
    )
    mutation_path: List[str] = Field(
        description="Path of mutations that led to this hypothesis"
    )
    
    @validator('average_score')
    def validate_average_score(cls, v):
        """Ensure average score is valid."""
        if not (0 <= v <= 10):
            raise ValueError(f"Average score {v} must be between 0 and 10")
        return v


class HypothesisCollection(BaseModel):
    """A collection of hypotheses organized by background question and inspiration."""
    
    background_question: str = Field(
        description="The research background question"
    )
    hypotheses_by_inspiration: Dict[str, List[HypothesisMutation]] = Field(
        default_factory=dict,
        description="Hypotheses organized by core inspiration title"
    )
    
    def add_hypothesis(
        self,
        inspiration_title: str,
        mutation_id: str,
        hypothesis: Hypothesis
    ) -> None:
        """Add a hypothesis to the collection."""
        if inspiration_title not in self.hypotheses_by_inspiration:
            self.hypotheses_by_inspiration[inspiration_title] = []
        
        # Find or create the mutation
        mutation = None
        for m in self.hypotheses_by_inspiration[inspiration_title]:
            if m.mutation_id == mutation_id:
                mutation = m
                break
        
        if mutation is None:
            mutation = HypothesisMutation(mutation_id=mutation_id)
            self.hypotheses_by_inspiration[inspiration_title].append(mutation)
        
        mutation.hypotheses.append(hypothesis)


class PromptTemplate(BaseModel):
    """A template for generating prompts."""
    
    name: str = Field(
        description="Name/identifier for this prompt template"
    )
    template: str = Field(
        description="The prompt template with placeholders"
    )
    required_fields: List[str] = Field(
        default_factory=list,
        description="Required fields that must be provided"
    )
    
    def format(self, **kwargs) -> str:
        """
        Format the template with provided values.
        
        Args:
            **kwargs: Values to substitute in the template
            
        Returns:
            Formatted prompt string
            
        Raises:
            ValueError: If required fields are missing
        """
        missing = [f for f in self.required_fields if f not in kwargs]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        return self.template.format(**kwargs)


class APIResponse(BaseModel):
    """Generic API response wrapper."""
    
    success: bool = Field(
        description="Whether the API call was successful"
    )
    data: Any = Field(
        default=None,
        description="Response data"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if success=False"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the response"
    )
