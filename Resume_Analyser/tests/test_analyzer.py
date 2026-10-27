import unittest
from pathlib import Path
from src.extractors import extract_text_from_txt
from src.parser import parse_document, extract_skills, extract_contact_info
from src.matcher import match_resume_to_jd
from config import BASE_DIR

class TestResumeAnalyser(unittest.TestCase):
    def setUp(self):
        sample_dir = BASE_DIR / "sample_data"
        self.resume_text = extract_text_from_txt(sample_dir / "sample_resume.txt")
        self.jd_text = extract_text_from_txt(sample_dir / "sample_jd.txt")

    def test_contact_extraction(self):
        contact = extract_contact_info(self.resume_text)
        self.assertEqual(contact["email"], "alex.mercer@example.com")
        self.assertIn("alexmercer-dev", contact["linkedin"])
        self.assertIn("alexmercer-code", contact["github"])

    def test_skills_extraction(self):
        skills = extract_skills(self.resume_text)
        self.assertIn("python", skills)
        self.assertIn("react", skills)
        self.assertIn("docker", skills)
        self.assertIn("fastapi", skills)

    def test_matcher_scores(self):
        result = match_resume_to_jd(self.resume_text, self.jd_text)
        self.assertGreater(result["overall_score"], 50.0)
        self.assertIn("python", result["skills"]["matched"])
        self.assertIn("react", result["skills"]["matched"])
        self.assertIsInstance(result["metrics"]["semantic_score"], float)

if __name__ == "__main__":
    unittest.main()
