from collections import defaultdict
from typing import List, Tuple, Dict

def score_and_categorize_skills(skills: List[Tuple[str, str, int]]) -> Dict[str, List[Dict]]:
    """
    Given a list of (skill, category, frequency), returns a categorized skill list
    with frequency and relevance score.
    """
    skill_data = defaultdict(lambda: defaultdict(int))
    
    for skill, category, count in skills:
        skill_data[category][skill] += count

    result = {}
    for category, skills_in_cat in skill_data.items():
        result[category] = []
        for skill, freq in sorted(skills_in_cat.items(), key=lambda x: x[1], reverse=True):
            result[category].append({
                "skill": skill,
                "frequency": freq,
                "relevance_score": min(freq * 10, 100)
            })

    return result
