import re
from typing import Dict, Any, List
import math
from collections import Counter
from typing import Dict, Any, List
from config import WEIGHTS
from src.parser import parse_document, extract_skills

def clean_text(text: str) -> str:
    """Preprocess text for vectorization."""
    text = re.sub(r'[^a-zA-Z0-9\s\+\#\.]', ' ', text)
    return text.lower()

def _pure_python_tfidf_similarity(text1: str, text2: str) -> float:
    """Pure-Python fallback for cosine similarity using term frequencies."""
    words1 = [w for w in clean_text(text1).split() if len(w) > 2]
    words2 = [w for w in clean_text(text2).split() if len(w) > 2]
    
    if not words1 or not words2:
        return 0.0

    counts1 = Counter(words1)
    counts2 = Counter(words2)
    
    all_words = set(counts1.keys()).union(set(counts2.keys()))
    
    dot_product = 0.0
    norm1 = 0.0
    norm2 = 0.0
    
    for word in all_words:
        c1 = counts1.get(word, 0)
        c2 = counts2.get(word, 0)
        dot_product += c1 * c2
        norm1 += c1 * c1
        norm2 += c2 * c2

    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = dot_product / (math.sqrt(norm1) * math.sqrt(norm2))
    # Document-to-job-description cosine similarity normalization
    # Raw cosine in sparse text documents typically peaks around 0.35-0.40
    scaled_sim = min(100.0, float(similarity) * 150.0)
    return round(scaled_sim, 1)

def compute_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """Compute normalized cosine similarity score (0-100) between resume and job description using TF-IDF."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        clean_resume = clean_text(resume_text)
        clean_jd = clean_text(jd_text)
        
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Normalize sparse document cosine similarity (0.35+ is strong correlation)
        scaled_sim = min(100.0, float(sim) * 150.0)
        return round(scaled_sim, 1)
    except Exception:
        # Fallback to pure python implementation if sklearn is not installed
        return _pure_python_tfidf_similarity(resume_text, jd_text)

def match_resume_to_jd(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """
    Core matching engine:
    Evaluates skill overlaps, TF-IDF semantic relevance, structural strength,
    and returns comprehensive metrics.
    """
    resume_parsed = parse_document(resume_text)
    jd_parsed = parse_document(jd_text)

    resume_skills = set(resume_parsed["skills"])
    jd_skills = set(jd_parsed["skills"])

    matched_skills = sorted(list(resume_skills.intersection(jd_skills)))
    missing_skills = sorted(list(jd_skills.difference(resume_skills)))
    additional_skills = sorted(list(resume_skills.difference(jd_skills)))

    # Skill match score calculation
    if len(jd_skills) > 0:
        skill_score = (len(matched_skills) / len(jd_skills)) * 100.0
    else:
        # If JD has no detectable standard taxonomy skills, rely on content similarity
        skill_score = 70.0

    # TF-IDF Cosine Similarity
    semantic_score = compute_tfidf_similarity(resume_text, jd_text)

    # Completeness of resume structure
    completeness = resume_parsed["completeness_score"]

    # Composite Score Calculation
    overall_score = (
        (skill_score * WEIGHTS["skill_match"]) +
        (semantic_score * WEIGHTS["semantic_similarity"]) +
        (completeness * WEIGHTS["section_completeness"])
    )
    overall_score = round(min(100.0, max(0.0, overall_score)), 1)

    # Match Category / Verdict
    if overall_score >= 75:
        verdict = "Strong Match"
        status_color = "green"
    elif overall_score >= 55:
        verdict = "Moderate Match"
        status_color = "orange"
    else:
        verdict = "Low Match / Needs Improvement"
        status_color = "red"

    return {
        "overall_score": overall_score,
        "verdict": verdict,
        "status_color": status_color,
        "metrics": {
            "skill_score": round(skill_score, 1),
            "semantic_score": round(semantic_score, 1),
            "completeness_score": completeness,
        },
        "skills": {
            "matched": matched_skills,
            "missing": missing_skills,
            "additional": additional_skills,
            "jd_total": len(jd_skills),
            "resume_total": len(resume_skills)
        },
        "resume_meta": {
            "word_count": resume_parsed["word_count"],
            "contact_info": resume_parsed["contact_info"],
            "sections": resume_parsed["sections"]
        },
        "jd_meta": {
            "word_count": jd_parsed["word_count"]
        }
    }
