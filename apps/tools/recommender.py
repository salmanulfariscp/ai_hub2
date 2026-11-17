"""
Rules-based recommendation engine (no paid AI API needed).

Each tool gets points based on how well it matches the quiz answers.
The logic is deliberately simple so you can read and change it:

    +6  tool's category matches the user's main goal
    +3  tool's category is the category the user picked
    +2  tool's category suits the user's profession
    +2  tool has a free plan and the user prefers free / has a small budget
    +1  per interest keyword found in the tool's text (max 3)
    +1  tool is featured by the admins
    -   tools WITHOUT a free plan are removed when the budget is "free only"
"""

# (value, label, icon, matching category slugs)
PURPOSES = [
    ("chat", "Chat, ask questions & brainstorm", "bi-chat-dots", ["ai-chatbots"]),
    ("write", "Write or improve content", "bi-pencil-square", ["writing-content"]),
    ("code", "Write or debug code", "bi-code-slash", ["coding-assistants"]),
    ("image", "Create images or designs", "bi-image", ["image-generation"]),
    ("video", "Create or edit videos", "bi-camera-video", ["video-generation"]),
    ("audio", "Voice, music or transcription", "bi-music-note-beamed", ["audio-music"]),
    ("research", "Research or study", "bi-journal-text", ["research-education"]),
    ("work", "Get everyday work done faster", "bi-lightning-charge", ["productivity"]),
    ("business", "Marketing or business tasks", "bi-briefcase", ["business-marketing"]),
]

# (value, label, icon, category slugs that suit this profession)
PROFESSIONS = [
    ("student", "Student", "bi-mortarboard", ["research-education", "writing-content"]),
    ("developer", "Developer", "bi-terminal", ["coding-assistants"]),
    ("designer", "Designer or creator", "bi-palette", ["image-generation", "video-generation"]),
    ("writer", "Writer or editor", "bi-feather", ["writing-content"]),
    ("marketer", "Marketer", "bi-megaphone", ["business-marketing", "writing-content"]),
    ("owner", "Business owner", "bi-shop", ["business-marketing", "productivity"]),
    ("researcher", "Researcher", "bi-search", ["research-education"]),
    ("other", "Something else", "bi-person", []),
]

BUDGETS = [
    ("free", "Free only", "bi-gift"),
    ("low", "Small budget (a free plan is ideal)", "bi-piggy-bank"),
    ("flexible", "Flexible - quality matters most", "bi-wallet2"),
]

PURPOSE_LABELS = {value: label for value, label, _icon, _cats in PURPOSES}
PURPOSE_CATEGORIES = {value: cats for value, _label, _icon, cats in PURPOSES}
PROFESSION_CATEGORIES = {value: cats for value, _label, _icon, cats in PROFESSIONS}


def _keywords(text):
    return [word for word in (text or "").lower().replace(",", " ").split() if len(word) > 2]


def score_tool(tool, answers):
    """Return (score, reasons) for one tool. A score of 0 means 'do not show'."""
    score, reasons = 0, []
    category_slug = tool.category.slug
    has_free_plan = tool.pricing_model in ("free", "freemium")

    # Budget "free only" removes tools without a free plan.
    if answers.get("budget") == "free" and not has_free_plan:
        return 0, []

    # --- relevance: how well does the tool fit what the user wants to do?
    relevance = 0
    purpose = answers.get("purpose")
    if category_slug in PURPOSE_CATEGORIES.get(purpose, []):
        relevance += 6
        reasons.append("Built for your goal: " + PURPOSE_LABELS[purpose].lower())
    if answers.get("category") and category_slug == answers["category"]:
        relevance += 3
        reasons.append("In your preferred category: " + tool.category.name)
    if category_slug in PROFESSION_CATEGORIES.get(answers.get("profession"), []):
        relevance += 2
        reasons.append("Suits your profession")

    text = " ".join([tool.name, tool.tagline, tool.description, tool.use_cases]).lower()
    hits = [word for word in _keywords(answers.get("interests")) if word in text]
    if hits:
        relevance += min(len(hits), 3)
        reasons.append("Matches your interests: " + ", ".join(hits[:3]))

    if relevance == 0:
        return 0, []  # nothing connects this tool to the user's needs
    score += relevance

    # --- bonuses (only apply to tools that are already relevant)
    wants_free = answers.get("prefer_free") == "yes" or answers.get("budget") in ("free", "low")
    if has_free_plan and wants_free:
        score += 2
        reasons.append("Free to use" if tool.pricing_model == "free" else "Has a free plan")
    if getattr(tool, "is_featured", False):
        score += 1
    return score, reasons


def recommend_tools(tools, answers, limit=6):
    """Rank tools for the given answers. Returns a list of {'tool', 'score', 'reasons'} dicts."""
    ranked = []
    for tool in tools:
        score, reasons = score_tool(tool, answers)
        if score > 0:
            ranked.append({"tool": tool, "score": score, "reasons": reasons})
    ranked.sort(key=lambda item: (-item["score"], item["tool"].name.lower()))
    return ranked[:limit]
