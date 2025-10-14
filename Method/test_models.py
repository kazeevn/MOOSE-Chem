"""
Unit tests for models module.
"""

import unittest
from models import (
    Hypothesis,
    Inspiration,
    ResearchBackground,
    HypothesisMutation,
    EvaluationResult,
    HypothesisCollection,
    PromptTemplate,
    APIResponse
)


class TestHypothesis(unittest.TestCase):
    """Test cases for Hypothesis model."""
    
    def test_basic_creation(self):
        """Test creating a basic hypothesis."""
        hyp = Hypothesis(
            text="We hypothesize that X causes Y",
            reasoning="Because of Z",
            feedback="Good hypothesis",
            scores=[8.0, 9.0, 7.5, 8.5]
        )
        
        self.assertEqual(hyp.text, "We hypothesize that X causes Y")
        self.assertEqual(len(hyp.scores), 4)
    
    def test_default_values(self):
        """Test that default values work correctly."""
        hyp = Hypothesis(text="Test hypothesis")
        
        self.assertEqual(hyp.text, "Test hypothesis")
        self.assertEqual(hyp.reasoning, "")
        self.assertEqual(hyp.feedback, "")
        self.assertEqual(hyp.scores, [])
    
    def test_average_score(self):
        """Test average score calculation."""
        hyp = Hypothesis(
            text="Test",
            scores=[8.0, 9.0, 7.0, 8.0]
        )
        
        self.assertEqual(hyp.average_score, 8.0)
    
    def test_average_score_empty(self):
        """Test average score with no scores."""
        hyp = Hypothesis(text="Test")
        self.assertIsNone(hyp.average_score)
    
    def test_score_validation(self):
        """Test that scores are validated to be between 0 and 10."""
        # Valid scores
        Hypothesis(text="Test", scores=[0.0, 5.0, 10.0])
        
        # Invalid scores
        with self.assertRaises(Exception):
            Hypothesis(text="Test", scores=[-1.0])
        with self.assertRaises(Exception):
            Hypothesis(text="Test", scores=[11.0])


class TestInspiration(unittest.TestCase):
    """Test cases for Inspiration model."""
    
    def test_basic_creation(self):
        """Test creating an inspiration."""
        insp = Inspiration(
            title="Paper Title",
            abstract="This is an abstract",
            reason="Relevant to our work"
        )
        
        self.assertEqual(insp.title, "Paper Title")
        self.assertEqual(insp.abstract, "This is an abstract")
        self.assertEqual(insp.reason, "Relevant to our work")
    
    def test_strips_whitespace(self):
        """Test that title and abstract whitespace is stripped."""
        insp = Inspiration(
            title="  Title  ",
            abstract="  Abstract  "
        )
        
        self.assertEqual(insp.title, "Title")
        self.assertEqual(insp.abstract, "Abstract")
    
    def test_empty_validation(self):
        """Test that empty title or abstract raises error."""
        with self.assertRaises(Exception):
            Inspiration(title="", abstract="Abstract")
        
        with self.assertRaises(Exception):
            Inspiration(title="Title", abstract="")


class TestResearchBackground(unittest.TestCase):
    """Test cases for ResearchBackground model."""
    
    def test_basic_creation(self):
        """Test creating a research background."""
        bg = ResearchBackground(
            question="What causes X?",
            survey="Previous work shows...",
            note="Important context"
        )
        
        self.assertEqual(bg.question, "What causes X?")
        self.assertEqual(bg.survey, "Previous work shows...")
        self.assertEqual(bg.note, "Important context")
    
    def test_optional_fields(self):
        """Test that survey and note are optional."""
        bg = ResearchBackground(question="What causes X?")
        
        self.assertEqual(bg.question, "What causes X?")
        self.assertIsNone(bg.survey)
        self.assertIsNone(bg.note)
    
    def test_empty_question(self):
        """Test that empty question raises error."""
        with self.assertRaises(Exception):
            ResearchBackground(question="")


class TestHypothesisMutation(unittest.TestCase):
    """Test cases for HypothesisMutation model."""
    
    def test_basic_creation(self):
        """Test creating a hypothesis mutation."""
        mut = HypothesisMutation(
            mutation_id="0",
            hypotheses=[
                Hypothesis(text="First version"),
                Hypothesis(text="Second version")
            ]
        )
        
        self.assertEqual(mut.mutation_id, "0")
        self.assertEqual(len(mut.hypotheses), 2)
    
    def test_get_latest_hypothesis(self):
        """Test getting the latest hypothesis."""
        mut = HypothesisMutation(
            mutation_id="0",
            hypotheses=[
                Hypothesis(text="First"),
                Hypothesis(text="Second"),
                Hypothesis(text="Third")
            ]
        )
        
        latest = mut.get_latest_hypothesis()
        self.assertEqual(latest.text, "Third")
    
    def test_get_latest_hypothesis_empty(self):
        """Test getting latest hypothesis when empty."""
        mut = HypothesisMutation(mutation_id="0")
        self.assertIsNone(mut.get_latest_hypothesis())


