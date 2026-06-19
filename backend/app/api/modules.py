from fastapi import APIRouter, HTTPException
from app.models.learning import Module, ModuleLevel

router = APIRouter()

MODULES = [
    Module(
        id="mod-1", title="Greetings and Introductions",
        description="Learn basic greetings, introductions, and polite expressions",
        level=ModuleLevel.BEGINNER, order=1,
        vocabulary=["hello", "goodbye", "please", "thank you", "nice to meet you",
                     "how are you", "fine", "morning", "afternoon", "evening"],
        phrases=["Hello, how are you?", "Nice to meet you.", "Good morning!",
                 "Thank you very much.", "See you later."],
        grammar_focus="Present simple with 'to be'"
    ),
    Module(
        id="mod-2", title="Daily Routines",
        description="Describe your daily activities and routines",
        level=ModuleLevel.BEGINNER, order=2,
        vocabulary=["wake up", "get dressed", "have breakfast", "go to work",
                     "take a shower", "brush teeth", "go to bed", "usually", "always", "never"],
        phrases=["I wake up at 7 AM.", "She always has breakfast at 8.",
                 "They go to work by bus.", "He never eats lunch at home."],
        grammar_focus="Present simple for habits and routines"
    ),
    Module(
        id="mod-3", title="Food and Restaurants",
        description="Order food, talk about preferences, and restaurant interactions",
        level=ModuleLevel.BEGINNER, order=3,
        vocabulary=["menu", "order", "waiter", "bill", "delicious", "spicy",
                     "sweet", "savory", "appetizer", "main course", "dessert"],
        phrases=["I would like to order the pasta.", "Could I have the menu, please?",
                 "The food is delicious.", "Can I have the bill, please?"],
        grammar_focus="Would like / Could for polite requests"
    ),
    Module(
        id="mod-4", title="Past Experiences",
        description="Talk about past events and experiences using past tenses",
        level=ModuleLevel.INTERMEDIATE, order=4,
        vocabulary=["yesterday", "last week", "ago", "visited", "traveled",
                     "watched", "enjoyed", "learned", "met", "went"],
        phrases=["I went to the beach yesterday.", "She visited Paris last summer.",
                 "They watched a movie last night.", "Have you ever been to London?"],
        grammar_focus="Past simple vs Present perfect"
    ),
    Module(
        id="mod-5", title="Future Plans",
        description="Express future plans, predictions, and intentions",
        level=ModuleLevel.INTERMEDIATE, order=5,
        vocabulary=["will", "going to", "plan to", "hope to", "next week",
                     "tomorrow", "soon", "eventually", "probably", "definitely"],
        phrases=["I am going to travel next month.", "She will call you later.",
                 "They plan to start a business.", "I hope to see you soon."],
        grammar_focus="Will vs Going to for future"
    ),
    Module(
        id="mod-6", title="Travel and Directions",
        description="Ask for and give directions, travel-related conversations",
        level=ModuleLevel.INTERMEDIATE, order=6,
        vocabulary=["straight", "turn left", "turn right", "crosswalk", "traffic light",
                     "roundabout", "destination", "route", "map", "far", "near"],
        phrases=["Excuse me, how do I get to the station?", "Go straight ahead.",
                 "Turn left at the traffic light.", "It is next to the bank."],
        grammar_focus="Imperatives and prepositions of place"
    ),
    Module(
        id="mod-7", title="Opinions and Debates",
        description="Express opinions, agree, disagree, and debate topics",
        level=ModuleLevel.ADVANCED, order=7,
        vocabulary=["in my opinion", "I believe", "I disagree", "on the other hand",
                     "however", "therefore", "consequently", "furthermore", "nevertheless"],
        phrases=["In my opinion, technology improves our lives.",
                 "I disagree with that point because...",
                 "From my perspective, the issue is more complex.",
                 "What are your thoughts on this matter?"],
        grammar_focus="Complex sentences and connectors"
    ),
    Module(
        id="mod-8", title="Business English",
        description="Professional communication, meetings, and negotiations",
        level=ModuleLevel.ADVANCED, order=8,
        vocabulary=["meeting", "deadline", "proposal", "budget", "negotiate",
                     "stakeholder", "agenda", "milestone", "collaborate", "implement"],
        phrases=["I would like to schedule a meeting.", "Let's discuss the proposal.",
                 "We need to meet the deadline.", "I propose we move forward with this plan."],
        grammar_focus="Conditional sentences and modal verbs"
    ),
]

@router.get("/", response_model=list[Module])
async def get_modules():
    return sorted(MODULES, key=lambda m: m.order)

@router.get("/{module_id}", response_model=Module)
async def get_module(module_id: str):
    for module in MODULES:
        if module.id == module_id:
            return module
    raise HTTPException(status_code=404, detail="Module not found")

@router.get("/level/{level}", response_model=list[Module])
async def get_modules_by_level(level: ModuleLevel):
    return [m for m in MODULES if m.level == level]
