from fastapi import APIRouter
from app.models.learning import VerbConjugation, VerbTense
from typing import List

router = APIRouter()

VERB_DATA = {
    "be": {
        "present_simple": {"I": "am", "you": "are", "he/she/it": "is", "we": "are", "they": "are"},
        "past_simple": {"I": "was", "you": "were", "he/she/it": "was", "we": "were", "they": "were"},
        "present_perfect": {"I": "have been", "you": "have been", "he/she/it": "has been", "we": "have been", "they": "have been"},
        "future_simple": {"I": "will be", "you": "will be", "he/she/it": "will be", "we": "will be", "they": "will be"},
        "present_continuous": {"I": "am being", "you": "are being", "he/she/it": "is being", "we": "are being", "they": "are being"}
    },
    "have": {
        "present_simple": {"I": "have", "you": "have", "he/she/it": "has", "we": "have", "they": "have"},
        "past_simple": {"I": "had", "you": "had", "he/she/it": "had", "we": "had", "they": "had"},
        "present_perfect": {"I": "have had", "you": "have had", "he/she/it": "has had", "we": "have had", "they": "have had"},
        "future_simple": {"I": "will have", "you": "will have", "he/she/it": "will have", "we": "will have", "they": "will have"},
        "present_continuous": {"I": "am having", "you": "are having", "he/she/it": "is having", "we": "are having", "they": "are having"}
    },
    "go": {
        "present_simple": {"I": "go", "you": "go", "he/she/it": "goes", "we": "go", "they": "go"},
        "past_simple": {"I": "went", "you": "went", "he/she/it": "went", "we": "went", "they": "went"},
        "present_perfect": {"I": "have gone", "you": "have gone", "he/she/it": "has gone", "we": "have gone", "they": "have gone"},
        "future_simple": {"I": "will go", "you": "will go", "he/she/it": "will go", "we": "will go", "they": "will go"},
        "present_continuous": {"I": "am going", "you": "are going", "he/she/it": "is going", "we": "are going", "they": "are going"}
    },
    "do": {
        "present_simple": {"I": "do", "you": "do", "he/she/it": "does", "we": "do", "they": "do"},
        "past_simple": {"I": "did", "you": "did", "he/she/it": "did", "we": "did", "they": "did"},
        "present_perfect": {"I": "have done", "you": "have done", "he/she/it": "has done", "we": "have done", "they": "have done"},
        "future_simple": {"I": "will do", "you": "will do", "he/she/it": "will do", "we": "will do", "they": "will do"},
        "present_continuous": {"I": "am doing", "you": "are doing", "he/she/it": "is doing", "we": "are doing", "they": "are doing"}
    },
    "say": {
        "present_simple": {"I": "say", "you": "say", "he/she/it": "says", "we": "say", "they": "say"},
        "past_simple": {"I": "said", "you": "said", "he/she/it": "said", "we": "said", "they": "said"},
        "present_perfect": {"I": "have said", "you": "have said", "he/she/it": "has said", "we": "have said", "they": "have said"},
        "future_simple": {"I": "will say", "you": "will say", "he/she/it": "will say", "we": "will say", "they": "will say"}
    },
    "make": {
        "present_simple": {"I": "make", "you": "make", "he/she/it": "makes", "we": "make", "they": "make"},
        "past_simple": {"I": "made", "you": "made", "he/she/it": "made", "we": "made", "they": "made"},
        "present_perfect": {"I": "have made", "you": "have made", "he/she/it": "has made", "we": "have made", "they": "have made"},
        "future_simple": {"I": "will make", "you": "will make", "he/she/it": "will make", "we": "will make", "they": "will make"}
    },
    "take": {
        "present_simple": {"I": "take", "you": "take", "he/she/it": "takes", "we": "take", "they": "take"},
        "past_simple": {"I": "took", "you": "took", "he/she/it": "took", "we": "took", "they": "took"},
        "present_perfect": {"I": "have taken", "you": "have taken", "he/she/it": "has taken", "we": "have taken", "they": "have taken"},
        "future_simple": {"I": "will take", "you": "will take", "he/she/it": "will take", "we": "will take", "they": "will take"}
    },
    "come": {
        "present_simple": {"I": "come", "you": "come", "he/she/it": "comes", "we": "come", "they": "come"},
        "past_simple": {"I": "came", "you": "came", "he/she/it": "came", "we": "came", "they": "came"},
        "present_perfect": {"I": "have come", "you": "have come", "he/she/it": "has come", "we": "have come", "they": "have come"},
        "future_simple": {"I": "will come", "you": "will come", "he/she/it": "will come", "we": "will come", "they": "will come"}
    },
    "see": {
        "present_simple": {"I": "see", "you": "see", "he/she/it": "sees", "we": "see", "they": "see"},
        "past_simple": {"I": "saw", "you": "saw", "he/she/it": "saw", "we": "saw", "they": "saw"},
        "present_perfect": {"I": "have seen", "you": "have seen", "he/she/it": "has seen", "we": "have seen", "they": "have seen"},
        "future_simple": {"I": "will see", "you": "will see", "he/she/it": "will see", "we": "will see", "they": "will see"}
    },
    "eat": {
        "present_simple": {"I": "eat", "you": "eat", "he/she/it": "eats", "we": "eat", "they": "eat"},
        "past_simple": {"I": "ate", "you": "ate", "he/she/it": "ate", "we": "ate", "they": "ate"},
        "present_perfect": {"I": "have eaten", "you": "have eaten", "he/she/it": "has eaten", "we": "have eaten", "they": "have eaten"},
        "future_simple": {"I": "will eat", "you": "will eat", "he/she/it": "will eat", "we": "will eat", "they": "will eat"},
        "present_continuous": {"I": "am eating", "you": "are eating", "he/she/it": "is eating", "we": "are eating", "they": "are eating"}
    },
    "drink": {
        "present_simple": {"I": "drink", "you": "drink", "he/she/it": "drinks", "we": "drink", "they": "drink"},
        "past_simple": {"I": "drank", "you": "drank", "he/she/it": "drank", "we": "drank", "they": "drank"},
        "present_perfect": {"I": "have drunk", "you": "have drunk", "he/she/it": "has drunk", "we": "have drunk", "they": "have drunk"},
        "future_simple": {"I": "will drink", "you": "will drink", "he/she/it": "will drink", "we": "will drink", "they": "will drink"}
    },
    "write": {
        "present_simple": {"I": "write", "you": "write", "he/she/it": "writes", "we": "write", "they": "write"},
        "past_simple": {"I": "wrote", "you": "wrote", "he/she/it": "wrote", "we": "wrote", "they": "wrote"},
        "present_perfect": {"I": "have written", "you": "have written", "he/she/it": "has written", "we": "have written", "they": "have written"},
        "future_simple": {"I": "will write", "you": "will write", "he/she/it": "will write", "we": "will write", "they": "will write"}
    },
    "read": {
        "present_simple": {"I": "read", "you": "read", "he/she/it": "reads", "we": "read", "they": "read"},
        "past_simple": {"I": "read", "you": "read", "he/she/it": "read", "we": "read", "they": "read"},
        "present_perfect": {"I": "have read", "you": "have read", "he/she/it": "has read", "we": "have read", "they": "have read"},
        "future_simple": {"I": "will read", "you": "will read", "he/she/it": "will read", "we": "will read", "they": "will read"}
    },
    "speak": {
        "present_simple": {"I": "speak", "you": "speak", "he/she/it": "speaks", "we": "speak", "they": "speak"},
        "past_simple": {"I": "spoke", "you": "spoke", "he/she/it": "spoke", "we": "spoke", "they": "spoke"},
        "present_perfect": {"I": "have spoken", "you": "have spoken", "he/she/it": "has spoken", "we": "have spoken", "they": "have spoken"},
        "future_simple": {"I": "will speak", "you": "will speak", "he/she/it": "will speak", "we": "will speak", "they": "will speak"}
    },
}

