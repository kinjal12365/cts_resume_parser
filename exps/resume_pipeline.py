from typing import Dict, Callable, List, Tuple, Optional
from contact_extractor import extract_contact_info
from skill_scorer import score_and_categorize_skills

def process_resume(
    text: str,
    extract_experience: Callable[[str], Optional[str]],
    generate_candidate_id: Callable[[str], str],
    extract_skills_with_regex: Callable[[str], List[Tuple[str, str, int]]]
) -> Dict:
    """
    Process a resume and extract structured candidate information.
    """
    contact = extract_contact_info(text)
    experience = extract_experience(text)
    candidate_id = generate_candidate_id(contact["name"])

    print("   → Extracting skills...")
    skills = extract_skills_with_regex(text)
    categories = score_and_categorize_skills(skills)
    total_skills = sum(len(v) for v in categories.values())
    total_mentions = sum(s["frequency"] for v in categories.values() for s in v)

    return {
        "candidate_id": candidate_id,
        "candidate_info": {
            "name": contact["name"],
            "email": contact["email"],
            "phone": contact["phone"],
            "experience": experience or "Not found"
        },
        "skills_summary": {
            "total_unique_skills": total_skills,
            "total_skill_mentions": total_mentions,
            "categories_found": len(categories)
        },
        "skills_by_category": categories,
    }
