import os
import streamlit as st
from pathlib import Path
import pandas as pd

from src.extractors import extract_text
from src.matcher import match_resume_to_jd
from src.llm_analyzer import generate_llm_analysis
from src.utils import generate_markdown_report
from config import BASE_DIR, GEMINI_API_KEY, DEFAULT_GEMINI_MODEL

st.set_page_config(
    page_title="Resume Analyser AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    .skill-tag-match {
        display: inline-block;
        background-color: #d1e7dd;
        color: #0f5132;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 15px;
        font-weight: 500;
        font-size: 0.88rem;
    }
    .skill-tag-missing {
        display: inline-block;
        background-color: #f8d7da;
        color: #842029;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 15px;
        font-weight: 500;
        font-size: 0.88rem;
    }
    .skill-tag-extra {
        display: inline-block;
        background-color: #cfe2ff;
        color: #084298;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 15px;
        font-weight: 500;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper to load sample files
SAMPLE_DIR = BASE_DIR / "sample_data"

def load_sample_file(filename: str) -> str:
    path = SAMPLE_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    return ""

# Sidebar: Configuration & Job Description
with st.sidebar:
    st.header("🎯 Job Description Setup")
    
    jd_input_mode = st.radio("Provide Job Description via:", ["Paste Text", "Upload File", "Use Sample JD"])
    
    jd_text = ""
    if jd_input_mode == "Paste Text":
        jd_text = st.text_area("Job Description Content", height=220, placeholder="Paste the job requirements, responsibilities, and required skills here...")
    elif jd_input_mode == "Upload File":
        jd_file = st.file_uploader("Upload JD (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"], key="jd_file")
        if jd_file:
            jd_text = extract_text(jd_file, jd_file.name)
            st.success(f"Loaded {jd_file.name}")
    else:
        sample_jd_content = load_sample_file("sample_jd.txt")
        jd_text = st.text_area("Sample Job Description", value=sample_jd_content, height=220)

    st.markdown("---")
    st.header("🤖 AI Settings (Optional)")
    user_api_key = st.text_input("Gemini API Key", value=GEMINI_API_KEY, type="password", help="Needed for SWOT analysis, tailoring recommendations, and custom interview questions.")
    model_choice = st.selectbox("Gemini Model", ["gemini-3.8-flash", "gemini-2.5-pro", "gemini-2.5-flash"], index=0)
    
    st.info("💡 Offline mode (skill matching & TF-IDF similarity) works 100% without an API key!")

# Main App Body
st.title("📄 AI Resume Analyser & Matcher")
st.caption("Intelligently evaluate candidate resumes against target job descriptions using NLP, skill gap discovery, and Gemini AI insights.")

mode = st.radio("Choose Analysis Mode:", ["Single Resume Deep Dive", "Batch Resumes Screening"], horizontal=True)

