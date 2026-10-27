import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Scoring Weights
WEIGHTS = {
    "skill_match": 0.50,      # Weight of direct skill match overlap
    "semantic_similarity": 0.35, # Weight of TF-IDF / semantic cosine similarity
    "section_completeness": 0.15 # Weight of structural completeness
}

# Comprehensive Skill Taxonomy for Tech, Data, Cloud, Management & Soft Skills
COMMON_SKILLS = [
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "bash", "shell", "powershell", "html", "css", "sass",
    
    # Frameworks & Libraries
    "react", "react.js", "next.js", "vue", "vue.js", "angular", "node.js", "express", "django", "flask", "fastapi", "spring", "spring boot", ".net", "asp.net", "laravel", "rails", "ruby on rails", "pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "opencv", "spacy", "huggingface", "langchain", "llamaindex",
    
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform", "ansible", "ci/cd", "jenkins", "github actions", "gitlab ci", "helm", "prometheus", "grafana", "linux", "nginx", "apache", "serverless", "lambda",
    
    # Databases & Storage
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "sqlite", "cassandra", "dynamodb", "snowflake", "bigquery", "redshift", "neo4j", "mariadb", "firebase", "supabase",
    
    # Architecture & Practices
    "microservices", "rest api", "restful", "graphql", "grpc", "system design", "agile", "scrum", "kanban", "test-driven development", "tdd", "unit testing", "ci/cd pipelines", "object-oriented programming", "oop", "distributed systems", "clean code",
    
    # Data Science & AI
    "machine learning", "deep learning", "nlp", "natural language processing", "computer vision", "llms", "large language models", "prompt engineering", "genai", "generative ai", "data engineering", "etl", "data warehousing", "data modeling", "feature engineering", "rag", "retrieval augmented generation",
    
    # Soft & Professional Skills
    "leadership", "communication", "problem solving", "critical thinking", "team collaboration", "project management", "mentorship", "stakeholder management", "time management", "analytical skills"
]
