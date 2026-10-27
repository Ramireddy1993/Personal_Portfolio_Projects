import argparse
import sys
from pathlib import Path
from src.extractors import extract_text
from src.matcher import match_resume_to_jd
from src.llm_analyzer import generate_llm_analysis
from src.utils import generate_markdown_report
from config import BASE_DIR

def run_cli():
    parser = argparse.ArgumentParser(
        description="Resume Analyser CLI - Evaluate resumes against job descriptions."
    )
    parser.add_argument("--resume", "-r", type=str, help="Path to resume file (PDF, DOCX, TXT)")
    parser.add_argument("--jd", "-j", type=str, help="Path to job description file (PDF, DOCX, TXT)")
    parser.add_argument("--sample", action="store_true", help="Run analysis using built-in sample data")
    parser.add_argument("--ai", action="store_true", help="Run Gemini AI qualitative analysis (requires GEMINI_API_KEY)")
    parser.add_argument("--export", "-e", type=str, help="Path to export report markdown file")

    args = parser.parse_args()

    sample_dir = BASE_DIR / "sample_data"

    if args.sample:
        resume_path = sample_dir / "sample_resume.txt"
        jd_path = sample_dir / "sample_jd.txt"
        print("[*] Running with built-in sample data...\n")
    else:
        if not args.resume or not args.jd:
            print("Error: Please provide both --resume and --jd paths, or use --sample.")
            parser.print_help()
            sys.exit(1)
        resume_path = Path(args.resume)
        jd_path = Path(args.jd)

    try:
        resume_text = extract_text(resume_path)
        jd_text = extract_text(jd_path)
    except Exception as e:
        print(f"Error reading files: {e}")
        sys.exit(1)

    print("==================================================")
    print("           RESUME ANALYSER REPORT                 ")
    print("==================================================")

    res = match_resume_to_jd(resume_text, jd_text)
    metrics = res["metrics"]
    skills = res["skills"]
    contact = res["resume_meta"]["contact_info"]

    print(f"\n[+] Overall Match Score: {res['overall_score']}% ({res['verdict']})")
    print(f"[+] Skill Match Score:   {metrics['skill_score']}%")
    print(f"[+] Semantic Similarity: {metrics['semantic_score']}%")
    print(f"[+] Structure Score:     {metrics['completeness_score']}%\n")

    print("--- Candidate Info ---")
    print(f"Email:    {contact.get('email') or 'N/A'}")
    print(f"Phone:    {contact.get('phone') or 'N/A'}")
    print(f"LinkedIn: {contact.get('linkedin') or 'N/A'}")
    print(f"GitHub:   {contact.get('github') or 'N/A'}")

    print("\n--- Skills Gap Analysis ---")
    print(f"Matched Skills ({len(skills['matched'])}):")
    print("  " + (", ".join(skills['matched']) if skills['matched'] else "None"))
    
    print(f"\nMissing Skills ({len(skills['missing'])}):")
    print("  " + (", ".join(skills['missing']) if skills['missing'] else "None"))

    print(f"\nAdditional Skills ({len(skills['additional'])}):")
    print("  " + (", ".join(skills['additional'][:10]) if skills['additional'] else "None"))

    ai_feedback = ""
    if args.ai:
        print("\n--- Generating Gemini AI Analysis ---")
        ai_feedback = generate_llm_analysis(resume_text, jd_text, res)
        print(ai_feedback)

    if args.export:
        report_md = generate_markdown_report(res, candidate_name=resume_path.name, ai_feedback=ai_feedback)
        export_path = Path(args.export)
        export_path.write_text(report_md, encoding="utf-8")
        print(f"\n[OK] Analysis report saved to: {export_path.resolve()}")

    print("\n==================================================")

if __name__ == "__main__":
    run_cli()
