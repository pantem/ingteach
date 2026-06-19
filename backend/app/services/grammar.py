import re
import httpx
from typing import List

LT_API_URL = "https://api.languagetool.org/v2/check"

async def correct_sentence(text: str) -> dict:
    if not text or not text.strip():
        return {"original": text, "corrected": text, "changes": [], "has_errors": False}

    original = text.strip()

    lt_result = None
    try:
        lt_result = await _correct_with_languagetool(original)
    except Exception:
        pass

    local_result = _correct_local(lt_result["corrected"] if lt_result else original)

    if lt_result and lt_result["has_errors"]:
        merged_changes = list(dict.fromkeys(lt_result["changes"] + local_result["changes"]))
        return {
            "original": original,
            "corrected": local_result["corrected"],
            "changes": merged_changes,
            "has_errors": len(merged_changes) > 0,
        }

    return local_result


async def _correct_with_languagetool(text: str) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(LT_API_URL, data={
            "text": text,
            "language": "en-US",
            "enabledOnly": "false",
        })
        resp.raise_for_status()
        data = resp.json()

    matches = data.get("matches", [])
    if not matches:
        return {"original": text, "corrected": text, "changes": [], "has_errors": False}

    changes = []
    corrected = text

    for match in reversed(matches):
        offset = match["offset"]
        length = match["length"]
        replacements = match.get("replacements", [])
        if not replacements:
            continue
        replacement = replacements[0]["value"]
        wrong = corrected[offset:offset + length]
        if wrong.lower() == replacement.lower():
            continue
        before = corrected[:offset]
        after = corrected[offset + length:]
        corrected = before + replacement + after
        msg = match.get("shortMessage") or match.get("message", "")
        changes.append(f'{msg}: "{wrong}" -> "{replacement}"')

    return {
        "original": text,
        "corrected": corrected,
        "changes": changes,
        "has_errors": len(changes) > 0,
    }


def _correct_local(text: str) -> dict:
    original = text.strip()
    corrected = original
    changes = []

    corrected = _fix_capitalization(corrected, changes)
    corrected = _fix_punctuation(corrected, changes)
    corrected = _fix_article_a_an(corrected, changes)
    corrected = _fix_subject_verb_agreement(corrected, changes)
    corrected = _fix_common_mistakes(corrected, changes)
    corrected = _fix_verb_tense(corrected, changes)
    corrected = _fix_missing_articles(corrected, changes)
    corrected = _fix_word_order(corrected, changes)
    corrected = _fix_preposition_errors(corrected, changes)
    corrected = _fix_pluralization(corrected, changes)
    corrected = _fix_contractions(corrected, changes)
    corrected = _fix_comparatives(corrected, changes)
    corrected = _fix_double_negatives(corrected, changes)
    corrected = _fix_question_formation(corrected, changes)
    corrected = _fix_gerund_infinitive(corrected, changes)
    corrected = _fix_possessives(corrected, changes)
    corrected = _fix_redundancy(corrected, changes)
    corrected = _fix_pronoun_case(corrected, changes)

    return {
        "original": original,
        "corrected": corrected,
        "changes": changes,
        "has_errors": len(changes) > 0,
    }


def _fix_capitalization(text: str, changes: list) -> str:
    result = text
    new = re.sub(r'\bi\b', 'I', result)
    if new != result:
        changes.append('"i" -> "I"')
    result = new
    if result and result[0].islower():
        result = result[0].upper() + result[1:]
        changes.append("Capitalized first letter")
    return result


def _fix_punctuation(text: str, changes: list) -> str:
    result = text.rstrip()
    if result and result[-1] not in ('.', '!', '?', ';', ':'):
        result += '.'
        changes.append("Added period")
    return result


def _fix_article_a_an(text: str, changes: list) -> str:
    result = text
    new = re.sub(r'\ba (a|e|i|o|u)[a-z]*\b', lambda m: _replace_article(m, "an"), result, flags=re.IGNORECASE)
    if new != result:
        changes.append("a -> an before vowel sound")
    result = new
    new = re.sub(r'\ban ([^aeiou])[a-z]*\b', lambda m: _replace_article(m, "a"), result, flags=re.IGNORECASE)
    if new != result:
        changes.append("an -> a before consonant sound")
    result = new
    return result


