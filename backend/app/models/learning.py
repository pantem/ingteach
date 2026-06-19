from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ModuleLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Module(BaseModel):
    id: str
    title: str
    description: str
    level: ModuleLevel
    order: int
    vocabulary: List[str]
    phrases: List[str]
    grammar_focus: str

class ConversationTopic(BaseModel):
    id: str
    module_id: str
    title: str
    description: str
    scenario: str
    key_phrases: List[str]
    vocabulary: List[str]

class ConversationMessage(BaseModel):
    role: str
    content: str
    audio_url: Optional[str] = None

class SpeechEvaluation(BaseModel):
    transcript: str
    accuracy_score: float
    pronunciation_score: float
    fluency_score: float
    feedback: str
    suggested_improvements: List[str]
    grammar_correction: Optional[str] = ""
    grammar_changes: Optional[List[str]] = []
    has_grammar_errors: Optional[bool] = False

class VerbTense(str, Enum):
    PRESENT_SIMPLE = "present_simple"
    PRESENT_CONTINUOUS = "present_continuous"
    PRESENT_PERFECT = "present_perfect"
    PAST_SIMPLE = "past_simple"
    PAST_CONTINUOUS = "past_continuous"
    FUTURE_SIMPLE = "future_simple"
    CONDITIONAL = "conditional"

class VerbConjugation(BaseModel):
    verb: str
    tense: VerbTense
    conjugations: dict
    examples: List[str]

class TestQuestion(BaseModel):
    id: str
    type: str
    question: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str

class ModuleTest(BaseModel):
    module_id: str
    questions: List[TestQuestion]
    passing_score: float = 0.7

class UserProgress(BaseModel):
    user_id: str
    completed_modules: List[str] = []
    current_module: str
    test_scores: dict = {}
    conversation_sessions: int = 0
    total_practice_time: int = 0

class TestSubmission(BaseModel):
    module_id: str
    answers: dict