from fastapi import APIRouter, HTTPException
from app.models.learning import TestQuestion, ModuleTest, TestSubmission
from app.database import get_db
from typing import List, Dict

router = APIRouter()

MODULE_TESTS: Dict[str, ModuleTest] = {
    "mod-1": ModuleTest(
        module_id="mod-1", passing_score=0.7,
        questions=[
            TestQuestion(id="m1q1", type="multiple_choice",
                question="How do you greet someone in the morning?",
                options=["Good night", "Good morning", "Goodbye", "See you"],
                correct_answer="Good morning",
                explanation="'Good morning' is the standard greeting in the morning."),
            TestQuestion(id="m1q2", type="multiple_choice",
                question="What is the correct response to 'How are you?'",
                options=["I'm fine, thank you", "I'm a student", "I'm 25 years old", "I'm from Spain"],
                correct_answer="I'm fine, thank you",
                explanation="'I'm fine, thank you' is the most common polite response."),
            TestQuestion(id="m1q3", type="fill_blank",
                question="Complete: 'Nice ___ meet you.'",
                options=["to", "too", "two", "for"],
                correct_answer="to",
                explanation="The correct expression is 'Nice to meet you.'"),
            TestQuestion(id="m1q4", type="multiple_choice",
                question="Which verb is used in 'I ___ a teacher'?",
                options=["am", "is", "are", "be"],
                correct_answer="am",
                explanation="'I am' is the correct form of 'to be' for the first person singular."),
            TestQuestion(id="m1q5", type="fill_blank",
                question="Complete: 'She ___ a doctor.' (to be)",
                options=["am", "is", "are", "be"],
                correct_answer="is",
                explanation="'She is' is the correct form of 'to be' for third person singular."),
        ]
    ),
    "mod-2": ModuleTest(
        module_id="mod-2", passing_score=0.7,
        questions=[
            TestQuestion(id="m2q1", type="multiple_choice",
                question="Which sentence is correct for a daily routine?",
                options=["I wake up at 7 AM every day.", "I waking up at 7 AM every day.",
                         "I am wake up at 7 AM every day.", "I waked up at 7 AM every day."],
                correct_answer="I wake up at 7 AM every day.",
                explanation="Present simple is used for routines: I wake up..."),
            TestQuestion(id="m2q2", type="multiple_choice",
                question="What does 'usually' mean?",
                options=["Always", "Most of the time", "Never", "Rarely"],
                correct_answer="Most of the time",
                explanation="'Usually' means something happens most of the time, but not always."),
            TestQuestion(id="m2q3", type="fill_blank",
                question="She always ___ (have) breakfast at 8.",
                options=["have", "has", "having", "had"],
                correct_answer="has",
                explanation="Third person singular uses 'has' in present simple."),
            TestQuestion(id="m2q4", type="multiple_choice",
                question="Which adverb of frequency means 0%?",
                options=["always", "usually", "sometimes", "never"],
                correct_answer="never",
                explanation="'Never' means it does not happen at all (0% of the time)."),
            TestQuestion(id="m2q5", type="fill_blank",
                question="They ___ (go) to work by bus.",
                options=["go", "goes", "going", "went"],
                correct_answer="go",
                explanation="'They' uses the base form 'go' in present simple."),
        ]
    ),
    "mod-3": ModuleTest(
        module_id="mod-3", passing_score=0.7,
        questions=[
            TestQuestion(id="m3q1", type="multiple_choice",
                question="How do you politely order food?",
                options=["Give me food!", "I would like the pasta, please.",
                         "I want pasta now!", "Food, please."],
                correct_answer="I would like the pasta, please.",
                explanation="'I would like...' is the polite way to order."),
            TestQuestion(id="m3q2", type="multiple_choice",
                question="What do you ask for at the end of a meal?",
                options=["The menu, please", "The bill, please",
                         "The kitchen, please", "The table, please"],
                correct_answer="The bill, please",
                explanation="You ask for 'the bill' when you want to pay."),
            TestQuestion(id="m3q3", type="fill_blank",
                question="Complete: 'Could I ___ the menu, please?'",
                options=["have", "has", "having", "had"],
                correct_answer="have",
                explanation="'Could I have...' is a polite request form."),
            TestQuestion(id="m3q4", type="multiple_choice",
                question="What is a 'main course'?",
                options=["A starter", "The primary dish of a meal",
                         "A dessert", "A drink"],
                correct_answer="The primary dish of a meal",
                explanation="The 'main course' is the primary or main dish of a meal."),
            TestQuestion(id="m3q5", type="fill_blank",
                question="The food ___ (be) delicious.",
                options=["am", "is", "are", "be"],
                correct_answer="is",
                explanation="'The food' is singular, so we use 'is'."),
        ]
    ),
    "mod-4": ModuleTest(
        module_id="mod-4", passing_score=0.7,
        questions=[
            TestQuestion(id="m4q1", type="multiple_choice",
                question="Which sentence is in past simple?",
                options=["I go to the beach.", "I went to the beach yesterday.",
                         "I am going to the beach.", "I will go to the beach."],
                correct_answer="I went to the beach yesterday.",
                explanation="'Went' is the past simple form of 'go'."),
            TestQuestion(id="m4q2", type="multiple_choice",
                question="What is the past participle of 'eat'?",
                options=["eat", "ate", "eaten", "eating"],
                correct_answer="eaten",
                explanation="'Eaten' is the past participle form of 'eat'."),
            TestQuestion(id="m4q3", type="fill_blank",
                question="She ___ (visit) Paris last summer.",
                options=["visit", "visited", "visits", "visiting"],
                correct_answer="visited",
                explanation="'Last summer' is a past time expression, so use past simple 'visited'."),
            TestQuestion(id="m4q4", type="multiple_choice",
                question="When do we use present perfect?",
                options=["For completed actions with no time specified",
                         "For actions happening right now",
                         "For future plans",
                         "For routines"],
                correct_answer="For completed actions with no time specified",
                explanation="Present perfect connects past actions to the present."),
            TestQuestion(id="m4q5", type="fill_blank",
                question="Have you ever ___ (be) to London?",
                options=["be", "being", "been", "was"],
                correct_answer="been",
                explanation="After 'have', we use the past participle 'been'."),
        ]
    ),
    "mod-5": ModuleTest(
        module_id="mod-5", passing_score=0.7,
        questions=[
            TestQuestion(id="m5q1", type="multiple_choice",
                question="Which is correct for a planned future action?",
                options=["I will go to the cinema.", "I am going to go to the cinema.",
                         "I go to the cinema.", "I went to the cinema."],
                correct_answer="I am going to go to the cinema.",
                explanation="'Going to' is used for planned future actions."),
            TestQuestion(id="m5q2", type="multiple_choice",
                question="When do we use 'will'?",
                options=["For planned actions", "For spontaneous decisions and predictions",
                         "For past actions", "For routines"],
                correct_answer="For spontaneous decisions and predictions",
                explanation="'Will' is used for spontaneous decisions, promises, and predictions."),
            TestQuestion(id="m5q3", type="fill_blank",
                question="I ___ (call) you tomorrow.",
                options=["call", "will call", "calling", "called"],
                correct_answer="will call",
                explanation="'Will call' expresses a promise about the future."),
            TestQuestion(id="m5q4", type="multiple_choice",
                question="What does 'probably' mean?",
                options=["Certainly", "Maybe, likely", "Never", "Always"],
                correct_answer="Maybe, likely",
                explanation="'Probably' means something is likely but not certain."),
            TestQuestion(id="m5q5", type="fill_blank",
                question="They ___ (plan) to start a business next year.",
                options=["plan", "plans", "planning", "planned"],
                correct_answer="plan",
                explanation="Present simple 'plan' is used with 'to' to express future intentions."),
        ]
    ),
    "mod-6": ModuleTest(
        module_id="mod-6", passing_score=0.7,
        questions=[
            TestQuestion(id="m6q1", type="multiple_choice",
                question="How do you ask for directions politely?",
                options=["Where is the station?", "Excuse me, how do I get to the station?",
                         "Tell me where the station is!", "Station location now!"],
                correct_answer="Excuse me, how do I get to the station?",
                explanation="Starting with 'Excuse me' makes the question polite."),
            TestQuestion(id="m6q2", type="multiple_choice",
                question="What does 'go straight' mean?",
                options=["Turn left", "Continue in the same direction",
                         "Go back", "Turn around"],
                correct_answer="Continue in the same direction",
                explanation="'Go straight' means continue forward without turning."),
            TestQuestion(id="m6q3", type="fill_blank",
                question="Turn left ___ the traffic light.",
                options=["in", "on", "at", "by"],
                correct_answer="at",
                explanation="We use 'at' with specific points or landmarks."),
            TestQuestion(id="m6q4", type="multiple_choice",
                question="What is a 'roundabout'?",
                options=["A circular junction", "A straight road",
                         "A pedestrian crossing", "A traffic light"],
                correct_answer="A circular junction",
                explanation="A roundabout is a circular intersection where traffic flows around a central island."),
            TestQuestion(id="m6q5", type="fill_blank",
                question="The bank is next ___ the supermarket.",
                options=["to", "of", "at", "in"],
                correct_answer="to",
                explanation="'Next to' means adjacent or beside."),
        ]
    ),
    "mod-7": ModuleTest(
        module_id="mod-7", passing_score=0.7,
        questions=[
            TestQuestion(id="m7q1", type="multiple_choice",
                question="Which phrase introduces an opinion?",
                options=["In my opinion", "For example", "On the other hand", "Therefore"],
                correct_answer="In my opinion",
                explanation="'In my opinion' is a common way to introduce a personal viewpoint."),
            TestQuestion(id="m7q2", type="multiple_choice",
                question="What does 'however' express?",
                options=["Addition", "Contrast", "Conclusion", "Example"],
                correct_answer="Contrast",
                explanation="'However' introduces a contrasting or different idea."),
            TestQuestion(id="m7q3", type="fill_blank",
                question="I disagree ___ that point.",
                options=["with", "to", "on", "at"],
                correct_answer="with",
                explanation="We say 'disagree with' someone or a point."),
            TestQuestion(id="m7q4", type="multiple_choice",
                question="Which connector means 'as a result'?",
                options=["Furthermore", "Nevertheless", "Therefore", "Moreover"],
                correct_answer="Therefore",
                explanation="'Therefore' introduces a logical conclusion or result."),
            TestQuestion(id="m7q5", type="fill_blank",
                question="___ the one hand, technology helps us.",
                options=["In", "On", "At", "By"],
                correct_answer="On",
                explanation="'On the one hand' is the correct expression."),
        ]
    ),
    "mod-8": ModuleTest(
        module_id="mod-8", passing_score=0.7,
        questions=[
            TestQuestion(id="m8q1", type="multiple_choice",
                question="What does 'deadline' mean?",
                options=["A meeting time", "A due date for completion",
                         "A line that is dead", "A type of document"],
                correct_answer="A due date for completion",
                explanation="A 'deadline' is the date or time by which something must be completed."),
            TestQuestion(id="m8q2", type="multiple_choice",
                question="How do you propose an idea in a meeting?",
                options=["Do this now!", "I propose we move forward with this plan.",
                         "Maybe this.","What?"],
                correct_answer="I propose we move forward with this plan.",
                explanation="'I propose' is a professional way to suggest an idea."),
            TestQuestion(id="m8q3", type="fill_blank",
                question="We need to ___ (meet) the deadline.",
                options=["meet", "met", "meeting", "meets"],
                correct_answer="meet",
                explanation="After 'need to', we use the base form of the verb."),
            TestQuestion(id="m8q4", type="multiple_choice",
                question="What is a 'stakeholder'?",
                options=["A person with a stake or interest in a project",
                         "A type of meeting", "A company document", "A job title"],
                correct_answer="A person with a stake or interest in a project",
                explanation="A stakeholder is anyone who has an interest or concern in a project."),
            TestQuestion(id="m8q5", type="fill_blank",
                question="Let's ___ (discuss) the proposal.",
                options=["discuss", "discusses", "discussed", "discussing"],
                correct_answer="discuss",
                explanation="After 'let's', we use the base form of the verb."),
        ]
    ),
}