TENSE_EXAMPLES = {
    "present_simple": {
        "description": "Used for habits, facts, and routines",
        "formula": "Subject + base verb (add -s/-es for he/she/it)",
        "examples": ["I eat breakfast every day.", "She works at a bank.", "The sun rises in the east."]
    },
    "present_continuous": {
        "description": "Used for actions happening now or temporary situations",
        "formula": "Subject + am/is/are + verb(-ing)",
        "examples": ["I am reading a book right now.", "They are studying for the exam.", "She is working from home this week."]
    },
    "present_perfect": {
        "description": "Used for past actions with present relevance or experience",
        "formula": "Subject + have/has + past participle",
        "examples": ["I have visited London twice.", "She has never tried sushi.", "They have finished their homework."]
    },
    "past_simple": {
        "description": "Used for completed actions in the past",
        "formula": "Subject + past tense verb (-ed for regular verbs)",
        "examples": ["I walked to school yesterday.", "She bought a new car.", "They watched a movie last night."]
    },
    "past_continuous": {
        "description": "Used for actions in progress at a specific past time",
        "formula": "Subject + was/were + verb(-ing)",
        "examples": ["I was sleeping when you called.", "They were having dinner at 8 PM.", "She was studying all night."]
    },
    "future_simple": {
        "description": "Used for predictions, promises, and spontaneous decisions",
        "formula": "Subject + will + base verb",
        "examples": ["I will call you tomorrow.", "It will rain later.", "She will help you with that."]
    },
    "conditional": {
        "description": "Used for hypothetical situations (if-clauses)",
        "formula": "If + subject + past tense, subject + would + base verb",
        "examples": ["If I had money, I would travel the world.", "If she studied more, she would pass the exam.", "They would come if you invited them."]
    }
}