def _replace_article(m: re.Match, correct: str) -> str:
    word = m.group(0)
    return (correct.capitalize() if word[0].isupper() else correct) + word[1:]


SUBJECT_SINGULAR = {"he", "she", "it", "this", "that", "everyone", "someone", "anyone", "no one", "everybody", "somebody", "anybody", "nobody", "each", "either", "neither", "the student", "the teacher", "the man", "the woman", "the child", "the person", "my friend", "his friend", "her friend", "john", "mary", "peter", "anna"}
SUBJECT_PLURAL = {"they", "we", "you", "these", "those", "people", "things", "students", "teachers", "children", "men", "women", "friends", "the students", "the teachers", "the children", "the men", "the women", "my friends", "his friends", "her friends", "some people", "many people", "all people"}

SV_PATTERNS = [
    (r'\b(I)\s+(is|are|were|has)\b', lambda m: f"I {'am' if m.group(2) == 'is' else 'are' if m.group(2) == 'are' else 'was' if m.group(2) == 'was' else 'were' if m.group(2) == 'were' else 'have'}", "I + verb agreement"),
    (r'\b(He|She|It)\s+(are|were|have)\b', lambda m: f"{m.group(1)} {'is' if m.group(2) == 'are' else 'was' if m.group(2) == 'were' else 'has'}", "he/she/it + verb agreement"),
    (r'\b(They|We|You)\s+(is|was|has)\b', lambda m: f"{m.group(1)} {'are' if m.group(2) == 'is' else 'were' if m.group(2) == 'was' else 'have'}", "they/we/you + verb agreement"),
    (r'\b(He|She|It)\s+(don\'t)\b', lambda m: f"{m.group(1)} doesn't", "he/she/it + don't -> doesn't"),
    (r'\b(He|She|It)\s+(do not)\b', lambda m: f"{m.group(1)} does not", "he/she/it + do not -> does not"),
]

def _fix_subject_verb_agreement(text: str, changes: list) -> str:
    result = text
    for pattern, replacement, desc in SV_PATTERNS:
        new = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        if new != result:
            changes.append(desc)
        result = new
    return result


COMMON_MISTAKES = {
    "peoples": "people", "childs": "children", "childs": "children",
    "moneys": "money", "informations": "information",
    "advices": "advice", "knowledges": "knowledge",
    "furnitures": "furniture", "homeworks": "homework",
    "staffs": "staff", "equipments": "equipment",
    "researches": "research", "progresses": "progress",
    "more better": "better", "more bigger": "bigger",
    "more larger": "larger", "most best": "best",
    "most worst": "worst", "more bigger": "bigger",
    "can could": "could", "will would": "would",
    "shall should": "should", "may might": "might",
    "must have to": "must", "need to to": "need to",
    "want to to": "want to", "try to to": "try to",
    "going to to": "going to", "have to to": "have to",
    "do does": "does", "does do": "does",
    "more easy": "easier", "more hard": "harder",
    "more good": "better", "more bad": "worse",
    "most good": "best", "most bad": "worst",
    "very good": "very good",
    "i can to": "i can", "i must to": "i must",
    "i should to": "i should", "i will to": "i will",
    "he can to": "he can", "she must to": "she must",
    "they can to": "they can",
    "look at to": "look at", "listen to to": "listen to",
    "is depends": "depends", "it depends of": "it depends on",
    "play computer": "play on the computer",
    "i have 20 years": "i am 20 years old",
    "make a party": "have a party",
    "make a question": "ask a question",
    "make a photo": "take a photo",
    "do a mistake": "make a mistake",
    "do a decision": "make a decision",
    "have a shower": "take a shower",
    "have a look": "take a look",
    "i am agree": "i agree",
    "i am not agree": "i do not agree",
    "i am 10 years": "i am 10 years old",
}

