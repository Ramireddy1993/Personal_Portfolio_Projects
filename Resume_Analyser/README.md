# 📄 Resume_Analyser

An AI-powered, production-ready Resume Analysis & Candidate Screening platform that evaluates resumes against job descriptions using Natural Language Processing (NLP), skill gap identification, TF-IDF semantic cosine similarity, and Google Gemini AI.

---

## 🚀 Key Features

- **Multi-Format Document Parsing**: Ingests resumes and job descriptions from **PDF**, **DOCX**, and **TXT** files.
- **Skill Extraction & Gap Analysis**:
  - Automatically identifies matching required skills.
  - Highlights missing qualifications/critical gaps.
  - Categorizes candidate's additional strengths.
- **Hybrid Scoring Engine**:
  - **Skill Alignment Score (50%)**: Exact & fuzzy keyword taxonomy overlap.
  - **Semantic Cosine Similarity (35%)**: TF-IDF vectorization with n-grams.
  - **Structure Completeness (15%)**: ATS section detection (Experience, Education, Skills, Projects, Contact info).
- **Interactive Streamlit Web Dashboard**:
  - **Single Resume Deep Dive**: Score gauges, interactive skill tags, and exportable reports.
  - **Batch Resume Screening & Ranking**: Upload multiple resumes simultaneously and rank candidates in a leader table with CSV export.
- **AI-Powered Deep Review (Optional Gemini Integration)**:
  - Executive hiring recommendation.
  - SWOT breakdown (Strengths, Weaknesses, Opportunities).
  - Actionable resume tailoring suggestions.
  - Tailored interview questions probing candidate gap areas.
- **Full CLI Support**: Fast terminal workflow for single or batch analysis.

---

## 📁 Project Architecture

```
Resume_Analyser/
├── app.py                  # Streamlit interactive web application
├── cli.py                  # Terminal CLI interface
├── config.py               # Weights, settings, and skills taxonomy
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── sample_data/
│   ├── sample_resume.txt   # Ready-to-test sample resume
│   └── sample_jd.txt       # Ready-to-test sample job description
├── src/
│   ├── __init__.py
│   ├── extractors.py       # PDF, DOCX, TXT document loaders
│   ├── parser.py           # Contact info, section, and skill parsing
│   ├── matcher.py          # TF-IDF, skill comparison, and composite scoring
│   ├── llm_analyzer.py     # Gemini AI prompt integration
│   └── utils.py            # Report generation and export utilities
└── tests/
    └── test_analyzer.py    # Automated test suite
```

---

## 🛠 Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Navigate to Project Directory
```powershell
cd C:\Users\arami\.gemini\antigravity\scratch\Resume_Analyser
```

### 3. Create a Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. (Optional) Configure Gemini AI
For AI-generated SWOT insights and tailored interview questions:
1. Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Open `.env` and add your [Google AI Studio Gemini API Key](https://aistudio.google.com/):
   ```ini
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
*(Note: Core skill matching and TF-IDF similarity function 100% offline without an API key).*

---

## 🖥 Usage

### A. Launching the Web Application
Run via Python module (recommended):
```powershell
cd C:\Users\arami\.gemini\antigravity\scratch\Resume_Analyser
python -m streamlit run app.py
```
Or double-click `run_app.bat` in the project directory.

Open your browser at `http://localhost:8501`. You can:
1. Choose between **Single Resume Deep Dive** or **Batch Resumes Screening**.
2. Upload your own resume and JD or test immediately with the built-in sample data!
3. Download the full evaluation as a Markdown report or CSV ranking.

### B. Command-Line Interface (CLI)

- **Test immediately with built-in sample data:**
  ```powershell
  python cli.py --sample
  ```

- **Analyze your custom files:**
  ```powershell
  python cli.py --resume path/to/resume.pdf --jd path/to/jd.txt
  ```

- **Export report to Markdown:**
  ```powershell
  python cli.py --resume resume.pdf --jd jd.txt --export analysis_report.md
  ```

- **Enable Gemini AI Qualitative Insights:**
  ```powershell
  python cli.py --sample --ai
  ```

---

## 🧪 Running Unit Tests
To verify all parsers and matching algorithms:
```powershell
python -m unittest tests/test_analyzer.py
```