@router.get("/verbs", response_model=List[VerbConjugation])
async def get_verbs(tense: VerbTense = None):
    results = []
    for verb, tenses in VERB_DATA.items():
        for tense_key, conjugations in tenses.items():
            if tense and tense_key != tense.value:
                continue
            examples = TENSE_EXAMPLES.get(tense_key, {}).get("examples", [])
            results.append(VerbConjugation(
                verb=verb,
                tense=VerbTense(tense_key),
                conjugations=conjugations,
                examples=examples[:2]
            ))
    return results

@router.get("/verbs/{verb}", response_model=VerbConjugation)
async def get_verb_conjugation(verb: str, tense: VerbTense = None):
    if verb not in VERB_DATA:
        return VerbConjugation(
            verb=verb,
            tense=tense or VerbTense.PRESENT_SIMPLE,
            conjugations={"I": f"[regular] {verb}", "you": f"[regular] {verb}",
                          "he/she/it": f"[regular] {verb}s", "we": f"[regular] {verb}",
                          "they": f"[regular] {verb}"},
            examples=[f"I {verb} every day.", f"She {verb}s every day."]
        )
    verb_tenses = VERB_DATA[verb]
    if tense:
        tense_key = tense.value
        if tense_key in verb_tenses:
            examples = TENSE_EXAMPLES.get(tense_key, {}).get("examples", [])
            return VerbConjugation(
                verb=verb, tense=tense,
                conjugations=verb_tenses[tense_key],
                examples=examples[:2]
            )
        return VerbConjugation(
            verb=verb, tense=tense,
            conjugations={"I": f"[form not available]", "you": f"[form not available]",
                          "he/she/it": f"[form not available]", "we": f"[form not available]",
                          "they": f"[form not available]"},
            examples=[]
        )
    first_tense = list(verb_tenses.keys())[0]
    examples = TENSE_EXAMPLES.get(first_tense, {}).get("examples", [])
    return VerbConjugation(
        verb=verb, tense=VerbTense(first_tense),
        conjugations=verb_tenses[first_tense],
        examples=examples[:2]
    )

@router.get("/tenses")
async def get_all_tenses():
    return TENSE_EXAMPLES

@router.get("/tenses/{tense}")
async def get_tense_info(tense: VerbTense):
    tense_key = tense.value
    if tense_key not in TENSE_EXAMPLES:
        return {"error": "Tense not found"}
    return TENSE_EXAMPLES[tense_key]
