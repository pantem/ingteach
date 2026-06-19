from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.learning import (
    ConversationTopic, ConversationMessage, SpeechEvaluation,
)
from app.services.grammar import correct_sentence
from typing import List, Optional
import random
import re

class EvaluateRequest(BaseModel):
    transcript: str
    expected_phrases: List[str] = []

class CorrectRequest(BaseModel):
    text: str

class ChatResponse(BaseModel):
    role: str
    content: str
    topic_id: str
    user_message: Optional[str] = ""
    grammar_correction: Optional[str] = ""
    grammar_changes: Optional[List[str]] = []
    has_grammar_errors: Optional[bool] = False

class StructuredChatRequest(BaseModel):
    role: str
    content: str
    current_question: int = 0
    session_id: Optional[str] = None
    responses: List[dict] = []

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

TOPIC_QUESTIONS = {
    "conv-1": [
        "Hello! Nice to meet you. Can you introduce yourself? Tell me your name and where you are from.",
        "What do you do? Are you a student or do you work?",
        "Why did you decide to learn English? What is your main motivation?",
        "What are your hobbies? What do you like to do in your free time?",
        "How do you feel about your new job? What do you do there?"
    ],
    "conv-2": [
        "What time do you usually wake up on weekdays?",
        "What do you usually have for breakfast?",
        "What do you do after breakfast? Describe your morning routine.",
        "How do you usually go to work or school?",
        "What do you do in the evening after work or school?"
    ],
    "conv-3": [
        "What is your favorite type of food? Why do you like it?",
        "How often do you eat out at restaurants?",
        "What would you order if you went to a restaurant right now?",
        "Do you prefer to cook at home or eat out? Explain why.",
        "What is the best restaurant you have ever been to? Describe it."
    ],
    "conv-4": [
        "Where did you go on your last vacation?",
        "Who did you go with and how long did you stay?",
        "What was the best part of your trip? Describe it.",
        "Have you ever been to another country? Which one?",
        "What kind of vacations do you prefer: beach, mountain, or city? Why?"
    ],
    "conv-5": [
        "What are you planning to do this weekend?",
        "Would you rather stay at home or go out? Why?",
        "If the weather is nice, what outdoor activity would you like to do?",
        "Is there a movie you want to see or a restaurant you want to try?",
        "What did you do last weekend? Was it fun?"
    ],
}