def _fix_common_mistakes(text: str, changes: list) -> str:
    result = text
    for wrong, correct in COMMON_MISTAKES.items():
        pat = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
        new = pat.sub(correct, result)
        if new != result:
            if wrong != correct.lower():
                changes.append(f'"{wrong}" -> "{correct}"')
            result = new
    return result


IRREGULAR_PAST = {
    "go": "went", "do": "did", "have": "had", "make": "made",
    "say": "said", "get": "got", "take": "took", "come": "came",
    "see": "saw", "know": "knew", "think": "thought", "give": "gave",
    "find": "found", "tell": "told", "become": "became", "leave": "left",
    "feel": "felt", "put": "put", "bring": "brought", "begin": "began",
    "keep": "kept", "hold": "held", "write": "wrote", "sit": "sat",
    "stand": "stood", "lose": "lost", "meet": "met", "lead": "led",
    "understand": "understood", "draw": "drew", "break": "broke",
    "spend": "spent", "cut": "cut", "rise": "rose", "drive": "drove",
    "buy": "bought", "wear": "wore", "choose": "chose", "eat": "ate",
    "drink": "drank", "speak": "spoke", "run": "ran", "read": "read",
    "teach": "taught", "catch": "caught", "fight": "fought",
    "send": "sent", "build": "built", "learn": "learned",
    "dream": "dreamed", "smell": "smelled", "spell": "spelled",
}

TIME_WORDS_PATTERN = r'\b(yesterday|last\s+\w+|ago|in\s+\d{4}|this morning|this afternoon|earlier|previously|already|just now|a moment ago)\b'

def _fix_verb_tense(text: str, changes: list) -> str:
    result = text

    def fix_past_verb(m):
        prefix = m.group(1).strip() if m.group(1) else ""
        verb = m.group(2).lower()
        if verb in IRREGULAR_PAST:
            replacement = prefix + " " + IRREGULAR_PAST[verb] if prefix else IRREGULAR_PAST[verb]
            return re.sub(r'\b' + re.escape(verb) + r'\b', replacement, m.group(0), count=1, flags=re.IGNORECASE)
        elif not verb.endswith('ed') and verb != 'is' and verb != 'are':
            replacement = prefix + " " + verb + "ed" if prefix else verb + "ed"
            if verb.endswith('e'):
                replacement = prefix + " " + verb + "d" if prefix else verb + "d"
            if verb.endswith('y') and not verb.endswith('ay') and not verb.endswith('ey') and not verb.endswith('iy') and not verb.endswith('oy') and not verb.endswith('uy'):
                replacement = prefix + " " + verb[:-1] + "ied" if prefix else verb[:-1] + "ied"
            return re.sub(r'\b' + re.escape(verb) + r'\b', replacement, m.group(0), count=1, flags=re.IGNORECASE)
        return m.group(0)

    new = re.sub(TIME_WORDS_PATTERN + r'.*?\b(go|do|have|make|say|get|take|come|see|know|think|give|find|tell|become|leave|feel|put|bring|begin|keep|hold|write|sit|stand|lose|meet|eat|drink|speak|run|buy|wear|choose|break|spend|cut|rise|drive|teach|catch|fight|send|build|learn|dream|smell|spell)\b',
                 fix_past_verb, result, flags=re.IGNORECASE)
    if new != result:
        changes.append("Verb tense corrected (past time context)")
    result = new

    result = re.sub(r'\b(he|she|it)\s+(go|do|have|make|say|get|take|come|see|know|think|give|find|tell|become|leave|feel|put|bring|begin)\b',
                    lambda m: f"{m.group(1)} {IRREGULAR_PAST.get(m.group(2).lower(), m.group(2) + 's')}" if m.group(2).lower() in IRREGULAR_PAST else f"{m.group(1)} {m.group(2)}s",
                    result, flags=re.IGNORECASE)

    new = re.sub(r'\b(he|she|it)\s+(go|do|have|make|say)\b',
                 lambda m: f"{m.group(1)} {m.group(2)}es" if m.group(2).lower() in {"go", "do"} else f"{m.group(1)} {m.group(2)}s",
                 result, flags=re.IGNORECASE)
    if new != result:
        changes.append("he/she/it + verb -> third person -s/-es")
    result = new

    new = re.sub(r'\b(don\'t|doesn\'t|do not|does not)\s+(goes|does|has|says|makes)\b',
                 lambda m: f"{m.group(1)} {m.group(2).rstrip('s') if m.group(2) != 'goes' else 'go' if m.group(2) != 'does' else 'do'}",
                 result, flags=re.IGNORECASE)
    if new != result:
        changes.append("Auxiliary + verb base form corrected")
    result = new

    return result