@router.get("/", response_model=List[ModuleTest])
async def get_all_tests():
    return list(MODULE_TESTS.values())

@router.get("/{module_id}", response_model=ModuleTest)
async def get_module_test(module_id: str):
    if module_id not in MODULE_TESTS:
        raise HTTPException(status_code=404, detail="Test not found for this module")
    return MODULE_TESTS[module_id]

@router.post("/submit/{module_id}")
async def submit_test(module_id: str, submission: TestSubmission):
    if module_id not in MODULE_TESTS:
        raise HTTPException(status_code=404, detail="Test not found for this module")

    test = MODULE_TESTS[module_id]
    correct = 0
    total = len(test.questions)
    results = []

    for question in test.questions:
        user_answer = submission.answers.get(question.id, "")
        is_correct = user_answer == question.correct_answer
        if is_correct:
            correct += 1
        results.append({
            "question_id": question.id,
            "question": question.question,
            "user_answer": user_answer,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct,
            "explanation": question.explanation
        })

    score = correct / total if total > 0 else 0
    passed = score >= test.passing_score

    try:
        db = await get_db()
        await db["test_results"].insert_one({
            "module_id": module_id,
            "score": round(score, 2),
            "correct": correct,
            "total": total,
            "passed": passed,
            "results": results,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
        })
    except Exception:
        pass

    return {
        "module_id": module_id,
        "score": round(score, 2),
        "correct": correct,
        "total": total,
        "passed": passed,
        "passing_score": test.passing_score,
        "results": results,
        "message": "Congratulations! You passed!" if passed else "Keep studying and try again!"
    }
