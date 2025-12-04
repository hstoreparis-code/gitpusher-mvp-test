import os


def file_exists(path: str) -> bool:
    return os.path.exists(path)


def compute_ai_visibility_score():
    score = 0

    # Base: AEO structure
    if file_exists("frontend/public/ai/indexers/ai-indexers.json"):
        score += 20
    if file_exists("frontend/public/ai/indexers/ai-80-indexers.json"):
        score += 15
    if file_exists("frontend/public/ai/knowledge/intent-map.json"):
        score += 10
    if file_exists("frontend/public/ai/knowledge/priority-map.json"):
        score += 15
    if file_exists("frontend/public/ai/knowledge/tool-catalog.json"):
        score += 10
    if file_exists("frontend/public/ai/agents/toolpack.json"):
        score += 15
    if file_exists("frontend/public/ai/agents/openai-tools.json"):
        score += 10

    # Cap at 100
    return min(100, score)
