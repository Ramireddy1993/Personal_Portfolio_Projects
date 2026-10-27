import re
from typing import Dict, List, Set, Any
from config import COMMON_SKILLS

EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'(?:(?:\+?\d{1,3}[-.\s*]?)?(?:\(?\d{3}\)?[-.\s*]?)?\d{3}[-.\s*]?\d{4})'
LINKEDIN_REGEX = r'linkedin\.com/in/[a-zA-Z0-9-_]+'
GITHUB_REGEX = r'github\.com/[a-zA-Z0-9-_]+'

SECTION_HEADERS = {
    "summary": ["summary", "professional summary", "about me", "profile", "objective"],
    "experience": ["experience", "work experience", "employment history", "professional experience", "work history"],
    "education": ["education", "academic background", "qualifications", "degrees"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "tools"],
    "projects": ["projects", "personal projects", "academic projects", "key initiatives"],
    "certifications": ["certifications", "licenses", "courses", "certificates"]
}

def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extract candidate contact details like email, phone, links."""
    emails = re.findall(EMAIL_REGEX, text)
    phones = re.findall(PHONE_REGEX, text)
    linkedin = re.findall(LINKEDIN_REGEX, text, re.IGNORECASE)
    github = re.findall(GITHUB_REGEX, text, re.IGNORECASE)

    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "linkedin": linkedin[0] if linkedin else None,
        "github": github[0] if github else None,
    }

def detect_sections(text: str) -> Dict[str, bool]:
    """Check presence of standard resume sections."""
    text_lower = text.lower()
    sections_present = {}
    for section, keywords in SECTION_HEADERS.items():
        found = any(re.search(rf"\b{re.escape(k)}\b", text_lower) for k in keywords)
        sections_present[section] = found
    return sections_present

def extract_skills(text: str, custom_skills: List[str] = None) -> Set[str]:
    """
    Extract technical and professional skills using boundary-safe matching
    against the taxonomy.
    """
    skill_set = set(COMMON_SKILLS)
    if custom_skills:
        skill_set.update(k.lower() for k in custom_skills)

    text_lower = text.lower()
    found_skills = set()

    for skill in skill_set:
        # Word boundary matching (with special consideration for symbols like c++, c#, .net)
        escaped_skill = re.escape(skill)
        # If skill contains non-alphanumeric trailing chars like ++ or #
        pattern = rf"(?<![\w\-]){escaped_skill}(?![\w\-])"
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    return found_skills

def parse_document(text: str) -> Dict[str, Any]:
    """Complete document breakdown into metadata, contact info, sections, and skills."""
    contact = extract_contact_info(text)
    sections = detect_sections(text)
    skills = extract_skills(text)
    words = len(text.split())

    # Section completeness score (0 to 100)
    completeness_score = int((sum(1 for v in sections.values() if v) / len(sections)) * 100)

    return {
        "word_count": words,
        "contact_info": contact,
        "sections": sections,
        "completeness_score": completeness_score,
        "skills": sorted(list(skills)),
        "raw_text": text
    }
