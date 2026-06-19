from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.learning import (
    ConversationTopic, ConversationMessage, SpeechEvaluation,
    Module
)
from app.services.grammar import correct_sentence
from typing import List
import random
import re

class EvaluateRequest(BaseModel):
    transcript: str
    expected_phrases: List[str] = []

class CorrectRequest(BaseModel):
    text: str

router = APIRouter()

CONVERSATIONS = [
    ConversationTopic(
        id="conv-1", module_id="mod-1",
        title="Meeting a new colleague",
        description="Practice introducing yourself and greeting a new coworker",
        scenario="You are at a new job. Your manager introduces you to a colleague named Sarah.",
        key_phrases=["Hello, I'm...", "Nice to meet you", "Where are you from?",
                      "What do you do?", "Great to meet you too"],
        vocabulary=["colleague", "manager", "introduce", "department", "position"]
    ),
    ConversationTopic(
        id="conv-2", module_id="mod-2",
        title="Talking about your morning routine",
        description="Describe what you do every morning",
        scenario="Your friend asks about your typical morning routine before work.",
        key_phrases=["I usually wake up at...", "Then I have...", "After that I...",
                      "I always...", "I never..."],
        vocabulary=["routine", "usually", "often", "sometimes", "rarely"]
    ),
    ConversationTopic(
        id="conv-3", module_id="mod-3",
        title="Ordering at a restaurant",
        description="Practice ordering food and interacting with waitstaff",
        scenario="You are at a nice restaurant. The waiter comes to take your order.",
        key_phrases=["I would like...", "Could I have...?",
                      "What do you recommend?", "The bill, please.",
                      "Is there a vegetarian option?"],
        vocabulary=["appetizer", "main course", "dessert", "beverage", "waiter"]
    ),
    ConversationTopic(
        id="conv-4", module_id="mod-4",
        title="Talking about last vacation",
        description="Share past travel experiences using past tenses",
        scenario="You are talking with a friend about your last vacation.",
        key_phrases=["I went to...", "It was amazing because...",
                      "I have never been to...", "The best part was...",
                      "Have you ever visited...?"],
        vocabulary=["vacation", "trip", "flight", "hotel", "souvenir"]
    ),
    ConversationTopic(
        id="conv-5", module_id="mod-5",
        title="Making weekend plans",
        description="Discuss future plans and invitations",
        scenario="You and your friend are planning what to do this weekend.",
        key_phrases=["What are you going to do?", "I am planning to...",
                      "Would you like to...?", "Let's meet at...",
                      "That sounds great!"],
        vocabulary=["plans", "weekend", "invitation", "suggest", "agree"]
    ),
]

SYSTEM_RESPONSES = {
    "greeting": ["Hello! How are you today?", "Hi there! Nice to see you.",
                  "Good day! How can I help you practice?"],
    "question": ["That is a great question!", "Interesting! Let me think about that.",
                  "Good one! Here is my response:"],
    "farewell": ["Goodbye! Keep practicing!", "See you next time!",
                  "Have a great day! Practice makes perfect."],
    "default": ["Tell me more about that.", "I see. Can you elaborate?",
                 "That is interesting! What else can you say?",
                 "Great job! Keep going.",
                 "Excellent! You are improving."]
}

@router.get("/topics", response_model=list[ConversationTopic])
async def get_conversation_topics(module_id: str = None):
    if module_id:
        return [c for c in CONVERSATIONS if c.module_id == module_id]
    return CONVERSATIONS

@router.get("/topics/{topic_id}", response_model=ConversationTopic)
async def get_conversation_topic(topic_id: str):
    for topic in CONVERSATIONS:
        if topic.id == topic_id:
            return topic
    raise HTTPException(status_code=404, detail="Conversation topic not found")

