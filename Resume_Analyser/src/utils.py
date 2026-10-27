import json
from typing import Dict, Any

def generate_markdown_report(result: Dict[str, Any], candidate_name: str = "Candidate", ai_feedback: str = "") -> str:
    """Generate a clean, exportable Markdown analysis report."""
    metrics = result["metrics"]
    skills = result["skills"]
    contact = result["resume_meta"]["contact_info"]

    matched_str = ", ".join(f"`{s}`" for s in skills["matched"]) if skills["matched"] else "_None_"
    missing_str = ", ".join(f"`{s}`" for s in skills["missing"]) if skills["missing"] else "_None_"
    additional_str = ", ".join(f"`{s}`" for s in skills["additional"][:15]) if skills["additional"] else "_None_"

    report = f"""# Resume Analysis Report: {candidate_name}

## 📊 Executive Score Overview
- **Overall Compatibility Score:** **{result['overall_score']}%** ({result['verdict']})
- **Skill Match Alignment:** {metrics['skill_score']}%
- **Semantic / Content Similarity:** {metrics['semantic_score']}%
- **Resume Section Completeness:** {metrics['completeness_score']}%

---

## 🔍 Candidate Profile
- **Email:** {contact.get('email') or 'Not specified'}
- **Phone:** {contact.get('phone') or 'Not specified'}
- **LinkedIn:** {contact.get('linkedin') or 'Not specified'}
- **GitHub:** {contact.get('github') or 'Not specified'}
- **Word Count:** {result['resume_meta']['word_count']} words

---

## 🛠 Skills Gap Analysis
### ✅ Matched Skills ({len(skills['matched'])})
{matched_str}

### ⚠️ Missing / Required Skills ({len(skills['missing'])})
{missing_str}

### 💡 Additional Candidate Skills ({len(skills['additional'])})
{additional_str}

---

## 📑 Resume Structure Checklist
"""
    for section, present in result["resume_meta"]["sections"].items():
        icon = "✅" if present else "❌"
        report += f"- {icon} **{section.capitalize()}**\n"

    if ai_feedback:
        report += f"\n---\n\n## 🤖 AI Deep Evaluation\n\n{ai_feedback}\n"

    return report