if mode == "Single Resume Deep Dive":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Candidate Resume")
        resume_source = st.radio("Resume Source:", ["Upload Resume File", "Use Sample Resume"], horizontal=True)
        resume_text = ""
        resume_name = "Candidate Resume"
        
        if resume_source == "Upload Resume File":
            resume_file = st.file_uploader("Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
            if resume_file:
                resume_text = extract_text(resume_file, resume_file.name)
                resume_name = resume_file.name
                st.success(f"Loaded: {resume_file.name} ({len(resume_text.split())} words)")
        else:
            resume_text = load_sample_file("sample_resume.txt")
            resume_name = "Sample_Candidate_Resume.txt"
            st.info("Loaded pre-configured Sample Full-Stack / ML Engineer Resume.")
            with st.expander("Preview Resume Text"):
                st.text(resume_text[:1000] + "\n...")

    with col2:
        st.subheader("2. Job Description Summary")
        if jd_text:
            st.success(f"Job Description Ready ({len(jd_text.split())} words)")
            with st.expander("Preview Job Description"):
                st.text(jd_text[:1000] + "\n...")
        else:
            st.warning("Please provide a Job Description in the sidebar.")

    st.markdown("---")
    
    if st.button("🚀 Analyze Match", type="primary", use_container_width=True):
        if not jd_text.strip():
            st.error("Please provide a Job Description in the left sidebar.")
        elif not resume_text.strip():
            st.error("Please provide or upload a Resume to analyze.")
        else:
            with st.spinner("Analyzing resume against job description..."):
                analysis = match_resume_to_jd(resume_text, jd_text)
                st.session_state["analysis_result"] = analysis
                st.session_state["resume_text"] = resume_text
                st.session_state["resume_name"] = resume_name
                st.session_state["jd_text"] = jd_text

    # Show results if available
    if "analysis_result" in st.session_state and st.session_state.get("resume_text") == resume_text:
        res = st.session_state["analysis_result"]
        metrics = res["metrics"]
        skills = res["skills"]
        contact = res["resume_meta"]["contact_info"]

        # Score Overview Banner
        st.markdown(f"### Results for `{st.session_state['resume_name']}`")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Overall Match Score", f"{res['overall_score']}%", delta=res["verdict"])
        with m_col2:
            st.metric("Skill Alignment", f"{metrics['skill_score']}%", f"{len(skills['matched'])}/{skills['jd_total']} skills")
        with m_col3:
            st.metric("Content Similarity", f"{metrics['semantic_score']}%", "TF-IDF Cosine")
        with m_col4:
            st.metric("Structure Completeness", f"{metrics['completeness_score']}%", "Standard Sections")

        # Tabs for detailed insights
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Match Overview",
            "🛠 Skills Gap Analysis",
            "📑 Resume Quality & Sections",
            "🤖 AI Executive Report",
            "📥 Export Report"
        ])

        with tab1:
            st.subheader("Match Breakdown")
            c1, c2 = st.columns([1, 1])
            with c1:
                st.write("**Candidate Contact Detected:**")
                st.write(f"- 📧 **Email:** {contact.get('email') or 'Not found'}")
                st.write(f"- 📱 **Phone:** {contact.get('phone') or 'Not found'}")
                st.write(f"- 💼 **LinkedIn:** {contact.get('linkedin') or 'Not found'}")
                st.write(f"- 💻 **GitHub:** {contact.get('github') or 'Not found'}")
            with c2:
                st.write("**Quick Insights:**")
                st.write(f"- **Matched Skills:** {len(skills['matched'])} skills align with JD requirements.")
                st.write(f"- **Missing Skills:** {len(skills['missing'])} required skills not detected in resume.")
                st.write(f"- **Resume Length:** {res['resume_meta']['word_count']} words.")

        with tab2:
            st.subheader("Skills Comparison")
            
            st.write(f"#### ✅ Matched Skills ({len(skills['matched'])})")
            if skills["matched"]:
                html_matched = "".join(f"<span class='skill-tag-match'>✓ {s}</span>" for s in skills["matched"])
                st.markdown(html_matched, unsafe_allow_html=True)
            else:
                st.warning("No overlapping skills found based on current taxonomy.")

            st.write(f"#### ⚠️ Missing / Required Skills ({len(skills['missing'])})")
            if skills["missing"]:
                html_missing = "".join(f"<span class='skill-tag-missing'>✕ {s}</span>" for s in skills["missing"])
                st.markdown(html_missing, unsafe_allow_html=True)
            else:
                st.success("Great! No critical required skills missing from the JD.")

            st.write(f"#### 💡 Additional Candidate Skills ({len(skills['additional'])})")
            if skills["additional"]:
                html_extra = "".join(f"<span class='skill-tag-extra'>+ {s}</span>" for s in skills["additional"][:20])
                st.markdown(html_extra, unsafe_allow_html=True)
            else:
                st.write("No additional specialized skills detected.")

        with tab3:
            st.subheader("Resume Structure Evaluation")
            sec_cols = st.columns(3)
            sections = res["resume_meta"]["sections"]
            for i, (sec, present) in enumerate(sections.items()):
                with sec_cols[i % 3]:
                    status = "✅ Present" if present else "❌ Missing"
                    st.write(f"**{sec.capitalize()} Section:** {status}")
            
            st.write("---")
            st.write("**Tips for Structural Optimization:**")
            st.write("- Ensure key metrics and quantifiable outcomes are highlighted in your experience bullets.")
            st.write("- Maintain clean, single-column formatting for standard ATS parser compatibility.")

        with tab4:
            st.subheader("🤖 AI Qualitative Assessment (Powered by Gemini)")
            if st.button("Generate AI SWOT & Tailoring Recommendations", type="secondary"):
                with st.spinner("Calling Gemini AI to conduct deep qualitative review..."):
                    ai_report = generate_llm_analysis(
                        resume_text=st.session_state["resume_text"],
                        jd_text=st.session_state["jd_text"],
                        metrics=res,
                        api_key=user_api_key,
                        model_name=model_choice
                    )
                    st.session_state["ai_report"] = ai_report

            if "ai_report" in st.session_state:
                st.markdown(st.session_state["ai_report"])

        with tab5:
            st.subheader("📥 Export Analysis Report")
            ai_rep = st.session_state.get("ai_report", "")
            markdown_content = generate_markdown_report(res, candidate_name=st.session_state['resume_name'], ai_feedback=ai_rep)
            st.download_button(
                label="📄 Download Report as Markdown (.md)",
                data=markdown_content,
                file_name=f"analysis_{st.session_state['resume_name']}.md",
                mime="text/markdown"
            )
            with st.expander("View Raw Markdown"):
                st.code(markdown_content, language="markdown")