QUESTIONS_RESPONSES = {
    "greeting": ["Hello! How are you today?", "Hi there! Nice to see you.",
                  "Good day! How can I help you practice?"],
    "farewell": ["Goodbye! Keep practicing!", "See you next time!",
                  "Have a great day! Practice makes perfect."],
    "praise": ["Great answer!", "Excellent!", "Good job!", "Well said!",
               "Very good! Keep it up."],
    "encourage": ["Try to use more details in your answer.",
                  "Can you tell me more about that?",
                  "That is a good start. Try to expand your answer.",
                  "Nice! Try to use some of the key vocabulary words."],
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

@router.post("/start/{topic_id}")
async def start_conversation(topic_id: str):
    if topic_id not in TOPIC_QUESTIONS:
        raise HTTPException(status_code=404, detail="Topic questions not found")
    questions = TOPIC_QUESTIONS[topic_id]
    return {
        "topic_id": topic_id,
        "current_question": 0,
        "total_questions": len(questions),
        "question": questions[0],
        "role": "assistant",
        "responses": [],
    }

@router.post("/structured/{topic_id}")
async def structured_chat(topic_id: str, body: StructuredChatRequest):
    if topic_id not in TOPIC_QUESTIONS:
        raise HTTPException(status_code=404, detail="Topic not found")

    questions = TOPIC_QUESTIONS[topic_id]
    q_idx = body.current_question
    responses = list(body.responses)

    grammar = await correct_sentence(body.content)
    score = _evaluate_response(body.content, q_idx, topic_id)

    responses.append({
        "question": questions[q_idx] if 0 <= q_idx < len(questions) else "",
        "answer": body.content,
        "grammar_correction": grammar["corrected"] if grammar["has_errors"] else None,
        "grammar_changes": grammar["changes"],
        "has_grammar_errors": grammar["has_errors"],
        "word_count": len(body.content.split()),
    })

    q_idx += 1

    if q_idx >= len(questions):
        summary = _generate_summary(responses)
        return {
            "role": "assistant",
            "content": summary["message"],
            "topic_id": topic_id,
            "current_question": -1,
            "total_questions": len(questions),
            "is_completed": True,
            "responses": responses,
            "summary": summary,
            "user_message": body.content,
            "grammar_correction": grammar["corrected"] if grammar["has_errors"] else None,
            "grammar_changes": grammar["changes"],
            "has_grammar_errors": grammar["has_errors"],
        }

    next_q = questions[q_idx]
    feedback = _generate_response_feedback(score, grammar, body.content)

    return {
        "role": "assistant",
        "content": f"{feedback}\n\n{next_q}",
        "topic_id": topic_id,
        "current_question": q_idx,
        "total_questions": len(questions),
        "is_completed": False,
        "responses": responses,
        "user_message": body.content,
        "grammar_correction": grammar["corrected"] if grammar["has_errors"] else "",
        "grammar_changes": grammar["changes"],
        "has_grammar_errors": grammar["has_errors"],
        "evaluation_score": score,
    }

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

    grammar = await correct_sentence(transcript)

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
    return await correct_sentence(body.text)

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
        response_text = random.choice(QUESTIONS_RESPONSES["farewell"])
    elif any(word in msg_lower for word in ["hello", "hi", "hey", "good morning"]):
        response_text = random.choice(QUESTIONS_RESPONSES["greeting"])
        response_text += f" Let's practice {topic.title}. {topic.scenario}"
    else:
        response_text = random.choice(QUESTIONS_RESPONSES["praise"])
        if random.random() > 0.5:
            response_text += f" Try incorporating: {random.choice(topic.key_phrases)}"

    grammar = await correct_sentence(message.content)

    return ChatResponse(
        role="assistant",
        content=response_text,
        topic_id=topic_id,
        user_message=message.content,
        grammar_correction=grammar["corrected"],
        grammar_changes=grammar["changes"],
        has_grammar_errors=grammar["has_errors"],
    )

def _evaluate_response(text: str, q_idx: int, topic_id: str) -> float:
    score = 0.5
    words = text.lower().split()
    word_count = len(words)

    if word_count >= 8:
        score += 0.2
    elif word_count >= 4:
        score += 0.1

    for conv in CONVERSATIONS:
        if conv.id == topic_id:
            vocab = [v.lower() for v in conv.vocabulary]
            used = sum(1 for v in vocab if v in text.lower())
            score += min(0.2, used * 0.05)
            break

    has_verbs = any(w in text.lower() for w in ["am", "is", "are", "was", "were", "have", "has", "had", "do", "does", "did", "will", "would", "can", "could", "go", "went", "like", "liked", "want", "needed"])
    if has_verbs:
        score += 0.1

    return min(1.0, max(0.0, score))

def _generate_response_feedback(score: float, grammar: dict, text: str) -> str:
    parts = []

    if grammar["has_errors"]:
        parts.append(f"Grammar: {grammar['corrected']}")
    else:
        parts.append(random.choice(["Good grammar!", "Your sentence structure is correct.", "Well constructed!"]))

    if len(text.split()) < 4:
        parts.append("Try to give longer answers with more details.")
    elif len(text.split()) >= 8:
        parts.append("Great length of answer!")

    if score >= 0.8:
        parts.append("Excellent response!")
    elif score >= 0.5:
        parts.append("Good effort!")

    return " ".join(parts)

def _generate_summary(responses: list) -> dict:
    total = len(responses)
    errors = sum(1 for r in responses if r.get("has_grammar_errors"))
    avg_words = sum(r.get("word_count", 0) for r in responses) / max(total, 1)

    if errors == 0:
        msg = f"Excellent work! You answered all {total} questions with correct grammar."
    elif errors <= total * 0.3:
        msg = f"Good job! You answered {total} questions with only {errors} grammar mistakes. Keep practicing!"
    else:
        msg = f"You answered {total} questions. Focus on grammar - you had {errors} sentences with errors. Review the corrections."

    if avg_words < 5:
        msg += " Try to give more detailed answers next time."
    elif avg_words >= 10:
        msg += " Your answers were detailed and well-developed!"

    return {
        "total_questions": total,
        "grammar_errors": errors,
        "average_word_count": round(avg_words, 1),
        "message": msg,
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