ARTICLE_PATTERNS = [
    (r'\b(the\s+)?(student|teacher|doctor|engineer|lawyer|nurse|pilot|police|firefighter|accountant|artist|writer|musician|actor|driver|cook|baker|farmer|manager|director|president|king|queen|prince|princess)\s+(is|was|works)\b',
     lambda m: f"{'the ' if not m.group(1) else m.group(1)}{m.group(2)} {m.group(3)}" if m.group(1) else f"the {m.group(2)} {m.group(3)}",
     "Missing article before profession"),
]

def _fix_missing_articles(text: str, changes: list) -> str:
    result = text
    for pattern, replacement, desc in ARTICLE_PATTERNS:
        new = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        if new != result:
            changes.append(desc)
        result = new
    return result


def _fix_word_order(text: str, changes: list) -> str:
    result = text
    new = re.sub(r'\balways\s+(am|is|are|was|were)\b',
                 lambda m: m.group(1) + " always", result, flags=re.IGNORECASE)
    if new != result:
        changes.append("Adverb position corrected")
    result = new

    new = re.sub(r'\b(never|always|often|sometimes|usually|rarely|seldom|always|hardly)\s+(am|is|are|was|were)\b',
                 lambda m: m.group(2) + " " + m.group(1), result, flags=re.IGNORECASE)
    if new != result:
        changes.append("Adverb after verb 'to be'")
    result = new

    new = re.sub(r'\b(like|love|enjoy|hate)\s+(very\s+)?much\s+(\w+)\b',
                 lambda m: f"{m.group(1)} {m.group(3)} {m.group(2) or ''}a lot" if m.group(2) else f"{m.group(1)} {m.group(3)}", result, flags=re.IGNORECASE)
    result = new

    adj_order = re.compile(r'\ba\s+(\w+)\s+(\w+)\s+(car|house|book|table|chair|dress|shirt|shoes|food|drink|movie|song|place|city|country|dog|cat|tree|flower)\b', re.IGNORECASE)

    return result


ADJECTIVE_ORDER_FIXES = [
    (r'\ba\s+(red|blue|green|yellow|black|white|big|small|old|new|young|tall|short|long|fast|slow|good|bad|nice|cool|great|wonderful|beautiful|ugly|hot|cold)\s+(red|blue|green|yellow|black|white|big|small|old|new|young|tall|short|long|fast|slow|good|bad|nice|cool|great|wonderful|beautiful|ugly|hot|cold)\s+(\w+)\b',
     None, ""),
]

PERSONAL_PRONOUNS = {
    "me": "I", "him": "he", "her": "she", "them": "they", "us": "we"
}

