import os
from typing import Dict, Any, Optional
from config import GEMINI_API_KEY, DEFAULT_GEMINI_MODEL

ANALYSIS_PROMPT_TEMPLATE = """You are an expert HR Leader, Hiring Manager, and Technical Recruiter.
Analyze this candidate's resume strictly against the provided job description.

JOB DESCRIPTION:
\"\"\"
{jd_text}
\"\"\"

CANDIDATE RESUME:
\"\"\"
{resume_text}
\"\"\"

CURRENT METRIC OVERVIEW:
- Overall Compatibility Score: {overall_score}%
- Matched Skills: {matched_skills}
- Missing Skills: {missing_skills}

Provide a structured, deeply insightful executive analysis formatted cleanly in Markdown:

### 1. Executive Summary
Brief 2-3 sentence verdict on candidate-role alignment.

### 2. Key Strengths & Differentiators
Highlight 3-4 specific experiences, projects, or capabilities in the resume that directly answer the core requirements of this JD.

### 3. Critical Gaps & Weaknesses
Identify missing requirements, technologies, or experience depth compared to the job description expectations.

### 4. Actionable Tailoring Recommendations
Provide concrete advice on how the candidate can optimize or rephrase their resume for this specific position (e.g. bullet point improvements, metric additions, keywords to highlight).

### 5. Tailored Interview Questions
Suggest 3-4 targeted interview questions the hiring team should ask this candidate to probe their actual depth in the required areas (especially around missing or adjacent skills).
"""

def generate_llm_analysis(
    resume_text: str,
    jd_text: str,
    metrics: Dict[str, Any],
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> str:
    """
    Generate in-depth qualitative evaluation using Gemini AI.
    Gracefully handles missing keys and SDK variations.
    """
    key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not key:
        return (
            "**Gemini AI Analysis not enabled.**\n\n"
            "To unlock AI-powered executive summaries, SWOT analysis, and custom interview questions, "
            "provide a Google Gemini API Key in your `.env` file or in the app sidebar."
        )

    model = model_name or DEFAULT_GEMINI_MODEL

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        jd_text=jd_text[:4000],
        resume_text=resume_text[:4000],
        overall_score=metrics.get("overall_score", "N/A"),
        matched_skills=", ".join(metrics.get("skills", {}).get("matched", [])) or "None detected",
        missing_skills=", ".join(metrics.get("skills", {}).get("missing", [])) or "None detected"
    )

    # Try modern google-genai first
    try:
        from google import genai
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text
    except ImportError:
        pass
    except Exception as e:
        # If modern client fails, fallback to google.generativeai
        err_msg = str(e)
        pass

    # Try legacy google.generativeai
    try:
        import google.generativeai as gai
        gai.configure(api_key=key)
        gm = gai.GenerativeModel(model)
        resp = gm.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"Error contacting Gemini AI: {str(e)}"
