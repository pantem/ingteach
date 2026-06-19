import re

ARTICLES = {"a", "an", "the"}
SUBJECTS_I = {"i"}
SUBJECTS_SINGULAR = {"he", "she", "it", "this", "that", "everyone", "someone", "no one", "everybody", "somebody", "nobody"}
SUBJECTS_PLURAL = {"they", "we", "you", "these", "those", "people", "things"}
VERB_BE = {"am", "is", "are", "was", "were", "be", "been", "being"}
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
    "drink": "drank", "speak": "spoke", "read": "read", "run": "ran",
}

COMMON_MISTAKES = {
    "peoples": "people",
    "childs": "children",
    "childs": "children",
    "moneys": "money",
    "informations": "information",
    "advices": "advice",
    "knowledges": "knowledge",
    "furnitures": "furniture",
    "homeworks": "homework",
    "staffs": "staff",
    "equipments": "equipment",
    "researches": "research",
    "progresses": "progress",
    "more better": "better",
    "more bigger": "bigger",
    "more larger": "larger",
    "most best": "best",
    "most worst": "worst",
    "can could": "could",
    "will would": "would",
    "shall should": "should",
    "may might": "might",
    "must have to": "must",
    "need to to": "need to",
    "want to to": "want to",
    "try to to": "try to",
    "going to to": "going to",
    "have to to": "have to",
}

def correct_sentence(text: str) -> dict:
    if not text or not text.strip():
        return {"original": text, "corrected": text, "changes": [], "has_errors": False}

    original = text.strip()
    corrected = original
    changes = []

    corrected = _fix_article_usage(corrected, changes)
    corrected = _fix_subject_verb_agreement(corrected, changes)
    corrected = _fix_common_mistakes(corrected, changes)
    corrected = _fix_verb_tense(corrected, changes)
    corrected = _fix_preposition_usage(corrected, changes)
    corrected = _fix_word_order(corrected, changes)
    corrected = _fix_capitalization(corrected, changes)
    corrected = _fix_punctuation(corrected, changes)

    return {
        "original": original,
        "corrected": corrected,
        "changes": changes,
        "has_errors": len(changes) > 0,
    }

def _fix_article_usage(text: str, changes: list) -> str:
    result = text

    result = re.sub(r'\ba (a|e|i|o|u)[a-z]*\b', lambda m: _replace_article(m, "an"), result, flags=re.IGNORECASE)
    result = re.sub(r'\ban ([^aeiou])[a-z]*\b', lambda m: _replace_article(m, "a"), result, flags=re.IGNORECASE)

    sing_nouns = re.findall(r'\b(?:a|an|the)\s+(\w+)\b', result.lower())
    for noun in set(sing_nouns):
        if noun.endswith('s') and noun not in {'is', 'has', 'was', 'this', 'his', 'its'}:
            pass

    return result

def _replace_article(m: re.Match, correct: str) -> str:
    word = m.group(0)
    if word[0].isupper():
        return correct.capitalize() + word[1:]
    return correct + word[1:]

def _fix_subject_verb_agreement(text: str, changes: list) -> str:
    result = text

    patterns = [
        (r'\b(I)\s+(is|are|were)\b', r'\1 am', "I + is/are/were -> I am"),
        (r'\b(I)\s+(has)\b', r'\1 have', "I + has -> I have"),
        (r'\b(He|She|It)\s+(are|were)\b', lambda m: m.group(1) + (" is" if m.group(2) == "are" else " was"),
         "he/she/it + are/were -> is/was"),
        (r'\b(He|She|It)\s+(have)\b', lambda m: m.group(1) + " has", "he/she/it + have -> has"),
        (r'\b(They|We|You)\s+(is|was)\b', lambda m: m.group(1) + (" are" if m.group(2) == "is" else " were"),
         "they/we/you + is/was -> are/were"),
        (r'\b(They|We|You)\s+(has)\b', lambda m: m.group(1) + " have", "they/we/you + has -> have"),
    ]

    for pattern, replacement, desc in patterns:
        new = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        if new != result:
            changes.append(desc)
        result = new

    return result

def _fix_common_mistakes(text: str, changes: list) -> str:
    result = text
    for wrong, correct in COMMON_MISTAKES.items():
        pattern = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
        new = pattern.sub(correct, result)
        if new != result:
            changes.append(f'"{wrong}" corregido a "{correct}"')
            result = new
    return result

def _fix_verb_tense(text: str, changes: list) -> str:
    result = text

    result = re.sub(
        r'\b(I|He|She|It|They|We|You)\s+(go)\s+(to)\s+(\w+ed)\b',
        lambda m: f"{m.group(1)} went to {m.group(4)}" if m.group(2) == "go" else m.group(0),
        result, flags=re.IGNORECASE
    )

    result = re.sub(
        r'\b(yesterday|last\s+\w+|ago|in\s+\d{4})\b.*?\b(go|do|have|make|say|get|take|come|see|know|think|give|find|tell|become|leave|feel|put|bring|begin|keep|hold|write|sit|stand|lose|meet|eat|drink|speak|run|buy|wear|choose|break|spend|cut|rise|drive)\b',
        lambda m: _fix_past_tense(m),
        result, flags=re.IGNORECASE
    )

    return result

def _fix_past_tense(m: re.Match) -> str:
    verb = m.group(2).lower()
    if verb in IRREGULAR_PAST:
        past = IRREGULAR_PAST[verb]
        return m.group(0).replace(m.group(2), past, 1)
    if verb.endswith('e'):
        return m.group(0).replace(m.group(2), verb + "d", 1)
    return m.group(0).replace(m.group(2), verb + "ed", 1)

def _fix_preposition_usage(text: str, changes: list) -> str:
    result = text

    def _check_prep(pattern: str, replacement: str, desc: str) -> str:
        nonlocal result
        new = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        if new != result:
            changes.append(desc)
        return new

    result = _check_prep(
        r'\b(interested|good|bad|skilled|involved)\s+in\b',
        r'\1 in', "ok"
    )

    return result

def _fix_word_order(text: str, changes: list) -> str:
    result = text

    result = re.sub(
        r'\balways\s+(am|is|are|was|were)\b',
        lambda m: m.group(1) + " always",
        result, flags=re.IGNORECASE
    )

    result = re.sub(
        r'\b(never|always|often|sometimes|usually|rarely|seldom)\s+(am|is|are|was|were)\b',
        lambda m: m.group(2) + " " + m.group(1),
        result, flags=re.IGNORECASE
    )

    return result

def _fix_capitalization(text: str, changes: list) -> str:
    result = text

    new = re.sub(r'\bi\b', 'I', result)
    if new != result:
        changes.append('"i" capitalizado a "I"')
    result = new

    if result and result[0].islower():
        result = result[0].upper() + result[1:]
        changes.append("Primera letra capitalizada")

    return result

def _fix_punctuation(text: str, changes: list) -> str:
    result = text.rstrip()
    if result and result[-1] not in ('.', '!', '?', ';', ':'):
        result += '.'
        changes.append("Punto final agregado")
    return result