else:
    # Batch Resume Screening
    st.subheader("📊 Batch Resume Screening & Ranking")
    st.write("Upload multiple candidate resumes to rank them side-by-side against the Job Description.")

    if not jd_text.strip():
        st.warning("Please provide a Job Description in the left sidebar first.")
    else:
        uploaded_resumes = st.file_uploader(
            "Upload Multiple Resumes (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )

        if uploaded_resumes and st.button("🏆 Screen & Rank Candidates", type="primary"):
            results_list = []
            progress_bar = st.progress(0)
            
            for idx, r_file in enumerate(uploaded_resumes):
                try:
                    text = extract_text(r_file, r_file.name)
                    res = match_resume_to_jd(text, jd_text)
                    results_list.append({
                        "Candidate / File": r_file.name,
                        "Overall Score (%)": res["overall_score"],
                        "Verdict": res["verdict"],
                        "Skill Match (%)": res["metrics"]["skill_score"],
                        "Semantic Score (%)": res["metrics"]["semantic_score"],
                        "Matched Skills": ", ".join(res["skills"]["matched"][:6]),
                        "Missing Skills Count": len(res["skills"]["missing"]),
                        "Email": res["resume_meta"]["contact_info"]["email"] or "N/A"
                    })
                except Exception as e:
                    results_list.append({
                        "Candidate / File": r_file.name,
                        "Overall Score (%)": 0.0,
                        "Verdict": f"Error: {str(e)}",
                        "Skill Match (%)": 0.0,
                        "Semantic Score (%)": 0.0,
                        "Matched Skills": "",
                        "Missing Skills Count": 0,
                        "Email": "N/A"
                    })
                progress_bar.progress((idx + 1) / len(uploaded_resumes))

            df = pd.DataFrame(results_list)
            df = df.sort_values(by="Overall Score (%)", ascending=False).reset_index(drop=True)
            df.index += 1  # 1-based ranking

            st.success(f"Successfully evaluated and ranked {len(uploaded_resumes)} candidates!")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv().encode('utf-8')
            st.download_button(
                "📥 Download Rankings as CSV",
                data=csv,
                file_name="candidate_rankings.csv",
                mime="text/csv"
            )