PREPOSITION_ERRORS = {
    "on morning": "in the morning", "on afternoon": "in the afternoon",
    "on evening": "in the evening", "on night": "at night",
    "in the weekend": "on the weekend", "at the weekend": "on the weekend",
    "on the summer": "in the summer", "on the winter": "in the winter",
    "on spring": "in spring", "on autumn": "in autumn",
    "interested on": "interested in", "interested of": "interested in",
    "good on": "good at", "good in": "good at",
    "bad on": "bad at", "bad in": "bad at",
    "excelent on": "excellent at", "brilliant on": "brilliant at",
    "skill on": "skilled at",
    "depend of": "depend on",
    "based of": "based on",
    "comprised of": "composed of",
    "different of": "different from",
    "similar with": "similar to",
    "arrive to": "arrive at",
    "go to home": "go home",
    "come to home": "come home",
    "discuss about": "discuss",
    "emphasize on": "emphasize",
    "request for": "request",
    "ask to": "ask",
    "explain me": "explain to me",
    "tell to him": "tell him",
    "say to him": "tell him",
    "look at to": "look at",
    "listen music": "listen to music",
    "speak english": "speak English",
    "talk with him about": "talk to him about",
    "go to the bed": "go to bed",
    "go to the school": "go to school",
    "go to the work": "go to work",
    "go to the church": "go to church",
    "go to the hospital (as patient)": "go to the hospital",
    "at the end of the day (literal)": "at the end of the day",
    "in the end (finally)": "in the end",
    "in the other hand": "on the other hand",
    "by the other hand": "on the other hand",
    "in my opinion i think": "in my opinion",
    "the reason is because": "the reason is that",
    "due to the fact that": "because",
}

def _fix_preposition_errors(text: str, changes: list) -> str:
    result = text
    for wrong, correct in PREPOSITION_ERRORS.items():
        pat = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
        new = pat.sub(correct, result)
        if new != result:
            changes.append(f'"{wrong}" -> "{correct}"')
            result = new
    return result


PLURAL_MISTAKES = {
    r'\b(this)\s+(\w+es)\b': ("these", "this + plural noun -> these"),
    r'\b(that)\s+(\w+es)\b': ("those", "that + plural noun -> those"),
    r'\b(this)\s+(\w+s)\b': ("these", "this + plural noun -> these"),
    r'\b(that)\s+(\w+s)\b': ("those", "that + plural noun -> those"),
    r'\b(a)\s+(\w+s)\b': ("", "a + plural noun -> remove 'a'"),
    r'\b(an)\s+(\w+s)\b': ("", "an + plural noun -> remove 'an'"),
    r'\b(many)\s+(\w+)\b': (None, ""),
    r'\b(much)\s+(\w+s)\b': ("many", "much + plural -> many"),
}

def _fix_pluralization(text: str, changes: list) -> str:
    result = text
    for pattern, (replacement, desc) in PLURAL_MISTAKES.items():
        new = re.sub(pattern, lambda m, r=replacement, d=desc: (r + " " + m.group(2)) if r else m.group(2), result, flags=re.IGNORECASE)
        if new != result:
            pass
    return result


CONTRACTION_FIXES = {
    "i\'m": "I'm", "i\'ve": "I've", "i\'ll": "I'll", "i\'d": "I'd",
    "i am": "I am", "i have": "I have", "i will": "I will", "i would": "I would",
    "dont": "don't", "doesnt": "doesn't", "didnt": "didn't",
    "cant": "can't", "couldnt": "couldn't", "wouldnt": "wouldn't",
    "shouldnt": "shouldn't", "wont": "won't", "isnt": "isn't",
    "arent": "aren't", "wasnt": "wasn't", "werent": "weren't",
    "havent": "haven't", "hasnt": "hasn't", "hadnt": "hadn't",
    "mustnt": "mustn't", "neednt": "needn't",
    "im": "I'm", "ive": "I've", "ill": "I'll", "id": "I'd",
    "hes": "he's", "she's": "she's", "its": "it's",
    "theres": "there's", "theyll": "they'll",
    "thats": "that's", "whats": "what's", "whos": "who's",
    "heres": "here's", "theres": "there's",
    "dont know": "don't know",
    "don't no": "don't know",
}

def _fix_contractions(text: str, changes: list) -> str:
    result = text
    for wrong, correct in CONTRACTION_FIXES.items():
        pat = re.compile(r'\b' + re.escape(wrong) + r'\b')
        new = pat.sub(correct, result)
        if new != result:
            if wrong != correct.lower():
                changes.append(f'"{wrong}" -> "{correct}"')
            result = new
    return result