@router.post("/evaluate")
async def evaluate_speech(body: EvaluateRequest):
    transcript = body.transcript
    expected_phrases = body.expected_phrases
    if not transcript.strip():
        return SpeechEvaluation(
            transcript="",
            accuracy_score=0.0,
            pronunciation_score=0.0,
            fluency_score=0.0,
            feedback="No speech detected. Please try again.",
            suggested_improvements=["Speak clearly into the microphone",
                                    "Try to say complete sentences"]
        )

    transcript_lower = transcript.lower().strip()

    expected_lower = [p.lower() for p in expected_phrases]
    best_match_score = 0.0
    best_match = ""

    for expected in expected_lower:
        score = _calculate_similarity(transcript_lower, expected)
        if score > best_match_score:
            best_match_score = score
            best_match = expected

    word_count = len(transcript_lower.split())
    avg_word_length = sum(len(w) for w in transcript_lower.split()) / max(word_count, 1)

    fluency_score = min(1.0, word_count / 15.0)
    if word_count < 3:
        fluency_score *= 0.5

    pronunciation_score = _estimate_pronunciation(transcript_lower, avg_word_length)

    accuracy_score = best_match_score

    feedback = _generate_feedback(accuracy_score, fluency_score, word_count, transcript)
    improvements = _generate_improvements(accuracy_score, transcript_lower, best_match)

    grammar = correct_sentence(transcript)

    return SpeechEvaluation(
        transcript=transcript,
        accuracy_score=round(accuracy_score, 2),
        pronunciation_score=round(pronunciation_score, 2),
        fluency_score=round(fluency_score, 2),
        feedback=feedback,
        suggested_improvements=improvements,
        grammar_correction=grammar["corrected"],
        grammar_changes=grammar["changes"],
        has_grammar_errors=grammar["has_errors"],
    )

@router.post("/correct")
async def correct_grammar(body: CorrectRequest):
    return correct_sentence(body.text)

@router.post("/chat/{topic_id}")
async def chat(topic_id: str, message: ConversationMessage):
    topic = None
    for c in CONVERSATIONS:
        if c.id == topic_id:
            topic = c
            break
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    msg_lower = message.content.lower()

    if any(word in msg_lower for word in ["bye", "goodbye", "see you", "later"]):
        response = random.choice(SYSTEM_RESPONSES["farewell"])
    elif "?" in message.content:
        response = random.choice(SYSTEM_RESPONSES["question"])
        response += f" Regarding {topic.title}, "
        response += f"try using phrases like: {random.choice(topic.key_phrases)}"
    elif any(word in msg_lower for word in ["hello", "hi", "hey", "good morning"]):
        response = random.choice(SYSTEM_RESPONSES["greeting"])
        response += f" Let's practice {topic.title}. {topic.scenario}"
    else:
        response = random.choice(SYSTEM_RESPONSES["default"])
        if random.random() > 0.5:
            response += f" Try incorporating: {random.choice(topic.key_phrases)}"

    return {
        "role": "assistant",
        "content": response,
        "topic_id": topic_id
    }

def _calculate_similarity(s1: str, s2: str) -> float:
    words1 = set(s1.split())
    words2 = set(s2.split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    jaccard = len(intersection) / len(union) if union else 0.0

    seq_match = 0
    s1_words = s1.split()
    for i, word in enumerate(s2.split()):
        if i < len(s1_words) and word == s1_words[i]:
            seq_match += 1
    seq_ratio = seq_match / max(len(s2.split()), 1)

    return max(jaccard, seq_ratio)

def _estimate_pronunciation(text: str, avg_word_len: float) -> float:
    score = 0.7
    vowel_pattern = re.findall(r'[aeiou]', text)
    vowel_ratio = len(vowel_pattern) / max(len(text), 1)
    if 0.3 <= vowel_ratio <= 0.6:
        score += 0.1
    if avg_word_len >= 4:
        score += 0.1

    complex_patterns = re.findall(r'(th|sh|ch|ph|wh|ght|tion|sion|ough)', text)
    if complex_patterns:
        score += min(0.1, len(complex_patterns) * 0.02)

    return min(1.0, max(0.0, score))

def _generate_feedback(accuracy: float, fluency: float, word_count: int, transcript: str) -> str:
    if accuracy >= 0.8:
        feedback = "Excellent! Your sentence was clear and accurate."
    elif accuracy >= 0.6:
        feedback = "Good effort! Most of your words matched well."
    elif accuracy >= 0.4:
        feedback = "Keep trying! Try to match the key phrases more closely."
    else:
        feedback = "Try again! Focus on pronouncing each word clearly."

    if fluency >= 0.7:
        feedback += " You spoke with good flow."
    elif fluency >= 0.4:
        feedback += " Try to speak a bit more to improve fluency."
    else:
        feedback += " Try speaking in complete sentences."

    return feedback

def _generate_improvements(accuracy: float, transcript: str, best_match: str) -> List[str]:
    improvements = []
    if accuracy < 0.8:
        improvements.append(f"Try saying: '{best_match}'")
    if len(transcript.split()) < 5:
        improvements.append("Try to form longer, complete sentences")
    if accuracy < 0.5:
        improvements.append("Focus on the key vocabulary words from the module")
    if not improvements:
        improvements.append("Keep practicing to maintain your progress!")
    return improvements