class TestEvaluationResult(unittest.TestCase):
    """Test cases for EvaluationResult model."""
    
    def test_basic_creation(self):
        """Test creating an evaluation result."""
        result = EvaluationResult(
            hypothesis="Test hypothesis",
            average_score=8.5,
            scores=[8.0, 9.0],
            core_inspiration_title="Paper Title",
            round_id=1,
            mutation_path=["0", "recom"]
        )
        
        self.assertEqual(result.average_score, 8.5)
        self.assertEqual(len(result.scores), 2)
    
    def test_score_validation(self):
        """Test that average score is validated."""
        # Valid score
        EvaluationResult(
            hypothesis="Test",
            average_score=5.0,
            scores=[5.0],
            core_inspiration_title="Title",
            round_id=1,
            mutation_path=[]
        )
        
        # Invalid scores
        with self.assertRaises(Exception):
            EvaluationResult(
                hypothesis="Test",
                average_score=-1.0,
                scores=[],
                core_inspiration_title="Title",
                round_id=1,
                mutation_path=[]
            )


class TestHypothesisCollection(unittest.TestCase):
    """Test cases for HypothesisCollection model."""
    
    def test_basic_creation(self):
        """Test creating a hypothesis collection."""
        coll = HypothesisCollection(
            background_question="What is X?"
        )
        
        self.assertEqual(coll.background_question, "What is X?")
        self.assertEqual(len(coll.hypotheses_by_inspiration), 0)
    
    def test_add_hypothesis(self):
        """Test adding hypotheses to collection."""
        coll = HypothesisCollection(background_question="What is X?")
        
        hyp1 = Hypothesis(text="First hypothesis")
        hyp2 = Hypothesis(text="Second hypothesis")
        
        coll.add_hypothesis("Paper 1", "0", hyp1)
        coll.add_hypothesis("Paper 1", "0", hyp2)
        
        self.assertEqual(len(coll.hypotheses_by_inspiration["Paper 1"]), 1)
        self.assertEqual(len(coll.hypotheses_by_inspiration["Paper 1"][0].hypotheses), 2)
    
    def test_add_hypothesis_different_mutations(self):
        """Test adding hypotheses with different mutation IDs."""
        coll = HypothesisCollection(background_question="What is X?")
        
        hyp1 = Hypothesis(text="Mutation 0")
        hyp2 = Hypothesis(text="Mutation 1")
        
        coll.add_hypothesis("Paper 1", "0", hyp1)
        coll.add_hypothesis("Paper 1", "1", hyp2)
        
        self.assertEqual(len(coll.hypotheses_by_inspiration["Paper 1"]), 2)


class TestPromptTemplate(unittest.TestCase):
    """Test cases for PromptTemplate model."""
    
    def test_basic_creation(self):
        """Test creating a prompt template."""
        template = PromptTemplate(
            name="test_template",
            template="Hello {name}, you are {age} years old.",
            required_fields=["name", "age"]
        )
        
        self.assertEqual(template.name, "test_template")
    
    def test_format_success(self):
        """Test formatting with all required fields."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}",
            required_fields=["name"]
        )
        
        result = template.format(name="Alice")
        self.assertEqual(result, "Hello Alice")
    
    def test_format_missing_fields(self):
        """Test that missing required fields raises error."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}",
            required_fields=["name"]
        )
        
        with self.assertRaises(ValueError) as context:
            template.format()
        
        self.assertIn("Missing required fields", str(context.exception))


class TestAPIResponse(unittest.TestCase):
    """Test cases for APIResponse model."""
    
    def test_success_response(self):
        """Test creating a success response."""
        response = APIResponse(
            success=True,
            data={"result": "value"}
        )
        
        self.assertTrue(response.success)
        self.assertEqual(response.data["result"], "value")
        self.assertIsNone(response.error)
    
    def test_error_response(self):
        """Test creating an error response."""
        response = APIResponse(
            success=False,
            error="Something went wrong"
        )
        
        self.assertFalse(response.success)
        self.assertEqual(response.error, "Something went wrong")


if __name__ == '__main__':
    unittest.main()