COMPARATIVE_FIXES = [
    (r'\b(more)\s+(easy|happy|busy|pretty|angry|funny|heavy|lucky|simple|quiet)\b',
     lambda m: m.group(2)[:-1] + "ier" if m.group(2).endswith('y') else "more " + m.group(2)),
    (r'\b(more)\s+(good|bad|far)\b', lambda m: {"good": "better", "bad": "worse", "far": "further"}.get(m.group(2), m.group(2))),
    (r'\b(most)\s+(good|bad|far)\b', lambda m: {"good": "best", "bad": "worst", "far": "furthest"}.get(m.group(2), m.group(2))),
    (r'\b(more)\s+(big|small|tall|short|long|fast|slow|cold|hot|warm|cool|old|young|new|clean|dark|light|soft|hard|high|low|near|far|bright|dark|rich|poor|cheap|expensive|strong|weak|full|empty|thick|thin|wide|narrow|deep|shallow)\b',
     lambda m: m.group(2) + "er" if len(m.group(2)) <= 5 else "more " + m.group(2)),
]

def _fix_comparatives(text: str, changes: list) -> str:
    result = text
    for pattern, replacement in COMPARATIVE_FIXES:
        new = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        if new != result:
            changes.append("Comparative form corrected")
        result = new
    return result


DOUBLE_NEGATIVES = [
    (r"\b(don't|doesn't|didn't|can't|couldn't|wouldn't|shouldn't|won't|isn't|aren't|wasn't|weren't|haven't|hasn't|hadn't|never|nothing|nobody|no one|nowhere)\b.*?\b(never|nothing|nobody|no one|nowhere|none|neither)\b",
     "Double negative detected"),
]

def _fix_double_negatives(text: str, changes: list) -> str:
    for pattern, desc in DOUBLE_NEGATIVES:
        if re.search(pattern, text, re.IGNORECASE):
            changes.append(desc + " - consider removing one negative")
    return text


QUESTION_FIXES = [
    (r'\b(you|he|she|they|we|it)\s+(is|are|was|were)\s+(going|coming|doing|eating|drinking|working|playing|reading|writing|speaking|listening|watching|studying)\b\s*\?',
     lambda m: f"Is {m.group(1)} {m.group(3)}?" if m.group(1).lower() == "he" or m.group(1).lower() == "she" or m.group(1).lower() == "it" else f"Are {m.group(1)} {m.group(3)}?"),
]

def _fix_question_formation(text: str, changes: list) -> str:
    result = text
    for pattern, replacement in QUESTION_FIXES:
        new = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        if new != result:
            changes.append("Question word order corrected")
            result = new
    return result


GERUND_INFINITIVE = {
    "enjoy to": "enjoy", "enjoy to do": "enjoy doing",
    "suggest to": "suggest", "suggest to do": "suggest doing",
    "recommend to": "recommend", "recommend to do": "recommend doing",
    "avoid to": "avoid", "avoid to do": "avoid doing",
    "consider to": "consider", "consider to do": "consider doing",
    "finish to": "finish", "finish to do": "finish doing",
    "practice to": "practice", "practice to do": "practice doing",
    "mind to": "mind", "mind to do": "mind doing",
    "discuss to": "discuss", "discuss to do": "discuss doing",
    "keep to": "keep", "keep to do": "keep doing",
    "imagine to": "imagine", "imagine to do": "imagine doing",
    "risk to": "risk", "risk to do": "risk doing",
    "admit to": "admit", "admit to do": "admit doing",
    "deny to": "deny", "deny to do": "deny doing",
    "involve to": "involve", "involve to do": "involve doing",
    "miss to": "miss", "miss to do": "miss doing",
    "postpone to": "postpone", "postpone to do": "postpone doing",
    "quit to": "quit", "quit to do": "quit doing",
    "resume to": "resume", "resume to do": "resume doing",
    "resist to": "resist", "resist to do": "resist doing",
    "appreciate to": "appreciate", "appreciate to do": "appreciate doing",
    "delay to": "delay", "delay to do": "delay doing",
}

LIKE_VERBS = ["like", "love", "hate", "prefer", "dislike", "enjoy"]

def _to_gerund(verb: str) -> str:
    if verb.endswith('e') and not verb.endswith('ee') and not verb.endswith('ie'):
        if len(verb) > 2:
            return verb[:-1] + 'ing'
    if verb.endswith('ie'):
        return verb[:-2] + 'ying'
    if len(verb) <= 3 and verb[-1] not in ('w', 'x', 'y'):
        return verb + verb[-1] + 'ing'
    return verb + 'ing'

def _fix_gerund_infinitive(text: str, changes: list) -> str:
    result = text
    for wrong, correct in GERUND_INFINITIVE.items():
        pat = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
        new = pat.sub(correct, result)
        if new != result:
            changes.append(f'"{wrong}" -> "{correct}"')
            result = new

    like_verbs_pattern = r'\b(' + '|'.join(LIKE_VERBS) + r')\s+(\w+)\b'
    def fix_gerund(m):
        verb = m.group(1).lower()
        action = m.group(2).lower()
        action_s = _to_gerund(action)
        if action != action_s and action not in ('to', 'the', 'a', 'an', 'this', 'that', 'my', 'your', 'his', 'her', 'its', 'our', 'their'):
            return f"{m.group(1)} {action_s}"
        return m.group(0)
    new = re.sub(like_verbs_pattern, fix_gerund, result, flags=re.IGNORECASE)
    if new != result:
        changes.append("Verb after like/love/hate -> gerund (-ing)")
    result = new

    return result


POSSESSIVE_FIXES = [
    (r"\b(it's)\s+(\w+)\b", lambda m: f"its {m.group(2)}" if m.group(2) in ("car", "house", "book", "name", "color", "size", "shape", "owner", "cover", "page", "door", "window", "roof", "engine", "screen", "battery", "key", "button") else m.group(0)),
]

def _fix_possessives(text: str, changes: list) -> str:
    result = text
    for pattern, replacement in POSSESSIVE_FIXES:
        new = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        if new != result:
            changes.append("Possessive corrected (its vs it's)")
        result = new
    return result


def _fix_redundancy(text: str, changes: list) -> str:
    result = text
    redundancies = [
        (r'\b(advance|progress|proceed)\s+(forward|ahead)\b', r'\1'),
        (r'\b(revert|return|repeat)\s+(back)\b', r'\1'),
        (r'\b(combine|merge|join|mix)\s+(together)\b', r'\1'),
        (r'\b(refer|mention|cite)\s+(back)\b', r'\1'),
        (r'\b(elevator|escalator)\s+(up|down)\b', r'\1'),
        (r'\b(the\s+)?(reason)\s+(why|is because)\b', r'\1\2 is that'),
        (r'\b(enter|go|come)\s+(into|inside)\b', lambda m: m.group(1) + " " + m.group(2)),
    ]
    for pat, replacement in redundancies:
        new = re.sub(pat, replacement, result, flags=re.IGNORECASE)
        if new != result:
            changes.append("Redundancy removed")
            result = new
    return result


PRONOUN_CASE_FIXES = [
    (r'\b(me|him|her|them|us)\s+(am|is|are|was|were|will|can|could|would|should|have|has|had|do|does|did|go|going|like|love|want|need|have|eat|drink|play|read|write|speak|listen|watch|work|study)\b',
     lambda m: {"me": "I", "him": "he", "her": "she", "them": "they", "us": "we"}.get(m.group(1).lower(), m.group(1)).capitalize() if m.group(1)[0].isupper() else {"me": "I", "him": "he", "her": "she", "them": "they", "us": "we"}.get(m.group(1).lower(), m.group(1)) + " " + m.group(2)),
]

def _fix_pronoun_case(text: str, changes: list) -> str:
    result = text
    for pattern, replacement in PRONOUN_CASE_FIXES:
        new = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        if new != result:
            changes.append("Pronoun case corrected (subject vs object)")
        result = new
    return result